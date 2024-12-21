import sqlite3
import bcrypt
from utils.config import config

'''
Used to interface with SQLite database for tracking users and roles, authentication, etc.
'''

class UserDB():
    def __init__(self):
        self.db_file = f"data/{config["database"]["filename"]}"
        self.con = sqlite3.connect(self.db_file)
        self.cursor = self.con.cursor()
        self.initialize_database()

    '''
    Create the user table if it hasn't yet been created.
    '''
    def initialize_database(self) -> None:
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT NOT NULL, 
            password CHAR(60) NOT NULL, 
            role TEXT NOT NULL
        );
        ''')

        self.con.commit()

    '''
    Returns True if a username exists in the database and is therefore taken.
    '''
    def check_username_exists(self, username: str) -> bool:
        username_lower = username.lower()

        try:
            self.cursor.execute('''
            SELECT * FROM users
            WHERE username = ?
            ''', (username_lower,))
            
            user = self.cursor.fetchone()
            if user:
                return True

        except Exception as e:
            return True

        return False

    '''
    Adds a user record to the database with the default "user" role.
    Returns True if successful or False if not.
    '''
    def user_register(self, username: str, password: str) -> bool:
        username_lower = username.lower()

        if self.check_username_exists(username_lower):
            return False

        password_bytes = self.password_to_bytes(password)
        hashed_password = self.get_hashed_password(password_bytes)

        self.cursor.execute('''
        INSERT INTO users
        VALUES
        (null, ?,?,"user")
        ''', (username_lower, hashed_password))

        self.con.commit()
        return True

    '''
    Validates a user's password against the hashed password in the database.
    Returns True if they match, False if not.
    '''
    def user_authenticate(self, username: str, password: str) -> bool:
        username_lower = username.lower()

        try:
            self.cursor.execute('''
            SELECT * FROM users
            WHERE username = ?
            ''', (username_lower,))

            user_record = self.cursor.fetchone()
            if not user_record:
                return False

            user_password = user_record[2]
        except Exception as e:
            return False
        else:
            hashed_password = self.password_to_bytes(password)

        return bcrypt.checkpw(hashed_password, user_password)

    '''
    Retrieves a user's role from the user database and returns it as a string.
    '''
    def get_user_role(self, username: str) -> str:
        username_lower = username.lower()

        try:
            self.cursor.execute('''
            SELECT role FROM users
            WHERE username = ?
            ''', (username_lower,))

            role_record = self.cursor.fetchone()
            if not role_record:
                return None

            user_role = role_record[0]
        except Exception as e:
            return None
        return user_role

    def get_hashed_password(self, password: bytes) -> bytes:
        return bcrypt.hashpw(password, bcrypt.gensalt())

    def password_to_bytes(self, password: str) -> bytes:
        return bytes(password, encoding='utf-8')
