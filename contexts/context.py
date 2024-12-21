from utils.message import Message

'''
A base class to base other Context objects on. Provides commonly used handy functions for Context objects.

A Context object represents an interface to the user that the user can interact with. It can be a menu (via the Menu context via menu.py)
or a game or a command or anything, really. When a user chooses a menu option, the user's context switches to the corresponding context option.
User input is then handled by that Context object until the Context object invokes self.session.revert_context(). This will revert the session context
to a previous context.
'''

class Context():
    def __init__(self, session: "UserSession", command: str, description: str):
        self.session = session              # Session object belonging to a session for a given user.
        self.message = Message()            # Message object. Can be updated with message contents for sending messages to the user.
        self.command = command              # Command the user must enter to trigger this context. Usually a single letter, but it could be almost anything.
        self.description = description      # Description displayed in menus for this context. Example: "[Q]uit"

    '''
    start() called whenever a user's session switches context to this context object.
    By default, it just sends the Context object's message to the user when the user connects. This is helpful if the message is first updated to 
    contain a help screen or something to instruct the user how to interact with the context.
    '''
    def start(self) -> None:
        self.session.send_message(self.message)

    '''
    receive_handler() is used to handle user input and then do something based on that input. Once the session context is switched to this Context object,
    incoming packets will be routed to the Context object via receive_handler(). The packet submitted by the user is included as a parameter.
    '''
    def receive_handler(self, packet: dict) -> None:
        return 

    '''
    get_text_input() is a helper function to extract the text data from a packet. This is where you would typically find the user's input assuming the user
    is interacting through the Meshtastic chat app.
    '''
    def get_text_input(self, packet: dict) -> str:
        choice = None
        if "text" in packet["decoded"]:
            choice = packet["decoded"]["text"]
        return choice  

    '''
    send_error() allows you to easily send a formatted error message to the user. By default the message looks like "Error: <message>" and is included
    in the message footer rather than the body. Override this function or implement your own function to change this behavior.
    '''
    def send_error(self, error: str) -> None:
        error_message = Message(header="Error!")
        error_message.body = error
        self.session.send_message(error_message)