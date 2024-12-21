from contexts.context import Context
from utils.tictactoemp_db import TicTacToeMPDB
import random

'''
A multiplayer version of the TicTacToe game. It allows two players to play against each other via the BBS.
'''

STATE_BEGIN = 0
STATE_ONE_PLAYER = 1
STATE_PLAYER_1_TURN = 2
STATE_PLAYER_2_TURN = 3
STATE_PLAYER_1_WIN = 4
STATE_PLAYER_2_WIN = 5
STATE_DRAW = 6
INVALID_CHOICE = 7
STATE_PLAYER_QUIT = 9

WINS = 0
LOSSES = 1
DRAWS = 2

# Global variable list which holds all games currently happening.
games = []

'''
GameTicTacToe() holds the actual game object and state of the game
'''
class GameTicTacToe():
    def __init__(self):
        self.session1 = None
        self.session2 = None
        self.session1_scores = None
        self.session2_scores = None
        self.reset_game()

    '''
    Reset the game board and game state
    '''
    def reset_game(self) -> None:
        self.board = [1,2,3,4,5,6,7,8,9]
        self.free_spaces = 9
        self.state = STATE_BEGIN

    '''
    Player is attempting to make a move
    '''
    def player_move(self, session: "UserSession", choice: str) -> None:
        player_piece = None
        if session == self.session1:
            player_piece = "X"
        elif session == self.session2:
            player_piece = "O"

        if not player_piece:
            return

        # Search the game board to see if the chosen space is empty.
        choice_found = False
        for space in range(0, 9):
            if self.board[space] == choice:
                self.board[space] = player_piece
                self.free_spaces = self.free_spaces - 1
                choice_found = True
                break
 
        # Check to see if this player just won the game.
        result = self.check_win()
        if result == "X":
            return STATE_PLAYER_1_WIN
        if result == "O":
            return STATE_PLAYER_2_WIN

        # Player made an invalid choice
        if not choice_found:
            return INVALID_CHOICE

        # There are no free spaces left and this player didn't win so it must be a draw
        if self.free_spaces == 0:
            return STATE_DRAW

        # Change game state to say which player's turn it is
        if session == self.session1:
            return STATE_PLAYER_2_TURN
        elif session == self.session2:
            return STATE_PLAYER_1_TURN

        return None

    '''
    check_win() will return 'X' if 'X' wins, 'O' if 'O' wins, or None if no one has won.
    '''
    def check_win(self) -> None:
        # Check to see if any row has matching X's or O's
        for row in range (0, 9, 3):
            if self.board[row + 0] == self.board[row + 1] == self.board[row + 2]:
                return self.board[row][0]

        # Check to see if any column has matching X's or O's
        for col in range(0, 3, 1):
            if self.board[0 + col] == self.board[3 + col] == self.board[6 + col]:
                return self.board[0 + col]

        # Check for diagonal wins
        if self.board[0] == self.board[4] == self.board[8]:
            return self.board[0]
        if self.board[2] == self.board[4] == self.board[6]:
            return self.board[2]
        
        return

    '''
    format_board() returns the tictactoe game board in a string that can be sent to a user to view the board. ASCII art, basically.
    1|2|3
    -----
    4|5|6
    -----
    7|8|9
    '''
    def format_board(self) -> str:
        board_string = ""
        board_string += f"{self.board[0]}|{self.board[1]}|{self.board[2]}\n"
        board_string += "--------\n"
        board_string += f"{self.board[3]}|{self.board[4]}|{self.board[5]}\n"
        board_string += "--------\n"
        board_string += f"{self.board[6]}|{self.board[7]}|{self.board[8]}\n"

        return board_string

