from datetime import datetime

class Topic():
    def __init__(self, uuid, title, last_modified):
        self.uuid = uuid
        self.title = title
        self.last_modified = last_modified
        self.posts = list()

    def get_string(self, index: int) -> str:
        str_topic = f"[{index}] ({self.last_modified}) {self.title}"
        return str_topic

class Post():
    def __init__(self, post_id: int, content: str, author: str, last_modified: int):
        self.id = post_id
        self.content = content
        self.author = author
        self.last_modified = last_modified

    @classmethod
    def from_tuple(cls, topic_tuple: tuple) -> None:
        post_id = topic_tuple[0]
        content = topic_tuple[1]
        author = topic_tuple[2]
        last_modified = topic_tuple[3]
        return cls(post_id, content, author, last_modified)

    def get_string(self) -> str:
        last_modified = datetime.fromtimestamp(int(self.last_modified)).strftime("%m-%d-%y %I:%M")
        body = ""
        body += f"<Posted by {self.author} on {last_modified}>\n"
        body += self.content
        
        return body