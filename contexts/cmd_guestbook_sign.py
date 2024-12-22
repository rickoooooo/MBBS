from contexts.context import Context
from utils.config import config
from datetime import datetime

'''
Allows the user to sign the BBS guestbook.
'''

class CmdGuestbookSign(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)
        self.message.header = "Guestbook - Sign"
        self.guestbook_file = config["guestbook"]["guestbook_file"]

    '''
    Invoked when this Context starts. Send welcome message.
    '''
    def start(self) -> None:
        self.message.body = "Submit your guestbook message or [q]uit"
        self.session.send_message(self.message)
        return

    '''
    Write a string to the guestbook.
    '''
    def sign(self, text: str) -> bool:
        timestamp = datetime.today().strftime('%Y-%m-%d')

        try:
            with open(self.guestbook_file, "a") as f:
                f.write(f"{timestamp}|{self.session.username}|{text}\n")
        except Exception as e:
            return False
        else:
            return True
        return False

    '''
    Receive packets from user
    '''
    def receive_handler(self, packet: dict) -> str:
        text = self.get_text_input(packet)

        # User wants to quit, so revert context
        if text.lower() == "q":
            self.session.revert_context()
            return

        # Try to write the user's message to the guestbook and send them a reply.
        if self.sign(text):
            self.message.body = "Guestbook message saved. Thank you!"
            self.session.send_message(self.message)
            self.session.revert_context()
            return
            
        self.send_error("Error saving message to guestbook!")
        return