class GameTicTacToeMultiPlayer(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)
        self.prompt = "Enter the space number you want to choose or [q]uit\n"
        self.game = None
        self.db = TicTacToeMPDB()

    def find_joinable_game(self) -> None:
        if len(games) == 0:
            return self.create_game()
        
        game = games[-1]
        if game.session1 != None and game.session2 != None:
            return self.create_game()
        
        self.join_game(game)
        return game

    def join_game(self, game: GameTicTacToe) -> None:
        game.session2 = self.session
        game.session2_scores = self.db.get_user_scores(self.session.username)

    def create_game(self) -> None:
        game = GameTicTacToe()
        game.session1 = self.session
        game.session1_scores = self.db.get_user_scores(self.session.username)
        game.reset_game()
        games.append(game)
        return game

    def end_game(self, session1: "UserSession", session2: "UserSession") -> None:
        games.remove(self.game)
        if session1:
            session1.game = None
        if session2:
            session2.game = None

    def start(self) -> None:
        if self.game == None:
            self.game = self.find_joinable_game()

        if self.game.state == STATE_BEGIN:
            self.game.state = STATE_ONE_PLAYER
            self.send_player_message(self.session, "Waiting for a challenger... [Q]uit")

        elif self.game.state == STATE_ONE_PLAYER:
            if self.session.username == self.game.session1.username:
                if self.game.session2 != None:
                    self.game.state = STATE_PLAYER_1_TURN
                else:
                    self.send_player_message(self.session, "Still waiting for a challenger... [Q]uit")
            
            if self.session.username == self.game.session2.username:
                self.game.state = STATE_PLAYER_1_TURN

            self.send_player_message(self.game.session1, "A challenger appears!\n" + self.prompt)
            username = self.game.session1.username
            self.send_player_message(self.game.session2, f"{username}'s turn!")

    def receive_handler(self, packet: dict) -> None: 
        waiting_session = None
        if self.game.state == STATE_PLAYER_1_TURN:
            waiting_session = self.game.session2
        elif self.game.state == STATE_PLAYER_2_TURN:
            waiting_session = self.game.session1

        choice = self.get_text_input(packet)
        if choice.lower() == "q":
            self.send_player_message(self.session, "Quitter!")
            self.session.revert_context()

            if self.game.session2 == self.session:
                self.send_player_message(self.game.session1, "Other player quit!")
                self.game.session1.revert_context()
            else:
                self.send_player_message(self.game.session2, "Other player quit!")
                self.game.session2.revert_context()

            self.end_game(self.game.session1, self.game.session2)
            return

            
        if self.game.state == STATE_ONE_PLAYER:
            if self.session.username == self.game.session1.username:
                if self.game.session2 != None:
                    self.game.state = STATE_PLAYER_1_TURN
                else:
                    self.send_player_message(self.session, "Still waiting for a challenger... [Q]uit")
                    return
            
            if self.session.username == self.game.session2.username:
                self.game.state = STATE_PLAYER_1_TURN

            self.send_player_message(self.game.session1, "A challenger appears!\n" + self.prompt)
            self.send_player_message(self.game.session2, "Other player's turn!")
            return

        if self.session.username == waiting_session.username:
            self.send_player_message(self.session, "Please wait your turn!")
            return

        if choice.isdigit():
            choice = int(choice)
        else:
            self.send_player_error(self.session, "Error: Invalid choice.")
            return

        self.game.state = self.game.player_move(self.session, choice)

        if self.game.state == STATE_PLAYER_1_WIN or self.game.state == STATE_PLAYER_2_WIN:
            self.send_player_message(waiting_session, "YOU LOSE!")
            waiting_session.revert_context()

            self.send_player_message(self.session, "YOU WIN!")
            self.session.revert_context()

            if self.game.session1 == self.session:
                new_wins = self.game.session1_scores[WINS] + 1
                self.db.update_user_scores(self.game.session1.username, wins=new_wins)
                new_losses = self.game.session2_scores[LOSSES] + 1
                self.db.update_user_scores(self.game.session2.username, losses=new_losses)

            elif self.game.session2 == self.session:
                new_wins = self.game.session2_scores[WINS] + 1
                self.db.update_user_scores(self.game.session2.username, wins=new_wins)
                new_losses = self.game.session1_scores[LOSSES] + 1
                self.db.update_user_scores(self.game.session1.username, losses=new_losses)

            self.end_game(self.game.session1, self.game.session2)

        elif self.game.state == STATE_DRAW:
            self.send_player_message(self.game.session1, "It's a DRAW!")
            self.send_player_message(self.game.session2, "It's a DRAW!")

            waiting_session.revert_context()
            self.session.revert_context()

            new_draws = self.game.session1_scores[DRAWS] + 1
            self.db.update_user_scores(self.game.session1.username, draws=new_draws)
            new_draws = self.game.session2_scores[DRAWS] + 1
            self.db.update_user_scores(self.game.session2.username, draws=new_draws)

            self.end_game(self.game.session1, self.game.session2)

        elif self.game.state == INVALID_CHOICE:
            self.send_player_message(self.session, "Invalid choice!")
            return

        elif self.game.state == STATE_PLAYER_1_TURN:
            self.send_player_message(self.game.session1, "Your move!")
            username = self.game.session1.username
            self.send_player_message(self.game.session2, f"{username}'s turn!")

        elif self.game.state == STATE_PLAYER_2_TURN:
            self.send_player_message(self.game.session2, "Your move!")
            username = self.game.session2.username
            self.send_player_message(self.game.session1, f"{username}'s turn!")

    def send_player_message(self, session: "UserSession", text: str) -> None:
        self.message.header = "Tic Tac Toe - MP"

        if self.game.session1_scores:
            wins = self.game.session1_scores[WINS]
            losses = self.game.session1_scores[LOSSES]
            draws = self.game.session1_scores[DRAWS]
            self.message.header += f"\n{self.game.session1.username} - W:{wins} L:{losses} D:{draws}"

        if self.game.session2_scores:
            wins = self.game.session2_scores[WINS]
            losses = self.game.session2_scores[LOSSES]
            draws = self.game.session2_scores[DRAWS]
            self.message.header += f"\n{self.game.session2.username} - W:{wins} L:{losses} D:{draws}"

        self.message.header += "\n"
        self.message.body = self.game.format_board()
        self.message.footer = text
        session.send_message(self.message)

    def send_player_error(self, session: "UserSession", error: str) -> None:
        self.message.header = "Tic Tac Toe - MP"
        self.message.body = self.game.format_board()
        self.message.footer = f"Error: {error}"
        session.send_message(self.message)

         
