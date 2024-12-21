from contexts.context import Context
import random

'''
A single player TicTacToe game.
'''

STATE_BEGIN = 0
STATE_PLAYING = 1

class GameTicTacToe(Context):
    def __init__(self, session: "UserSession", command: str, description: str):
        super().__init__(session, command, description)
        self.prompt = "Enter the space number you want to choose or [q]uit"
        self.reset_game()
    '''
    reset_game() will reset the game board and state
    '''
    def reset_game(self) -> None:
        self.board = [1,2,3,4,5,6,7,8,9]
        self.free_spaces = 9
        self.state = STATE_BEGIN

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
        board_string += f"{self.board[0]}|{self.board[1]}|{self.board[2]}|\n"
        board_string += "--------\n"
        board_string += f"{self.board[3]}|{self.board[4]}|{self.board[5]}|\n"
        board_string += "--------\n"
        board_string += f"{self.board[6]}|{self.board[7]}|{self.board[8]}|\n"

        return board_string

    '''
    Invoked when the context changes to this game object
    '''
    def start(self) -> None:
        self.reset_game()
        self.message.body = self.format_board() + "\n" + self.prompt
        self.session.send_message(self.message)
        self.state = STATE_PLAYING

    '''
    Invoked when a packet arrives. handles user input and basically the main logic of the game
    '''
    def receive_handler(self, packet: dict) -> str:
        # if user hasn't started playing yet, then begin the game.
        if self.state == STATE_BEGIN:
            self.state = STATE_PLAYING
            self.message.body = self.format_board() + "\n" + self.prompt
            self.session.send_message(self.message)
            return
            
        # Get player choice, then ensure it is either the quit command, or a number.
        choice = self.get_text_input(packet)

        if choice.lower() == "q":
            session.revert_context()
            return

        if choice.isdigit():
            choice = int(choice)
        else:
            self.send_error("Invalid choice.")
            return

        # Search the game board to see if the chosen space is empty.
        choice_found = False
        for space in range(0, 9):
            if self.board[space] == choice:
                self.board[space] = "X"
                self.free_spaces = self.free_spaces - 1
                choice_found = True
                break

        # Player chose a space that wasn't empty
        if not choice_found:
            self.send_error("Invalid choice.")
            return

        # Check to see if the player won.
        if self.check_win() == "X":
            self.message.body = self.format_board() + "\n" + "Congrats! You won!"
            self.session.send_message(self.message)
            self.session.revert_context()
            return

        # Entire board is full, so it must be a draw
        if self.check_draw():
            self.message.body = "It's a draw!"
            self.session.send_message(self.message)
            self.session.revert_context()
            return
        
        # Computer randomly chooses a space over and over until it happens to choose one that isn't taken
        choice_found = False
        while not choice_found:
            comp_choice = random.randrange(1, 10, 1)        # Choose a random space on the board for the computer player
            if self.board[comp_choice - 1] == comp_choice:
                self.board[comp_choice - 1] = "O"
                choice_found = True
                self.free_spaces = self.free_spaces - 1

        # Check to see if the computer won.
        if self.check_win() == "O":
            self.message.body = self.format_board() + "\n" + "YOU LOSE!"
            self.session.send_message(self.message)
            self.session.revert_context()
            return

        if self.check_draw():
            self.message.body = "It's a draw!"
            self.session.send_message(self.message)
            self.session.revert_context()
            return

        # Send board back to the user and let them take another turn
        self.message.body = self.format_board() + "\n" + self.prompt
        self.session.send_message(self.message)
        return

    '''
    check_win() will return 'X' if 'X' wins, 'O' if 'O' wins, or None if no one has won.
    '''
    def check_win(self) -> str:
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
    Check to see if the game is a draw
    '''
    def check_draw(self) -> bool:
        # There are no spaces left, so it must be a draw
        if self.free_spaces == 0:
            return True
        return False

