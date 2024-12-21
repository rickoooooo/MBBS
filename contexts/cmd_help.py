from contexts.context import Context

'''
A simple 'Help' function which will send the user the current menu options.
'''

class CmdHelp(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)
        self.message.header = None
        self.message.border_top = None
        self.message.body = None
        self.message.footer = None

    '''
    The Help context really just needs to print the contents of the menu again. We can do this by simply reverting back
    to the menu Context, since it will automatically display the help menu when this happens.
    '''
    def start(self) -> None:
        self.session.revert_context()