from gamestatenode import GameStateNode
from copy import deepcopy

FLOOR = '.'
WALL = '#'
CLEANED = (None,'-','~') # If cleaned by player 1, '-'. If cleaned by player 2 '~'


class RoombaRaceGameState(GameStateNode):

    # Class-level variables representing all the directions
    # the position can move.
    STR_TO_ACTIONS = { "N": (-1,0), "E": (0,1), "S": (1,0), "W": (0, -1)}
    NEIGHBORING_STEPS = {(-1,0): "North", (0,1): "East", (1,0): "South", (0, -1): "West"}

    """
    A 'static' method that reads mazes from text files and returns
    a RoombaRaceGameState which is an initial state.
    """
    def readFromFile(filename):
        with open(filename, 'r') as file:
            grid = []
            max_r, max_c = [int(x) for x in file.readline().split()]
            init_r_1, init_c_1 = [int(x) for x in file.readline().split()]
            init_r_2, init_c_2 = [int(x) for x in file.readline().split()]
            for i in range(max_r):
                row = list(file.readline().strip()) # or file.readline().split()
                assert (len(row) == max_c)
                #
                grid.append(row) # list -> tuple makes it immutable, needed for hashing
            # grid is a list of lists - a 2d grid!

            return RoombaRaceGameState(positions = [(init_r_1, init_c_1),(init_r_2, init_c_2)],
                                grid = grid,
                                parent = None,
                                path_length = 0,
                                previous_action = None,
                                current_player = 1)
    """
    A 'static' method that creates some default
    GameStateNode which is an initial state (e.g. standard blank board).

    Should be implemented by subclasses.
     """
    @staticmethod
    def defaultInitialState():

        return RoombaRaceGameState(positions = [(2, 1),(2, 5)],
                            grid =  [[ FLOOR for c in range(7)] for r in range(5)],
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
        return RoombaRaceGameState.STR_TO_ACTIONS[action_str.upper()]

    """
    A 'static' method that translates an action into a str representing that action.
    It is not necessary to error handle invalid actions here.
    """
    @staticmethod
    def action_to_str(action):
        return RoombaRaceGameState.NEIGHBORING_STEPS[action][0] # Return first character of North/West/East/South

    @staticmethod
    def action_to_pretty_str(action) :
        """
        A 'static' method that translates an action into a pretty, readable string
        that clearly indicates what the action means.
        It is not necessary to error handle invalid actions here.
        Should be implemented by subclasses.
        """
        return "move {}.".format(RoombaRaceGameState.NEIGHBORING_STEPS[action])


    """
    Creates a RoombaRaceGameState node.
    Takes:
    position: 2-tuple of 2-tuples: current coordinates of player 1 and 2
    grid: 2-d grid representing features of the maze.
    previous_action: string describing the last action taken

    parent: the preceding GameStateNode along the path taken to reach the state
            (the initial state's parent should be None)
    path_length: the number of actions taken in the path to reach the state (aka number of plies)
    previous_action: whatever action was last taken to arrive at this state
    current_player: the number of the player whose turn it is to take an action

    In any subclass of GameStateNode, the __init__() should take and store
    additional parameters that define its state.

    Use super().__init__() to call this function in the subclass __init__()
    """
    def __init__(self, positions, grid,  parent, path_length, previous_action, current_player):
        super().__init__(parent, path_length, previous_action, current_player)

        self.positions = positions
        self.grid = grid


    """
    Returns a full feature representation of the environment's current state.
    This should be an immutable type - only primitives, strings, and tuples.
    (no lists or objects).
    If two GameStateNode objects represent the same state,
    get_features() should return the same for both objects.
    Note, however, that two states with identical features
    may have different paths.
    """
    # Override
    def get_all_features(self) :
        return (tuple(tuple(pos) for pos in self.positions), tuple(tuple(row) for row in self.grid) )


    """
    Returns number of winning player if an endgame state.
    If no winning player, return 0.
    If not an endgame state, behavior is undefined (but returning None is a good idea)

    Since nonzero numbers are interpreted as "True" in Python, and 0 or None as "False",
    this method may be used as a condition check for the endgame if the player_numbers
    are nonzero numbers and ties are not possible.

    In some games, there is no clear "winner," such as in abstract game trees.
    Some kind of endgame utility function is needed to evaluate the relative
    "goodness" of endgame states.
    """
    def endgame_winner(self) :
        return self.current_player % 2 + 1

    """
    Returns whether or not this state is an endgame (terminal) state (True/False)
    """
    def is_endgame_state(self) :
        return len(self.get_all_actions()) == 0

    """
    Return a string representation of the State
    This gets called when str() is used on an Object.
    """
    # Override
    def __str__(self):
        s = "\n".join(["".join(row) for row in self.grid])
        for p in RoombaRaceGameState.player_numbers:
            r,c = self.get_position(p)
            str_pos =  r * (self.get_width()+1) + c
            s = s[:str_pos] + str(p) + s[str_pos+1:] + "\n"
        return s

    """
    Generate and return an iterable (e.g. a list) of all possible actions.
    Actions may be whatever datatype you wish

    In Roomba Race, actions are a tuple of row and column movement.
    """
    def get_all_actions(self, custom_move_ordering = False) :
        actions = []
        for dr, dc in RoombaRaceGameState.NEIGHBORING_STEPS:
            my_r, my_c = self.get_position(self.current_player)
            new_r, new_c = my_r + dr, my_c + dc
            # Don't use any out-of-bounds moves
            if (new_r < 0) or (new_c < 0) or (new_r >= self.get_height()) or (new_c >= self.get_width()):
                continue
            # Only add moves to unvisited floor
            if self.grid[new_r][new_c] != FLOOR:
                continue
            if (new_r, new_c) == self.get_position(self.current_player % 2 + 1) :
                continue
            actions.append((dr,dc))
        return actions

    """
    Generate and return the next state (GameStateNode object) that would
    result from the given action.
    Does NOT modify this state.
    """
    def generate_next_state(self, action) :
        new_grid = deepcopy(self.grid)

        dr, dc = action
        my_r, my_c = self.get_position(self.current_player)
        new_r, new_c = my_r + dr, my_c + dc

        new_grid[my_r][my_c] = CLEANED[self.current_player]
        new_positions = deepcopy(self.positions)
        new_positions[self.current_player-1] = (new_r, new_c)
        return RoombaRaceGameState(
                        positions = new_positions,
                        grid = new_grid,
                        parent = self,
                        path_length = self.path_length + 1,
                        previous_action = action,
                        current_player = self.current_player % 2 + 1
                        )

    """ Additional accessor methods used the GUI """

    """
    Returns the width (number of cols) of the maze
    """
    def get_width(self):
        return len(self.grid[0])

    """
    Returns the height (number of rows) of the maze
    """
    def get_height(self):
        return len(self.grid)

    """
    Returns a 2d-list grid of the maze.
    """
    def get_grid(self) :
        return self.grid
    """
    Returns a 2-tuple of a player roomba's position (row, col) in the maze
    """
    def get_position(self, player):
        return self.positions[player-1]

    """
    Returns a 2d-list grid of the maze.
    """
    def get_grid(self) :
        return self.grid
