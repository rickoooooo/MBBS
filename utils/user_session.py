from contexts.context import Context
from contexts.menu import Menu
from utils.session_db import session_db
from utils.config import config
from utils.user_db import UserDB
from utils.message import Message
from contexts.message_pager import MessagePager
from meshtastic import mesh_pb2
from threading import Timer

'''
This class is the main class for each user once they are logged in.
The current_context is the object that displays an interface to the user and receives and responds to user input. 
This can be a menu, program, etc. Review contexts/context.py for details or review some example contexts to see 
possible implementations (cmd_echo.py, cmd_sysinfo.py, etc)
'''

class UserSession():
    '''
    __init__() is called only when the session is created.
    Sets up default param values and sets the default context
    '''
    def __init__(self, user_id: int, interface: "CommInterface", packet: dict):
        self.user_id = user_id
        self.username = ""
        self.interface = interface      # Hardware interface object. Could be a mesh interface on the backend or TCP, or anything really.
        self.authenticated = False      # Authentication flag for this session.
        self.current_context = None     # Instance of a Context object that is currently handling user input and sending messages to the user.
        self.context_history = []       # List containing all previous context objects in order. revert_context() will delete items from the end of the list.
        self.user_db = UserDB()         # Object to interact with the user database for authentication purposes.
        
        self.timeout_seconds = config["sessions"]["timeout"] # How many seconds until the session times out from inactivity
        self.session_timer = Timer(self.timeout_seconds, self.timeout)    # Timer object to destroy session if timeout occurs
        self.session_timer.start()

        bbs_menu_context = Menu(self, config["menus"][0])   # Set the default context to the first menu defined in config.toml.
        self.change_context(bbs_menu_context)               # Change to the default context

    '''
    send_message() can be used to send a message to the user who owns this session.
    The message parameter is a Message() object.
    '''
    def send_message(self, message: Message) -> None:
        # Check if message size is too big to fit in a mesh packet
        if message.get_message_size() > mesh_pb2.Constants.DATA_PAYLOAD_LEN:
            # If so, use MessagePager() context to paginate the output and let the user view it in chunks.
            message.footer = None
            bbs_message_pager = MessagePager(self, message)
            self.change_context(bbs_message_pager)
        else:
            # If not, just send the message as is.
            text = message.get_text()
            self.send_text_part(text)

    '''
    send_one_page() will send only one page worth of text from a message, even if the message is too long to fit in a page
    '''
    def send_one_page(self, message: Message) -> None:
        new_message = message.copy()

        # Check if message size is too big to fit in a mesh packet
        message_size = message.get_message_size()

        # Not sure why, but I have to make packets less than the DATA_PAYLOAD_LEN in order for them to send properly. So I subtract 10.
        if message_size > (mesh_pb2.Constants.DATA_PAYLOAD_LEN - 10):
            #size_delta = message_size - (mesh_pb2.Constants.DATA_PAYLOAD_LEN + 4 + 10)
            #size_delta = size_delta * -1
            new_message.body = ""
            chunk_size = 0
            ellipses_size = 4
            chunk_size = (mesh_pb2.Constants.DATA_PAYLOAD_LEN - ellipses_size - 10)
            chunk_size = chunk_size - new_message.get_message_size() - 1
            new_message.body = message.body[0:chunk_size]
            new_message.body += " ..."

        text = new_message.get_text()
        self.send_text(text)

    '''
    send_text() can be used to send a message to the user based on a basic text string.
    Primarily used by self.send_message() but could be used directly by other Context objects.
    It will use MessagePager() to paginate output if the output is too long to fit in a mesh packet.
    '''
    def send_text(self, text: str) -> None:
        if not text:
            return

        if len(text) > mesh_pb2.Constants.DATA_PAYLOAD_LEN:
            raise(ValueError(f"Message too long. Must be shorter than mesh_pb2.Constants.DATA_PAYLOAD_LEN ({mesh_pb2.Constants.DATA_PAYLOAD_LEN})."))
        else:
            self.send_text_part(text)

    '''
    send_text_part() sends a basic text string to the user with no pagination.
    It is intended to be used after the message length is checked and pagination occurs.
    '''
    def send_text_part(self, text: str) -> None:
        self.interface.send_text(text, self.user_id)

    '''
    receive_message() is invoked whenever a message comes in from the interface and is destined for this Session.
    It just forwards the incoming packet to the current Context() object's receive_handler().
    '''
    def receive_message(self, packet: dict) -> None:
        # Reset session timer
        self.session_timer.cancel()
        self.session_timer = Timer(self.timeout_seconds, self.timeout) 
        self.session_timer.start()

        # Handle user input
        self.current_context.receive_handler(packet)

    '''
    is_ack() check sif the incoming packet is an "ack" message from Meshtastic.
    '''
    def is_ack(self, packet: dict) -> None:
        if "decoded" in packet and packet["decoded"]["portnum"] == "ROUTING_APP":
            if packet["decoded"]["payload"] == b'\x18\x00': # I think this is an ack? Not sure.
                return True
        return False

    '''
    change_context() changes the session context to a new context object.
    It also adds the current context to context history before changing the context so the context can be reverted later if needed.
    '''
    def change_context(self, new_context: Context) -> None:
        self.context_history.append(self.current_context)
        self.current_context = new_context
        self.current_context.start()

    '''
    revert_context reverts the session context to a previous context from the self.context_history list.
    The optional 'level' argument can be used to skip back multiple levels in the history.
    Context objects at the end of the history list are removed from the list after a revert.
    '''
    def revert_context(self, levels: int =1) -> None:
        self.current_context = self.context_history[0 - levels]
        for i in range(0, levels):
            del self.context_history[-1]
        self.current_context.start()

    '''
    set_authenticated() sets the session to an authenticated session.
    It also sets the user's role appropriately based on the user's record in the user database.
    '''
    def set_authenticated(self, username: str) -> None:
        self.authenticated = True
        self.username = username
        self.role = self.user_db.get_user_role(username)

    '''
    destroy() destroys this session by removing it from the global list of sessions. This is good for when a user logs out, etc.
    '''
    def destroy(self) -> None:
        session_db.remove_session(self.user_id)

    '''
    timeout() sends a timeout message to the user and then destroys the session
    '''
    def timeout(self) -> None:
        message = Message(header="Error", body = "Session timeout!")
        self.send_message(message)
        self.destroy()