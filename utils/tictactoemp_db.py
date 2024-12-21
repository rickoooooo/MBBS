import sqlite3
from utils.config import config
from utils.bbs_utils import Topic, Post

'''
Manages database for BBS functionality
'''

class TicTacToeMPDB():
    def __init__(self):
        self.db_file = config["contexts"]["tictactoemp"]["database"]
        self.initialize_database()

    '''
    Create the score table if it hasn't yet been created.
    '''
    def initialize_database(self) -> None:
        with sqlite3.connect(self.db_file) as con:
            cursor = con.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username TEXT NOT NULL, 
                wins INTEGER NOT NULL,
                losses INTEGER NOT NULL,
                draws INTEGER NOT NULL
            );
            ''')

            con.commit()

    '''
    Get user's scores
    '''
    def get_user_scores(self, username: str) -> set:
        with sqlite3.connect(self.db_file) as con:
            cursor = con.cursor()
            try:
                cursor.execute('''
                SELECT wins, losses, draws from scores
                WHERE username = ?;
                ''', (username, ))
            except Exception as e:
                return None
            else:
                scores = cursor.fetchone()

            if scores == None:
                if self.add_user(username):
                    scores = self.get_user_scores(username)
        
        return scores

    '''
    Add user to scores table
    '''
    def add_user(self, username: str) -> bool:
        with sqlite3.connect(self.db_file) as con:
            cursor = con.cursor()
            try:
                cursor.execute('''
                INSERT INTO scores
                VALUES
                (null, ?, 0, 0, 0);
                ''', (username, ))
            except Exception as e:
                return False
            else:
                con.commit()
                return True

    '''
    Update user's score
    '''
    def update_user_scores(self, username: str, wins: int=None, losses: int=None, draws: int=None) -> bool:
        with sqlite3.connect(self.db_file) as con:
            cursor = con.cursor()
            if wins:
                try:
                    cursor.execute('''
                    UPDATE scores
                    SET 'wins' = ?
                    WHERE username = ?;
                    ''', (wins, username))
                except Exception as e:
                    return False
            
            if losses:
                try:
                    cursor.execute('''
                    UPDATE scores
                    SET 'losses' = ?
                    WHERE username = ?;
                    ''', (losses, username))
                except Exception as e:
                    return False

            if draws:
                try:
                    cursor.execute('''
                    UPDATE scores
                    SET 'draws' = ?
                    WHERE username = ?;
                    ''', (draws, username))
                except Exception as e:
                    return False

            con.commit()
        
        return True
        