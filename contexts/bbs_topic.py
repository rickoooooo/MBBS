from contexts.context import Context
from contexts.bbs_post import BBSPost as BBSPost
from utils.bbs_utils import Topic, Post
from utils.bbs_db import BBSDB as BBSDB

'''
Context which handles viewing posts inside a BBS topic
'''

TOPIC_COMMANDS = "[M]ore [R]eply [N]ext [P]rev [B]ack [#]"

class BBSTopic(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)
        self.message.header = description
        self.message.footer = TOPIC_COMMANDS
        self.topic = None
        self.bbs_db = BBSDB()
        self.post_num = 0
        self.num_posts = 0
        self.posts = list()

    '''
    Called when context switches to this object
    '''
    def start(self) -> None:
        self.num_posts = self.bbs_db.get_post_count(self.topic.uuid)
        if self.num_posts != 0:
            self.posts = self.bbs_db.get_all_posts(self.topic.uuid)
            current_post = self.posts[self.post_num]
            self.send_message(current_post.get_string(), one_page=True)

        # There are no posts, so we'll just make a blank one
        else:
            self.send_message("This topic is empty.")

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

        # User wants to go back, so revert context
        if cmd.lower() == "b":
            self.session.revert_context()
            return

        # User wants to create a new reply to the topic
        elif cmd.lower() == "r":
            self.reply_to_topic()

        # User wants to see next page of posts
        elif cmd.lower() == "n":
            self.next_post()

        # User wants to see previous page of posts
        elif cmd.lower() == "p":
            self.prev_post()

        # User wants to read more of a long post:
        elif cmd.lower() == "m":
            self.more()

        # User wants to choose a post to view
        elif cmd.isdigit():
            self.choose_post(int(cmd))

        else:
            self.send_error("Invalid option!")

    '''
    Post a reply to a topic
    '''
    def reply_to_topic(self) -> None:
        post_context = BBSPost(self.session, None, None)
        post_context.topic = self.topic
        self.session.change_context(post_context)

    '''
    User wants to see the next post
    '''
    def next_post(self) -> None:
        if self.post_num >= (self.num_posts - 1):
            self.send_error("No more posts in this topic!")
            return

        self.post_num += 1
        post = self.posts[self.post_num]
        self.send_message(post.get_string(), one_page=True)

    '''
    User wants to see the previous post
    '''
    def prev_post(self) -> None:
        if self.post_num <= 0:
            self.send_error("No more posts in this topic!")
            return

        self.post_num -= 1
        post = self.posts[self.post_num]
        self.send_message(post.get_string(), one_page=True)

    '''
    Build the post counter string
    '''
    def build_post_counter(self) -> None:
        post_num = self.post_num + 1
        total_posts = len(self.posts)
        text = f"Post {post_num}/{total_posts}"
        return text

    '''
    Send message with updated footer
    '''
    def send_message(self, text: str, one_page: bool=True) -> None:
        self.message.body = text
        page_counter = self.build_post_counter()
        self.message.footer = f"{TOPIC_COMMANDS}\n{page_counter}"
        if one_page:
            self.session.send_one_page(self.message)
        else:
            self.session.send_message(self.message)

    '''
    User wants to see the entirety of a long message
    '''
    def more(self) -> None:
        post = self.posts[self.post_num]
        self.send_message(post.get_string(), one_page=False)

    '''
    User wants to view specific post
    '''
    def choose_post(self, post_num: int) -> None:
        if post_num <= 0 or post_num > self.num_posts:
            self.send_error("Invalid post number!")
            return

        self.post_num = post_num - 1
        post = self.posts[self.post_num]
        self.send_message(post.get_string(), one_page=True)
