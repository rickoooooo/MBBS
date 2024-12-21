import subprocess
from contexts.context import Context

'''
Example context which will run `uname -a` in a command shell and send the output back to the user.
'''

class CmdSysinfo(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)
        self.message.header = "SysInfo"

    '''
    Invoked when session context switches to this object.
    It will execute a `uname -a` in a shell and return the result
    '''
    def start(self) -> str:
        try:
            result = subprocess.run(['uname', '-a'], stdout=subprocess.PIPE)
        except Exception as e:
            self.send_error("Unable to execute command!")
        else:
            self.message.body = str(result.stdout.decode("utf-8"))
            self.session.send_message(self.message)
            
        self.session.revert_context()
        return