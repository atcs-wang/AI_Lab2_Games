from gamestatenode import GameStateNode
from copy import deepcopy
import re

"""
A GameStateNode representation of the game Connect Four.
"""

class ConnectFourGameState(GameStateNode):

    num_rows = 6  # board height
    num_cols = 7  # board width
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



    """
    A 'static' method that creates some default
    GameStateNode which is an initial state (e.g. standard blank board).
    """
    @staticmethod
    def defaultInitialState():
        return ConnectFourGameState(
            board_array = [[0 for c in range(ConnectFourGameState.num_cols)] for r in range(ConnectFourGameState.num_rows)],
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
        return int(action_str)

    """
    A 'static' method that translates an action into a str representing that action.
    It is not necessary to error handle invalid actions here.
    """
    @staticmethod
    def action_to_str(action):
        return str(action)

    """
    A 'static' method that translates an action into a str representing that action

    Returns a pretty, readable string that more clearly indicates what the action
    means.
    It is not necessary to error handle invalid actions here.
    Should be implemented by subclasses.
    """
    def action_to_pretty_str(action) :
        return "play in column {}".format(action)

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
    Returns number of winning player if an endgame state.
    If no winning player, return 0.
    If not an endgame state,
    behavior is undefined (but returning 0 or None is a good idea)

    For ConnectFour, the winner is whoever gets
    4 consecutive pieces in a horizontal, vertical, or diagonal direction
    """
    def endgame_winner(self) :
        for player in ConnectFourGameState.player_numbers:
            if self.get_num_chains(4, player):
                return player
        return 0

    # def endgame_winner(self) :
    #     win_len = 4
    #     # Horizontal wins
    #     # Each leftmost position of a horizontal 4 sequence
    #     for r in range(ConnectFourGameState.num_rows):
    #         for c in range(ConnectFourGameState.num_cols - win_len + 1):
    #             first_piece = self.board_array[r][c]
    #             # if empty, move on
    #             if first_piece == 0:
    #                 continue
    #             # check next 3 to the right same as leftmost piece
    #             if all(self.board_array[r][c+i] == first_piece for i in range(1, win_len)) :
    #                 return first_piece

    #     # Vertical wins
    #     # Each uppermost position of a vertical 4 sequence
    #     for c in range(ConnectFourGameState.num_cols):
    #         for r in range(ConnectFourGameState.num_rows - win_len + 1):
    #             first_piece = self.board_array[r][c]
    #             # if empty, move on
    #             if first_piece == 0:
    #                 continue
    #             # check next 3 downwards same as uppermost piece
    #             if all(self.board_array[r+i][c] == first_piece for i in range(1, win_len)) :
    #                 return first_piece

    #     # Diagonal down-right wins
    #     # Each leftmost position of a diagonal down 4 sequence
    #     for r in range(ConnectFourGameState.num_rows - win_len + 1):
    #         for c in range(ConnectFourGameState.num_cols - win_len + 1):
    #             first_piece = self.board_array[r][c]
    #             # if empty, move on
    #             if first_piece == 0:
    #                 continue
    #             # check next 3 in digonal down-right same as leftmost piece
    #             if all(self.board_array[r+i][c+i] == first_piece for i in range(1, win_len)) :
    #                 return first_piece

    #     # Diagonal up wins
    #     # Each leftmost position of a diagonal up-right 4 sequence
    #     for r in range(win_len - 1, ConnectFourGameState.num_rows):
    #         for c in range(ConnectFourGameState.num_cols - win_len + 1):
    #             first_piece = self.board_array[r][c]
    #             # if empty, move on
    #             if first_piece == 0:
    #                 continue
    #             # check next 3 in diagonal up-right direction same as leftmost piece
    #             if all(self.board_array[r-i][c+i] == first_piece for i in range(1, win_len)) :
    #                 return first_piece

    #     # If you get here, no winner yet!
    #     return 0



    """
    Returns whether or not this state is an endgame (terminal) state.
    """
    def is_endgame_state(self) :
        return len(self.get_all_actions()) == 0 or self.endgame_winner() != 0



    """
    Generate and return an iterable (e.g. a list) of all possible actions.
    Actions may be whatever datatype you wish

    In ConnectFour, actions are column numbers.
    """

    center_column = num_rows // 2
    def get_all_actions(self, custom_move_ordering = False):
        actions = [col for col in range(ConnectFourGameState.num_cols)
                    if not self.is_column_full(col) ]
        return sorted(actions, key = lambda col : abs( ConnectFourGameState.center_column - col)) if custom_move_ordering else actions


    """
    Generate and return the next state (GameStateNode object) that would
    result from the given action.
    Does NOT modify this state.

    In ConnectFour, actions are column numbers.
    """
    def generate_next_state(self, action) :
        if action not in range(ConnectFourGameState.num_cols) or self.is_column_full(action) :
            raise IndexError("Can't add piece to column "+str(action)+".")

        r = ConnectFourGameState.num_rows - self.get_column_height(action) - 1

        new_board = deepcopy(self.board_array)
        new_board[r][action] = self.current_player

        # ( self.board_array[:r]                        # using slicing to create
        #             + ( self.board_array[r][:action]        # a new 2-d tuple
        #                 + (self.current_player,)                # with the new piece
        #                 + self.board_array[r][action + 1:], )
        #             + self.board_array[r + 1:] )

        return ConnectFourGameState(board_array = new_board,
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

    """Return the number of pieces in the column; e.g., 0 if the column is empty."""
    def get_column_height(self, col_number):
        height = 0
        for row in reversed(self.board_array) :
            if row[col_number] != 0:
                height += 1
            else :
                break
        return height

    """Return True if column is full, False otherwise. Just checks the top row for speed."""
    def is_column_full(self, col_number) :
        return self.board_array[0][col_number] != 0

    def get_piece_at(self, row, col):
        return self.board_array[row][col]

    def get_num_chains(self, chain_len, piece):
        if chain_len > 1:
            return (self.get_num_chains_hor(chain_len, piece) +
                self.get_num_chains_ver(chain_len, piece) +
                self.get_num_chains_diag(chain_len, piece) )
        else : # if len 1, don't repeat count
                return self.get_num_chains_hor(chain_len, piece)
                
    def get_num_chains_hor(self, chain_len, piece):
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
