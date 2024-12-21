from contexts.context import Context
from meshtastic import mesh_pb2
import copy

'''
If a message is too long to fit in a single Meshtastic message packet, this context will handle pagination. It splits the packet
into multiple pages and allows the user to page through them or jump to a specific page, or cancel entirely.
'''

SPACE_FOR_PAGE_COUNTER = 9

class MessagePager(Context):
    def __init__(self, session: "UserSession", message: "Message"):
        super().__init__(session, None, None)
        self.message = copy.deepcopy(message)
        self.message_text = None
        self.footer_text = "[N]ext [C]ancel Page[#] "

        # Not sure why, but I have to make packets less than the DATA_PAYLOAD_LEN in order for them to send properly. So I subtract 10.
        self.max_message_size = mesh_pb2.Constants.DATA_PAYLOAD_LEN - 10
        self.messages = []
        self.total_pages = 0
        self.current_page = 0
        self.page_counter = f" {self.current_page}|{self.total_pages}"

    '''
    Called when session context switches to this context object
    '''
    def start(self) -> None:
        # Check if message is small enough to send without paging it
        if self.message.get_message_size() <= self.max_message_size:
            self.session.send_message(self.message)
            self.session.revert_context()
            return

        # Otherwise, process the message
        self.process_message()

    '''
    Convert a long text message to a list of "pages". A "page" is just a string with part of the overall message.
    '''
    def process_message(self) -> None:
        # Split long message into multiple message "pages"
        message_text = self.message.get_text()
        footer_size = len(self.footer_text) + SPACE_FOR_PAGE_COUNTER
        page_size = self.max_message_size - footer_size - len(self.message.border_bottom)

        self.messages = [message_text [i:i+(page_size)] for i in range(0, len(message_text), page_size)]
        self.total_pages = len(self.messages)
        self.current_page = 0
        self.message.header = None
        self.message.border_top = None
        self.message.body = self.get_current_page()
        self.session.send_message(self.message)

    '''
    Returns the current page from the list of pages as a string
    '''
    def get_current_page(self) -> str:
        page_text = self.messages[self.current_page]

        if self.current_page < self.total_pages:
            self.page_counter = f" {self.current_page + 1}/{self.total_pages}"
            self.message.footer = self.footer_text + self.page_counter

        return page_text

    '''
    User wants to see the next page
    '''
    def next_page(self) -> None:
        if self.current_page <= self.total_pages:
            self.current_page += 1
            page_text = self.messages[self.current_page]
            self.message.body = self.get_current_page()
            if self.current_page == self.total_pages - 1:
                self.footer = None
                self.session.send_message(self.message)
                #self.session.revert_context()
            else:
                self.session.send_message(self.message)
    '''
    Invoked whenever a packet comes into this context. Handles user input.
    '''
    def receive_handler(self, packet: dict) -> None:
        command = self.get_text_input(packet)
        if not command:
            return

        # If the user is not viewing the last page...
        if self.current_page < self.total_pages:
            # If the user wants the [N]ext page
            if command.lower() == "n":
                self.next_page()
                return
            
            # If the user wants to [C]ancel
            elif command.lower() == "c":
                self.session.revert_context()
                return
            
            # If the user wants to specify a page number to jump to
            elif command.isdigit():
                new_page = int(command)
                if new_page > 0 and new_page <= self.total_pages:
                    self.current_page = int(command) - 1
                    self.message.body = self.get_current_page()
                    self.session.send_message(self.message)
                    if self.current_page == self.total_pages - 1:
                        self.session.revert_context()
                        return
                    return
                else:
                    self.message.body = "Error: Invalid page number."
                    self.session.send_message(self.message)
                    return
            
            # User entered something that isn't a valid command
            else:
                self.message.body = "Invalid option!"
                self.session.send_message(self.message)
        return