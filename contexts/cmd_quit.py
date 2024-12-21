import subprocess
from contexts.context import Context
from utils.config import config

'''
A default context object which can be used to quit the BBS and destroy the user's session.
'''

class CmdQuit(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)

    '''
    This Context quits the BBS, so destroy the session and send a goodbye message
    TODO: Load goodbye message from config.toml.
    '''
    def start(self) -> None:
        self.session.destroy()
        self.message.header = "BBS"
        body = config["contexts"]["quit"]["msg_goodbye"]
        self.message.body = body
        self.session.send_message(self.message)