import sqlite3
from contexts.context import Context
from contexts.menu import Menu
from utils.user_db import UserDB
from utils.config import config
from utils.log import logger

'''
Authenticates a user to the BBS. When a user successfully authenticates, the context will switch to whatever the second menu object is in config.toml.
'''

STATE_BEGIN = 0
STATE_USERNAME = 1
STATE_PASSWORD = 2

class UserLogin(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)
        self.command = command
        self.description = description

        self.state = STATE_BEGIN
        self.user_db = UserDB()
        self.username = ""

        self.message.header = "User login"

    '''
    Called when the session context switches to this Context
    '''
    def start(self) -> None:
        # Session has just switched to this context, so ask the user for their username and then adjust the state.
        if self.state == STATE_BEGIN:
            self.state = STATE_USERNAME
            self.message.body = "Please submit username."
            self.session.send_message(self.message)
            return

    '''
    Called whenever a packet comes into this context
    '''
    def receive_handler(self, packet: dict) -> str:
        text = self.get_text_input(packet)

        # User has entered their username, so ask for the password.
        if self.state == STATE_USERNAME:
            self.username = text
            self.state = STATE_PASSWORD
            self.message.body = "Please submit password."
            self.session.send_message(self.message)
            return

        # User has entered their password
        elif self.state == STATE_PASSWORD:
            # Try to authenticate
            if self.user_db.user_authenticate(self.username, text):
                logger.info(f"User {self.username} logged in.")
                self.message.body = "Login successful!"
                self.session.send_message(self.message)
                self.session.set_authenticated(self.username)

                # Change the user's context to the second menu context so they can access the main menu now that they logged in.
                bbs_menu_context = Menu(self.session, config["menus"][1])
                self.session.change_context(bbs_menu_context)
                return

            # User failed to authenticate
            else:
                logger.info(f"User {self.username} failed to log in.")
                self.message.body = "Login failure!"
                self.session.send_message(self.message)
                self.session.revert_context()
                return

        # Somehow we ended up in an unhandled state. Send an error.
        else:
            self.message.body = "Error: invalid state"
            self.session.send_message(self.message)
            return
