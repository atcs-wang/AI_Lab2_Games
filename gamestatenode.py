from copy import deepcopy

"""
This is not meant to be used directly
as an object, but serves as a abstract parent object for various
Adversarial Game Search problem representations.

Your algorithms will use GameStateNode objects, making them generalizable
for all kinds of problems.
"""
class GameStateNode:

    """ A class-level variable, accessible by all subclasses.
    Defaults to (1,2) but could be overrideen by subclasses. """
    player_numbers = (1,2)

    @staticmethod
    def readFromFile(filename):
        """
        A 'static' method that reads data from a text file and returns
        a GameStateNode which is an initial state.

        Should be implemented by subclasses.
        """
        raise NotImplementedError


    @staticmethod
    def defaultInitialState():
        """
        A 'static' method that creates some default
        GameStateNode which is an initial state (e.g. standard blank board).

        Should be implemented by subclasses.
        """
        raise NotImplementedError

    @staticmethod
    def str_to_action(str):
        """
        A 'static' method that translates a string representing an action
        (say, a human user's text input) into the appropriate datatype for that action.
        This should be essentially the inverse of action_to_str
        It is not necessary to error handle invalid actions here.

        Should be implemented by subclasses.
        """
        raise NotImplementedError


    @staticmethod
    def action_to_str(action):
        """
        A 'static' method that translates an action into a str representing that action
        This should be essentially the inverse of str_to_action
        It is not necessary to error handle invalid actions here.

        Should be implemented by subclasses.
        """
        raise NotImplementedError

    @staticmethod
    def action_to_pretty_str(action) :
        """
        A 'static' method that translates an action into a pretty, readable string
        that clearly indicates what the action means.
        It is not necessary to error handle invalid actions here.

        Should be implemented by subclasses.
        """
        raise NotImplementedError


    def __init__(self, parent, path_length, previous_action, current_player) :
        """
        Creates a game state node.
        Takes:
        parent: the preceding GameStateNode along the path taken to reach the state (None if root)
        path_length: the number of actions taken in the path to reach the state (aka level or ply)
        previous_action: whatever action was last taken to arrive at this state (None if root)
        current_player: the number of the player whose turn it is to take an action

        In any subclass of GameStateNode, the __init__() should take any
        additional parameters that are needed to define its state.

        Subclasses should also use super().__init__() to call this function in the subclass __init__()
        """
        self.parent = parent
        self.path_length = path_length
        self.previous_action = previous_action
        self.current_player = current_player

    def __str__(self) :
        """
        Return a string representation of the State
        This gets called when str() is used on an Object.
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def is_endgame_state(self) :
        """
        Returns whether or not this state is an endgame (terminal) state (True/False)
        """
        raise NotImplementedError

    def endgame_winner(self) :
        """
        Returns number of winning player if an endgame state.
        If no winning player, return 0.
        If not an endgame state, behavior is undefined (but returning None is a good idea)

        Since nonzero numbers are interpreted as "True" in Python, and 0 or None as "False",
        this method may be used as a condition check for the endgame if the player_numbers
        are nonzero numbers and ties are not possible.

        In some games there is no clear "winner," such as in abstract game trees.
        An endgame utility function is needed to evaluate the relative
        "goodness" of endgame states.
        """
        raise NotImplementedError



    def get_all_actions(self, custom_move_ordering = False) :
        """
        Generate and return an iterable (e.g. a list) of all possible actions from this state.
        Actions may be whatever datatype you wish.

        If custom_move_ordering is True, optionally orders the moves in a custom way.
        """
        raise NotImplementedError


    def generate_next_state(self, action) :
        """
        Generate and return the next state (GameStateNode object) that would
        result from the given action.
        Does NOT modify this state, but rather creates a new successor.
        """
        raise NotImplementedError


    def generate_next_states_and_actions(self, custom_move_ordering = False) :
        """
        Generate and return an iterable (e.g. a list) of all possible next
        states (GameStateNode objects) and the actions that lead to them.

        This is a list of 2-tuples: [(s1, a1), (s2, a2) ... ]

        If custom_move_ordering is True, optionally orders the moves in a custom way.
        Could also be overridden to customize move-ordering in a different way than
        get_all_actions does.
        """
        actions = self.get_all_actions(custom_move_ordering = custom_move_ordering)
        next_states = [self.generate_next_state(a) for a in actions]
        return list(zip(next_states, actions))

    def get_parent(self) :
        """
        Returns the parent GameStateNode, the preceding GameStateNode
        along the path taken to reach this state.
        (None if the initial state)
        """
        return self.parent

    def get_previous_action(self) :
        """
        Returns the move taken in the parent GameStateNode,
        the preceding GameStateNode, to reach this state.
        (None if the initial state)
        """
        return self.previous_action

    def get_current_player(self) :
        """
        Returns the number of the current player (whose turn it is to act)
        """
        return self.current_player

    def get_path_length(self) :
        """
        Returns the length of the entire path (# moves taken) to reach this state,
        aka the level or ply number of this state.
        """
        return self.path_length

    def get_path(self) :
        """
        Returns a list of GameStateNodes on the path from
        the initial state to this state,
        """
        path = [self]
        s = self.get_parent()
        while s is not None :
            path.append(s)
            s = s.get_parent()
        path.reverse()
        return path

    def clone_as_root(self) :
        """
        Make a clone of this state, but as the root node.
        """
        clone = deepcopy(self)
        clone.parent = None
        clone.path_length = 0
        clone.previous_action = None
        return clone

    def __eq__(self, other):
        """
        This is needed to make GameStateNode comparable and usable in Sets/Dicts
        It compares types and get_all_features().
        You probably want to leave this function alone, but subclasses could override
        this to be more efficient.
        """
        return (isinstance(other, type(self)) and (self.get_all_features() == other.get_all_features()))

    def __hash__(self):
        """
        This is important to make GameStateNode hashable and usable in Sets/Dicts;
        it hashes get_all_features().
        You probably want to leave this function alone, but subclasses could override
        this to be more efficient.
        """
        return hash(self.get_all_features())
