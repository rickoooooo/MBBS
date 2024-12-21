from contexts.context import Context
import subprocess

'''
Dangerous!

An example context which allows the user to run shell commands on the server
'''

class CmdShell(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)
        self.message.header = "Command Shell"
        self.text = "Enter shell command or [q]uit> "
        self.message.body = self.text

    def receive_handler(self, packet: dict) -> str:
        cmd = self.get_text_input(packet)
        if not cmd:
            return

        # User wants to quit, so revert context
        if cmd.lower() == "q":
            self.session.revert_context()
            return
        
        try:
            # Execute specified command in shell
            result = subprocess.run([cmd], stdout=subprocess.PIPE)

        except Exception as e:
            # Something went wrong...
            self.send_error("Error executing shell command!")

        else:
            # Nothing went wrong.
            self.message.body = str(result.stdout.decode("utf-8"))
            self.session.send_message(self.message)

        self.message.body = self.text
        self.session.send_message(self.message)
        return
