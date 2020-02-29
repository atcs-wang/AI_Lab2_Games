from gamestatenode import GameStateNode
from copy import deepcopy
import re

"""
A GameStateNode representation of the game Connect Four.

You will need to implement some of these methods in Part 2.
"""

class ConnectFourGameState(GameStateNode):

    num_rows = 6  # board height
    num_cols = 7  # board width
    board_str = {0: "_", 1 : "X", 2: "0"}

    @staticmethod
    def readFromFile(filename):
        """
        A 'static' method that reads data from a text file and returns
        a GameStateNode which is an initial state.

        File format:
        Int on first line to indicate whose turn it is (1 or 2)
        6 rows of 7 Space, comma, or pipe delimited pieces
        0 means empty, 1 and 2 are pieces
        """
        with open(filename, 'r') as file:
            board = []
            first_player = int(file.readline())

            for i in range(ConnectFourGameState.num_rows):
                row = [int(x) for x in re.split(",| |\|",file.readline())]
                assert(len(row) == ConnectFourGameState.num_cols)
                assert(all(n in ConnectFourGameState.player_numbers or n == 0 for n in row))
                board.append(row)

        return ConnectFourGameState(
            board_array = board,
            parent = None,
            path_length = 0,
            previous_action = None,
            current_player = first_player)



    @staticmethod
    def defaultInitialState():
        """
        A 'static' method that creates some default
        GameStateNode which is an initial state (e.g. standard blank board).
        """
        return ConnectFourGameState(
            board_array = [[0 for c in range(ConnectFourGameState.num_cols)] for r in range(ConnectFourGameState.num_rows)],
            parent = None,
            path_length = 0,
            previous_action = None,
            current_player = 1)

    @staticmethod
    def str_to_action(action_str):
        """
        A 'static' method that translates a string representing an action
        (say, a human user's text input) into the appropriate datatype for that action.
        This should be essentially the inverse of action_to_str
        It is not necessary to error handle invalid actions here.
        """
        return int(action_str)

    @staticmethod
    def action_to_str(action):
        """
        A 'static' method that translates an action into a str representing that action
        This should be essentially the inverse of str_to_action
        It is not necessary to error handle invalid actions here.
        """
        return str(action)

    def action_to_pretty_str(action) :
        """
        A 'static' method that translates an action into a pretty, readable string
        that clearly indicates what the action means.
        It is not necessary to error handle invalid actions here.
        """
        return "play in column {}".format(action)

    def __init__(self, board_array,
        parent, path_length, previous_action, current_player) :
        """
        Creates a game state node.
        Takes:

        board_array: a 2-d list (list of lists) representing the board.
        Numbers are either 0 (no piece), 1 or 2.

        parent: the preceding GameStateNode along the path taken to reach the state (None if root)
        path_length: the number of actions taken in the path to reach the state (aka level or ply)
        previous_action: whatever action was last taken to arrive at this state (None if root)
        current_player: the number of the player whose turn it is to take an action
        """
        self.board_array = board_array
        super().__init__(parent = parent,
            path_length = path_length,
            previous_action = previous_action,
            current_player = current_player)

    def get_all_features(self) :
        """
        Returns a full feature representation of the environment's current state.
        This should be an immutable type - only primitives, strings, and tuples.
        (no lists or objects) - so that it is hashable.

        If two GameStateNode objects represent the same state,
        get_features() should return the same for both objects.
        NOTE: Different current players means the state is different!!
        The current player might be implicitly encoded in other features,
        but it may not be.

        Note, however, that two states with identical features
        may have had different paths that led to them.
        """
        return tuple(tuple(row) for row in self.board_array)

    def endgame_winner(self) :
        """
        Returns number of winning player if an endgame state.
        If no winning player, return 0.
        If not an endgame state, behavior is undefined (but returning None is a good idea)

        Since nonzero numbers are interpreted as "True" in Python, and 0 or None as "False",
        this method may be used as a condition check for the endgame if the player_numbers
        are nonzero numbers and ties are not possible.

        For ConnectFour, the winner is whoever gets
        4 consecutive pieces in a horizontal, vertical, or diagonal direction
        """
        raise NotImplementedError



    def is_endgame_state(self) :
        """
        Returns whether or not this state is an endgame (terminal) state.
        """
        raise NotImplementedError


    def get_all_actions(self, custom_move_ordering = False):
        """
        Generate and return an iterable (e.g. a list) of all possible actions from this state.
        Actions may be whatever datatype you wish.

        If custom_move_ordering is True, optionally orders the moves in a custom way.

        In ConnectFour, actions are column numbers.
        Default ordering should be left to right columns.
        """
        raise NotImplementedError

    def generate_next_state(self, action) :
        """
        Generate and return the next state (GameStateNode object) that would
        result from the given action.
        Does NOT modify this state, but rather creates a new successor.

        In ConnectFour, actions are column numbers.
        You may find deepcopy to be very useful for making
        full copies of nested lists.
        """
        raise NotImplementedError





    def __str__(self) :
        """
        Return a string representation of the State
        This gets called when str() is used on an Object.
        """
        ret = ""
        for row in self.board_array:
            ret += "|".join(ConnectFourGameState.board_str[piece] for piece in row)
            ret += "\n"
        for i in range(ConnectFourGameState.num_cols * 2 - 1):
            ret += "-"
        ret += "\n"
        ret += "|".join(str(c) for c in range(ConnectFourGameState.num_cols))
        ret += "\n"

        return ret

    """ Additional ConnectFour specific methods """

    def get_column_height(self, col_number):
        """Return the number of pieces in the column; e.g., 0 if the column is empty."""
        height = 0
        for row in reversed(self.board_array) :
            if row[col_number] != 0:
                height += 1
            else :
                break
        return height

    def is_column_full(self, col_number) :
        """Return True if column is full, False otherwise. Just checks the top row for speed."""
        return self.board_array[0][col_number] != 0

    def get_piece_at(self, row, col):
        """
        Number of piece at row, col position. 0 if empty
        """
        return self.board_array[row][col]

    def get_num_chains(self, chain_len, piece):
        """
        Number of chains of length chain_len
        with number piece in all directions
        """
        if chain_len > 1:
                return (self.get_num_chains_hor(chain_len, piece) +
                        self.get_num_chains_ver(chain_len, piece) +
                        self.get_num_chains_diag(chain_len, piece) )
        else : # if len 1, don't repeat count
                return self.get_num_chains_hor(chain_len, piece)
                
    def get_num_chains_hor(self, chain_len, piece):
        """
        Number of chains of length chain_len
        with number piece in horizontal directions
        """
        count = 0
        # Horizontal chains
        # Each leftmost position of a horizontal 4 sequence
        for r in range(ConnectFourGameState.num_rows):
            for c in range(ConnectFourGameState.num_cols - chain_len + 1):
                # check 4 consecutive rightwards all same as piece
                if all(self.board_array[r][c+i] == piece for i in range(0, chain_len)) :
                    count += 1

        return count

    def get_num_chains_ver(self, chain_len, piece):
        """
        Number of chains of length chain_len
        with number piece in vertical direction
        """
        count = 0
        # Vertical chains
        # Each uppermost position of a vertical 4 sequence
        for c in range(ConnectFourGameState.num_cols):
            for r in range(ConnectFourGameState.num_rows - chain_len + 1):
                # check 4 consecutive in diagonal down-right all same as piece
                if all(self.board_array[r+i][c] == piece for i in range(0, chain_len)) :
                    count += 1

        return count

    def get_num_chains_diag(self, chain_len, piece):
        """
        Number of chains of length chain_len
        with number piece in diagonal directions
        """
        count = 0

        # Diagonal down-right chains
        # Each leftmost position of a diagonal down 4 sequence
        for r in range(ConnectFourGameState.num_rows - chain_len + 1):
            for c in range(ConnectFourGameState.num_cols - chain_len + 1):
                # check 4 consecutive in digonal down-right same as leftmost piece
                if all(self.board_array[r+i][c+i] == piece for i in range(0, chain_len)) :
                    count += 1

        # Diagonal up-right chains
        # Each leftmost position of a diagonal up-right 4 sequence
        for r in range(chain_len - 1, ConnectFourGameState.num_rows):
            for c in range(ConnectFourGameState.num_cols - chain_len + 1):
                # check 4 consecutive in diagonal up-right direction all same as piece
                if all(self.board_array[r-i][c+i] == piece for i in range(0, chain_len)) :
                    count += 1

        return count
