#from utils.user_session import UserSession as UserSession

'''
Keeps track of user sessions.
Currently just a dict where each user_id (device id) has a session object in a large dict.
This could be changed to be an actual database
'''

class SessionDB():
    def __init__(self):
        self.user_sessions = {} # {user_id: UserSession}

    '''
    Check if a given user ID already has a session in the list.
    '''
    def check_session(self, user_id: int) -> bool:
        if user_id in self.user_sessions:
            return True
        return False

    '''
    Add a new session to the list. Tie it to a user_id.
    '''
    def add_session(self, user_id: int, session: "UserSession") -> bool:
        if self.check_session(user_id):
            return False
        self.user_sessions[user_id] = session
        return True

    '''
    Remove a session from the list based on a given user_id.
    '''
    def remove_session(self, user_id: int) -> bool:
        if self.check_session(user_id):
            del self.user_sessions[user_id]
            return True
        return False

    '''
    Get the session object based on a given user_id.
    '''
    def get_session(self, user_id: int) -> "UserSession":
        if self.check_session(user_id):
            return self.user_sessions[user_id]
        return None

session_db = SessionDB()