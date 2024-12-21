from contexts.context import Context

'''
A simple command which can be included in various menus to allow the user to go back to a previous menu.
'''

class CmdBack(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)

    '''
    This Context object is intended to be a menu option that a user can choose to go back to the previous context.
    To make that happen, we need to revert out of this context, and the menu that led here. Therefore we revert_context(2)
    '''
    def start(self) -> None:
        self.session.revert_context(levels=2)