from contexts.context import Context
from utils.config import config

'''
Allows a user to read the guestbook.txt file on the BBS server.
'''

STATE_BEGIN = 0
STATE_READING = 1

class CmdGuestbookRead(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)
        self.guestbook_file = config["config"]["guestbook_file"]
        self.message.header = "Guestbook - Read"
        self.state = STATE_BEGIN

    '''
    Invoked when the session switches to this context.
    '''
    def start(self) -> None:
        if self.state == STATE_BEGIN:
            self.state = STATE_READING
            # Try to read the guestbook and send it to the user
            try:
                with open(self.guestbook_file, "r") as f:
                    text = f.read()
            except Exception as e:
                self.send_error("Error: Unable to read guestbook file: " + str(e))
            else:
                self.message.body = text
                self.session.send_message(self.message)
        
        elif self.state == STATE_READING:
            self.session.revert_context()

    '''
    Invoked when a packet is received from the user.
    '''
    def receive_handler(self, packet: dict) -> None:
        # TODO: This is not ideal. After reading a single page guestbook, the user is presented with no options. Sending
        # anything will revert session. This is a bit hacky to prevent the user from getting totally stuck.
        self.session.revert_context()