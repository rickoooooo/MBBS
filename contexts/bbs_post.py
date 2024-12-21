from contexts.context import Context
from utils.bbs_utils import Topic, Post
from utils.bbs_db import BBSDB as BBSDB
import time

'''
Context which handles viewing posts inside a BBS topic
'''


class BBSPost(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)
        self.message.header = "Compose reply"
        self.message.footer = "[!C]ancel [.]End Reply"
        self.bbs_db = BBSDB()
        self.topic = None
        self.post = ""

    '''
    Called when context switches to this object
    '''
    def start(self) -> None:
        num_posts = self.bbs_db.get_post_count(self.topic.uuid)
        newest_post = self.bbs_db.get_newest_post(self.topic.uuid)

        # There are no posts, so we'll just make a blank one
        '''
        if newest_post == None:
            self.message.body = "This topic is empty."
        else:
            self.message.body = Post.from_tuple(newest_post).get_string()
        '''

        self.session.send_message(self.message)

    def set_topic(self, topic: Topic) -> None:
        self.topic = topic

    '''
    Processes packets from the user
    '''
    def receive_handler(self, packet: dict) -> None:
        # Get user input
        cmd = self.get_text_input(packet)
        if not cmd:
            return

        # User wants to cancel their message, so just revert context
        if cmd.lower() == "!c":
            self.session.revert_context()
            return

        # User has finished submitting their reply
        elif cmd.lower() == ".":
            self.end_reply()

        else:
            self.append_to_post(cmd)

    '''
    Build reply message
    '''
    def append_to_post(self, text: str) -> None:
        self.post += text

    '''
    Add reply to database
    '''
    def end_reply(self) -> None:
        topic_id = self.topic.uuid
        content = self.post
        author = self.session.username
        timestamp = int(time.time())
        if self.bbs_db.create_post(topic_id, content, author, timestamp):
            self.message.body = "Reply posted to topic!"
            self.session.send_message(self.message)
        else:
            self.send_error("Problem adding reply to database!")
        self.session.revert_context(levels=2)


