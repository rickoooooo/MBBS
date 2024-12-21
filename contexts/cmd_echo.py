from contexts.context import Context

'''
An example Context which allows the user to enter some text. The text will be echoed back to the user.
'''

class CmdEcho(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)
        self.message.header = "ECHO"
        self.message.body = "Enter a message and it will be echoed back to you."

    '''
    Processes packets from the user
    '''
    def receive_handler(self, packet: dict) -> None:
        user_input = self.get_text_input(packet)
        self.message.body = user_input

        # If the user submitted text, then send the same text back to them (echo it)
        if user_input:
            self.session.send_message(self.message)

        # Revert context back to the previous one (probably a menu)
        self.session.revert_context()