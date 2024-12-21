from utils.config import config

'''
A Message object holds data which will be converted to text and transmitted to the end user.
They are formatted like this:

HEADER
====================
BODY
====================
FOOTER

The header and footer borders are defined in the config.toml file by default but can be overridden.
They will only appear if there is header or footer text. This message object should be updated by a C
Context object and then it can be passed to the UserSession.send_message() function to send to a user.
'''

class Message():
    def __init__(self, header: str=None, body: str=None, footer: str=None, border_top: str=None, border_bottom: str=None):
        self.header = header
        self.body = body
        self.footer = footer
        self.border_top = border_top
        self.border_bottom = border_bottom

        if border_top == None:
            if "border_top" in config["messages"]:
                self.border_top = config["messages"]["border_top"]
            else:
                self.border_top = None
        if border_bottom == None:
            if "border_bottom" in config["messages"]:
                self.border_bottom = config["messages"]["border_bottom"]
            else:
                self.border_bottom = None

    '''
    Return the Message as a text string
    '''
    def get_text(self) -> str:
        text = ""
        if self.header:
            text += self.header + "\n"
            if self.border_top:
                text += self.border_top + "\n"
        if self.body:
            text += self.body + "\n"
        if self.border_bottom:
            text += self.border_bottom + "\n"
        if self.footer:
            text += self.footer + "\n"
        return text

    '''
    Return the size of the message as it would be if converted to text.
    '''
    def get_message_size(self) -> int:
        return len(self.get_text())

    '''
    Return a copy of this object
    '''
    def copy(self) -> "Message":
        new_message = Message(self.header, self.body, self.footer, self.border_top, self.border_bottom)
        return new_message
        