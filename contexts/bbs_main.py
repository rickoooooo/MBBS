from contexts.context import Context
from contexts.bbs_topic import BBSTopic as BBSTopic
from utils.bbs_db import BBSDB as BBSDB
from utils.message import Message as Message
from meshtastic import mesh_pb2
from datetime import datetime
from utils.bbs_utils import Topic, Post
import subprocess
import time

'''
List topics from the BBS database
'''

TOPIC_COL_UUID = 0
TOPIC_COL_TITLE = 1
TOPIC_COL_LAST_MODIFIED = 2

BBS_COMMANDS = "[C]reate [N]ext [P]rev [Q]uit [#]"

class BBSMain(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)
        self.message.header = "Bulletin Board"
        self.message.footer = BBS_COMMANDS
        self.message.body = ""
        self.bbs_db = BBSDB()
        self.next_func = None       # Next function that should be called when the user replies
        self.topics = list()
        self.pages = list()
        self.page_num = 0
        self.max_message_size = mesh_pb2.Constants.DATA_PAYLOAD_LEN - len(BBS_COMMANDS) - 10 - 20

    '''
    Called when context switches to this object
    '''
    def start(self) -> None:
        self.generate_topics_list()
        self.list_topics()

    '''
    Handle user input
    '''
    def receive_handler(self, packet: dict) -> str:
        if self.next_func:
            self.next_func(packet)
            return

        # Get user input
        cmd = self.get_text_input(packet)
        if not cmd:
            return

        # User wants to quit, so revert context
        if cmd.lower() == "q":
            self.session.revert_context()
            return

        # User wants to create a new topic
        elif cmd.lower() == "c":
            self.request_topic_name()

        # User wants to see next page of topics
        elif cmd.lower() == "n":
            self.next_page()

        # User wants to see previous page of topics
        elif cmd.lower() == "p":
            self.prev_page()

        # User wants to choose a topic
        elif cmd.isdigit():
            self.choose_topic(int(cmd))

        else:
            self.send_error("Invalid option!")
        
        return

    '''
    Ask user for topic name when creating new topic
    '''
    def request_topic_name(self) -> None:
        self.message.body = "Enter topic name:"
        self.message.footer = None
        self.session.send_message(self.message)
        self.next_func = self.create_topic

    '''
    Create the topic in the DB
    '''
    def create_topic(self, packet: dict) -> None:
        topic = self.get_text_input(packet)
        if not topic:
            self.session.send_error("Invalid topic name!")
            return

        timestamp = int(time.time())
        if not self.bbs_db.create_topic(topic, timestamp):
            self.session.send_error("Unable to create topic in database!")

        self.message.body = "Topic created"
        self.session.send_message(self.message)
        self.list_topics()

    '''
    Update a list of topics based on whatever is in the DB
    '''
    def generate_topics_list(self) -> None:
        topics = self.bbs_db.list_topics()
        self.topics = list()

        for i in range(0, len(topics)):
            index = i + 1
            uuid = topics[i][TOPIC_COL_UUID]
            title = topics[i][TOPIC_COL_TITLE]
            last_modified_unixtime = topics[i][TOPIC_COL_LAST_MODIFIED]
            last_modified = datetime.fromtimestamp(int(last_modified_unixtime)).strftime("%m-%d-%y %I:%M")
            topic = Topic(uuid, title, last_modified)
            
            self.topics += [topic]

    '''
    Convert the list of topics to a single string for sending to the user
    '''
    def generate_topics_pages(self) -> None:
        self.pages = list()

        text = ""
        counter = 1
        for topic in self.topics:
            topic_string = topic.get_string(counter)
            if len(text + topic_string) > self.max_message_size:
                text = text.strip()
                self.pages += [text]
                text = ""

            text += f"{topic_string}\n"
            counter += 1

        if (len(self.topics) > 0):
            # If the last line ends with newline then we haven't yet accounted for the final page
            if text[-1] == "\n":
                text = text.strip()
                self.pages += [text]

    '''
    Generate a list of topics, convert to string, and send message to user with the list
    '''
    def list_topics(self) -> None:
        self.generate_topics_list()
        self.generate_topics_pages()
        if (len(self.pages) > 0):
            self.message.body = self.pages[self.page_num]
        else:
            self.message.body = "<Crickets chirping>"
        page_counter = self.build_page_counter()
        self.message.footer = f"{BBS_COMMANDS }\n{page_counter}"
        self.session.send_message(self.message)
        self.next_func = None

    '''
    Generate page counter
    '''
    def build_page_counter(self) -> None:
        current_page = self.page_num + 1
        total_pages = len(self.pages)
        text = f"Page {current_page}/{total_pages}"
        return text

    '''
    Switch to next page
    '''
    def next_page(self) -> None:
        if self.page_num < (len(self.pages) - 1):
            self.page_num += 1
            self.list_topics()
        else:
            self.send_error("No pages left!")

    '''
    Switch to previous page
    '''
    def prev_page(self) -> None:
        if self.page_num > 0:
            self.page_num -= 1
            self.list_topics()
        else:
            self.send_error("No pages left!")

    '''
    Choose a topic
    '''
    def choose_topic(self, choice: int) -> None:
        topic_num = choice - 1
        if topic_num < 0 or topic_num >= len(self.topics):
            self.send_error("Invalid page number!")
            return

        topic = self.topics[topic_num]
        topic_context = BBSTopic(self.session, "", f"BBS - {topic.title[0:15]}...")
        topic_context.topic = topic
        self.session.change_context(topic_context)

        #self.message.body = Post.from_tuple(newest_post)
        #self.session.send_message(self.message)

        