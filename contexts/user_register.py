import sqlite3
import string
from contexts.context import Context
from utils.user_db import UserDB
from utils.config import config

'''
Allows a user to register their own account on the BBS system.
'''

STATE_BEGIN = 0
STATE_USERNAME = 1
STATE_PASSWORD = 2

class UserRegister(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)
        self.command = command
        self.description = description

        self.message.header = "User registration"
        self.state = STATE_BEGIN    # Tracks state of the registration process
        self.user_db = UserDB()
        self.username = ""

    '''
    Called when context is switched to this context object
    '''
    def start(self) -> None:
        if self.state == STATE_BEGIN:
            self.state = STATE_USERNAME
            self.message.body = "Please submit desired username."
            self.session.send_message(self.message)

    '''
    Handle incoming packets
    '''
    def receive_handler(self, packet: dict) -> None:
        text = self.get_text_input(packet)
    
        # User has just connected to this context, so we need to ask them for their username to start.
        if self.state == STATE_BEGIN:
            self.state = STATE_USERNAME
            self.message.body = "Please submit desired username."
            self.session.send_message(self.message)

        # User has entered their username, so now we'll validate that it isn't taken and then ask for a password.
        elif self.state == STATE_USERNAME:
            # Check to ensure the username only uses acceptable characters
            if not self.validate_username(text):
                self.send_error("Invalid characters in username! Use [a-z,A-Z,0-9,-,_,.]")
                return

            username_min_length = config["config"]["username_min_length"]
            username_max_length = config["config"]["username_max_length"]
            if len(text) < username_min_length or len(text) > 30:
                self.send_error(f"Username must be between {username_min_length} and {username_max_length} characters long.")
                return
            if self.user_db.check_username_exists(text):
                self.message.body = "Username taken.\nPlease submit desired username."
                self.session.send_message(self.message)
                return

            self.username = text
            self.state = STATE_PASSWORD
            self.message.body = "Please submit desired password"
            self.session.send_message(self.message)
            return

        # User has entered a password. We'll register the user now based on the supplied username and password.
        elif self.state == STATE_PASSWORD:
            if self.user_db.user_register(self.username, text):
                self.message.body = "Registration complete!\n\n"
                self.session.send_message(self.message)
                self.session.revert_context()
            else:
                self.message.body = "Error registering new user!"
                self.session.send_message(self.message)
                self.session.revert_context()
            return

        # We ended up in an unhandled state somehow. This is unexpected so send an error.
        else:
            self.message.body = "Error: Invalid state."
            self.session.send_message(self.message)

    def validate_username(self, username: str) -> bool:
        allowed = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + '._-')
        return set(username) <= allowed
