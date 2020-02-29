from gamestatenode import GameStateNode
from copy import deepcopy
import re
"""
A GameStateNode representation of the game Tic Tac Toe.
"""

class TicTacToeGameState(GameStateNode):

    num_rows = 3  # board height
    num_cols = 3  # board width
    board_str = {0: "_", 1 : "X", 2: "0"}

    """
    A 'static' method that reads data from a text file and returns
    a GameStateNode which is an initial state.
    """
    @staticmethod
    def readFromFile(filename):
        with open(filename, 'r') as file:
            board = []
            first_player = int(file.readline())

            for i in range(TicTacToeGameState.num_rows):
                row = [int(x) for x in re.split(",| |\|",file.readline())]
                assert(len(row) == TicTacToeGameState.num_cols)
                assert(all(n in TicTacToeGameState.player_numbers or n == 0 for n in row))
                board.append(row)

        return TicTacToeGameState(
            board_array = board,
            parent = None,
            path_length = 0,
            previous_action = None,
            current_player = first_player)




    """
    A 'static' method that creates some default
    GameStateNode which is an initial state (e.g. standard blank board).
    """
    @staticmethod
    def defaultInitialState():
        return TicTacToeGameState(
            board_array = [[0 for c in range(TicTacToeGameState.num_cols)] for r in range(TicTacToeGameState.num_rows)],
            parent = None,
            path_length = 0,
            previous_action = None,
            current_player = 1)

    """
    A 'static' method that translates a string representing an action
    (say, a user's input) into the appropriate datatype for that action.

    It is not necessary to error handle invalid actions here.
    """
    @staticmethod
    def str_to_action(action_str):
        row, col = (int(x) for x in action_str.split())
        return row, col

    """
    A 'static' method that translates an action into a str representing that action

    It is not necessary to error handle invalid actions here.
    """
    @staticmethod
    def action_to_str(action):
        row, col = action
        return "{} {}".format(row, col)


    @staticmethod
    def action_to_pretty_str(action) :
        """
        A 'static' method that translates an action into a pretty, readable string
        that clearly indicates what the action means.
        It is not necessary to error handle invalid actions here.
        Should be implemented by subclasses.
        """
        return "play at row {}, col {}.".format(action[0], action[1])

    """
    Creates a game state node.
    Takes:

    board_array: a 2-d list (list of lists) representing the board.
    Numbers are either 0 (no piece), 1 or 2.

    parent: the preceding GameStateNode along the path taken to reach the state
            (the initial state's parent should be None)
    path_length: the number of actions taken in the path to reach the state (aka number of plies)
    previous_action: whatever action was last taken to arrive at this state
    current_player: the number of the player whose turn it is to take an action



    Use super().__init__() to call this function in the subclass __init__()
    """
    def __init__(self, board_array,
        parent, path_length, previous_action, current_player) :
        self.board_array = board_array
        super().__init__(parent = parent,
            path_length = path_length,
            previous_action = previous_action,
            current_player = current_player)

    """
    Returns a full feature representation of the environment's current state.
    This should be an immutable type - only primitives, strings, and tuples.
    (no lists or objects).
    If two GameStateNode objects represent the same state,
    get_features() should return the same for both objects.
    Note, however, that two states with identical features
    may have different paths.
    """
    def get_all_features(self) :
        return tuple(tuple(row) for row in self.board_array)

    """
    Returns True if an endgame state.
    Since nonzero numbers are interpreted as "True" in Python,
    we will return the number of the winning player.

    Endgame state if 4 consecutive pieces in a row, col, or diagonal
    that are all the same (1 or 2)
    """

    def endgame_winner(self) :

        # Both player 1 and 2
        for player in TicTacToeGameState.player_numbers:

            # Horizontal wins
            for r in range(TicTacToeGameState.num_rows):
                if all(self.board_array[r][c] == player for c in range(TicTacToeGameState.num_cols)) :
                    return player

            # Vertical wins
            for c in range(TicTacToeGameState.num_cols):
                if all(self.board_array[r][c] == player for r in range(TicTacToeGameState.num_rows)) :
                    return player

            # Diagonal down-right wins
            if all(self.board_array[r][c] == player for r, c in zip(range(TicTacToeGameState.num_rows),range(TicTacToeGameState.num_cols))) :
                return player

            # Diagonal up-right wins
            if all(self.board_array[r][c] == player for r, c in zip(reversed(range(TicTacToeGameState.num_rows)),range(TicTacToeGameState.num_cols))) :
                return player

        # If you get here, no winner yet!
        return 0

    """
    Returns whether or not this state is an endgame (terminal) state.
    """
    def is_endgame_state(self) :
        return (len(self.get_all_actions()) == 0) or (self.endgame_winner() != 0)

    """
    Generate and return an iterable (e.g. a list) of all possible actions.
    Actions may be whatever datatype you wish

    In TicTacToe, actions are a tuple of row and column to fill.
    """
    def get_all_actions(self, custom_move_ordering = False) :
        actions = [(sector // TicTacToeGameState.num_cols, sector % TicTacToeGameState.num_cols) for sector in range(0,TicTacToeGameState.num_cols*TicTacToeGameState.num_rows) ]
        actions = [(r,c) for r,c in actions if self.board_array[r][c] == 0]
        if custom_move_ordering:
            actions = sorted(actions, key = lambda rc: (0 if rc[0] == rc[1] else (abs(rc[0]-rc[1]) % 2) + 1)) # prioritizes center then corners then edges.
        return actions

    """
    Generate and return the next state (GameStateNode object) that would
    result from the given action.
    Does NOT modify this state.

    In TicTacToe, actions are a tuple of row and column to fill.
    """
    def generate_next_state(self, action) :
        row, col = action
        if col not in range(TicTacToeGameState.num_cols) or row not in range(TicTacToeGameState.num_rows) :
            raise IndexError("Invalid position "+str(action)+".")

        if self.board_array[row][col] != 0:
            raise IndexError("Already piece at position "+str(action)+".")

        new_board = deepcopy(self.board_array)
        new_board[row][col] = self.current_player

        return TicTacToeGameState(board_array = new_board,
            parent = self,
            path_length = self.path_length + 1,
            previous_action = action,
            current_player = self.current_player % 2 + 1)


    """
    Return a string representation of the State
    This gets called when str() is used on an Object.
    """
    def __str__(self) :
        ret = ""
        for r, row in enumerate(self.board_array):
            ret += "|".join(TicTacToeGameState.board_str[piece] for piece in row)
            ret += "|"
            ret += str(r)
            ret += "\n"
        for i in range(TicTacToeGameState.num_cols * 2 - 1):
            ret += "-"
        ret += "\n"
        ret += "|".join(str(c) for c in range(TicTacToeGameState.num_cols))
        ret += "\n"

        return ret

    """ Additional TicTacToe specific methods """

    def get_piece_at(self, row, col):
        return self.board_array[row][col]
