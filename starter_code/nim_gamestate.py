from gamestatenode import GameStateNode
from copy import deepcopy
import re
"""
A GameStateNode representation of the game Tic Tac Toe.
"""

class NimGameState(GameStateNode):

    """
    A 'static' method that reads data from a text file and returns
    a GameStateNode which is an initial state.
    """
    @staticmethod
    def readFromFile(filename):
        """ Format:
        First line: int for number of piles, followed by a list of limited numbers of stones you may remove.
            If just the number of piles, any amount is legal.

        Following lines: int for number of stones in the pile
        """
        with open(filename, 'r') as file:
            board = []
            first_line = [int(x) for x in file.readline().split()]
            num_rows = first_line[0]
            move_limits = first_line[1:] if len(first_line) > 1 else None

            for i in range(num_rows):
                board.append(int(file.readline()))

        return NimGameState(
            board_array = board,
            move_limits = move_limits,
            parent = None,
            path_length = 0,
            previous_action = None,
            current_player = 1)




    """
    A 'static' method that creates some default
    GameStateNode which is an initial state (e.g. standard blank board).
    """
    @staticmethod
    def defaultInitialState():
        return NimGameState(
            board_array = [3,4,5],
            move_limits = None,
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
        pile, stones = (int(x) for x in action_str.split())
        return pile, stones

    """
    A 'static' method that translates an action into a str representing that action

    It is not necessary to error handle invalid actions here.
    """
    @staticmethod
    def action_to_str(action):
        pile, stones = action
        return "{} {}".format(pile, stones)


    @staticmethod
    def action_to_pretty_str(action) :
        """
        A 'static' method that translates an action into a pretty, readable string
        that clearly indicates what the action means.
        It is not necessary to error handle invalid actions here.
        Should be implemented by subclasses.
        """
        return "take {} stones from pile {}".format(action[1], action[0])

    """
    Creates a game state node.
    Takes:

    board_array: a list of ints representing the piles and how many stones are in them.
    move_limits: a list of legal # of stones you can take, or None if no limitations

    parent: the preceding GameStateNode along the path taken to reach the state
            (the initial state's parent should be None)
    path_length: the number of actions taken in the path to reach the state (aka number of plies)
    previous_action: whatever action was last taken to arrive at this state
    current_player: the number of the player whose turn it is to take an action



    Use super().__init__() to call this function in the subclass __init__()
    """
    def __init__(self, board_array, move_limits,
        parent, path_length, previous_action, current_player) :
        self.board_array = board_array
        self.move_limits = move_limits
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
        return tuple(self.board_array), self.current_player

    """
    Returns True if an endgame state.
    Since nonzero numbers are interpreted as "True" in Python,
    we will return the number of the winning player.

    Endgame state if 4 consecutive pieces in a row, col, or diagonal
    that are all the same (1 or 2)
    """

    def endgame_winner(self) :
        return self.current_player

    """
    Returns whether or not this state is an endgame (terminal) state.
    """
    def is_endgame_state(self) :
        return all(pile == 0 for pile in self.board_array)

    """
    Generate and return an iterable (e.g. a list) of all possible actions.
    Actions may be whatever datatype you wish

    In TicTacToe, actions are a tuple of row and column to fill.
    """
    def get_all_actions(self, custom_move_ordering = False) :
        actions = []
        for pile, max_stones in enumerate(self.board_array):
            for rem_stones in range(1,max_stones+1):
                if self.move_limits == None or rem_stones in self.move_limits:
                    actions.append((pile, rem_stones))

        return sorted(actions, key = lambda a: a[1], reverse = True) if custom_move_ordering  else actions

    """
    Generate and return the next state (GameStateNode object) that would
    result from the given action.
    Does NOT modify this state.

    In Nim, actions are a tuple of the pile number (0 to num piles - 1) and how many stones to take.
    """
    def generate_next_state(self, action) :
        pile, rem_stones = action
        # if pile not in range(len(self.board_array)) :
        #     raise IndexError("Invalid pile {}".format(pile))
        #
        # if rem_stones not in range(1, self.board_array[pile] + 1):
        #     raise IndexError("Cant remove {} from pile {}.".format(rem_stones, pile))

        new_board = deepcopy(self.board_array)
        new_board[pile] -= rem_stones

        return NimGameState(board_array = new_board,
            move_limits = self.move_limits,
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
        for pile, stones in enumerate(self.board_array):
            ret += str(pile) + "|"
            ret += "".join("*" for stone in range(stones))
            ret += "\n"
        ret += "\n"

        return ret

    """ Additional Nim specific methods """

    def get_stones_in_pile(self, pile):
        return self.board_array[pile]

    def get_num_piles(self):
        return len(self.board_array)
