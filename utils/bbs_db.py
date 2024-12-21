import sqlite3
import uuid
from utils.config import config
from utils.bbs_utils import Topic, Post

'''
Manages database for BBS functionality
'''

class BBSDB():
    def __init__(self):
        self.db_file = f"data/{config["bbs"]["database"]}"
        self.con = sqlite3.connect(self.db_file)
        self.cursor = self.con.cursor()
        self.initialize_database()

    '''
    Create the topics table if it hasn't yet been created.
    '''
    def initialize_database(self) -> None:
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS topics(
            uuid CHAR(32) PRIMARY KEY NOT NULL, 
            title TEXT NOT NULL, 
            last_modified DATETIME NOT NULL
        );
        ''')

        self.con.commit()

    '''
    Create Topic
    '''
    def create_topic(self, topic_name: str, timestamp:int) -> bool:
        topic_id = str(uuid.uuid4()).replace('-', '')

        if not self.add_topic_to_list(topic_id, topic_name, timestamp):
            return False

        if not self.create_topic_table(topic_id):
            return False

        return True
        
    '''
    Try to create a new DB table for this topic. If it fails, we can detect the error here
    '''
    def add_topic_to_list(self, topic_id: str, topic_name: str, timestamp: int) -> bool:
        try:
            self.cursor.execute('''
            INSERT INTO topics
            VALUES
            (?, ?, ?)
            ''', (topic_id, topic_name, timestamp))
        except Exception as e:
            return False
        self.con.commit()

        return True

    '''
    Try to add the topic to the list of topics
    '''
    def create_topic_table(self, topic_id: str) -> bool:
        table_name = f"topic_{topic_id}"
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS '''
            + table_name + '''(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                author TEXT NOT NULL,
                timestamp DATETIME NOT NULL
            );
            ''')
        except Exception as e:
            return False
        
        return True

    '''
    Create a new post to a topic.
    '''
    def create_post(self, topic_id: str, content: str, username: str, datetime: int) -> bool:
        table_name = f"topic_{topic_id}"

        # Add post to topic table
        try:
            self.cursor.execute('''
            INSERT INTO '''
            + table_name + 
            ''' VALUES
            (null, ?, ?, ?)
            ''', (content, username, datetime))
        except Exception as e:
            return False
        self.con.commit()

        # Update topic table with new timestamp
        try:
            self.cursor.execute('''
            UPDATE topics
            SET 'last_modified' = ?
            WHERE uuid LIKE ?;
            ''', (datetime, topic_id))
        except Exception as e:
            return False
        self.con.commit()
        
        return True

    '''
    Retrieve a list of topics
    '''
    def list_topics(self) -> list:
        topics = list()

        try:
            self.cursor.execute('''
            SELECT * from topics
            ORDER BY last_modified DESC;
            ''')
        except:
            pass
        else:
            topics = self.cursor.fetchall()
        
        return topics

    '''
    Retrieve a post
    '''
    def get_post(self, topic_id: str, post_id: int) -> tuple:
        table_name = f"topic_{topic_id}"
        result = tuple()

        try:
            self.cursor.execute('''
            SELECT * from ?
            WHERE uuid = ?;
            ''', (table_name, post_id))
        except:
            pass
        else:
            result = self.cursor.fetchone()
        
        return result

    '''
    Get number of posts in a topic
    '''
    def get_post_count(self, topic_id: str) -> int:
        table_name = f"topic_{topic_id}"
        result = 0

        try:
            self.cursor.execute('''
            SELECT * from '''
            + table_name +
            ''';''')
        except:
            pass
        else:
            posts = self.cursor.fetchall()
            result = len(posts)
        
        return result

    '''
    Get specific post from topic:
    '''
    def get_all_posts(self, topic_id: str) -> list:
        table_name = f"topic_{topic_id}"
        result = list()

        try:
            self.cursor.execute('''
            SELECT * from '''
            + table_name + 
            ''' ORDER BY timestamp DESC;
            ''')
        except:
            pass
        else:
            entries = self.cursor.fetchall()

            for entry in entries:
                post = Post(entry[0], entry[1], entry[2], entry[3])
                result += [post]
        
        return result

    '''
    Get newest post from topic
    '''
    def get_newest_post(self, topic_id: str) -> tuple:
        table_name = f"topic_{topic_id}"
        result = tuple()

        try:
            self.cursor.execute('''
            SELECT * from '''
            + table_name + 
            ''' ORDER BY 'datetime' DESC
            LIMIT 1;
            ''')
        except Exception as e:
            pass
        else:
            result = self.cursor.fetchone()
        
        return result