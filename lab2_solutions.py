# Lab 2: Games (Connect-4, Roomba Race)
# Name(s): Mr. Wang
# Email(s): matwan@bergen.org
import random # choice, shuffle methods
import math # optional, remove later
from time import time
from collections import defaultdict # optional, remove later
from gamestatenode import GameStateNode
from lab2_util_eval import always_zero

INF = float('inf')
# optional flags for visualization customization
VIS_ENDGAME = True
VIS_CUTOFF = True
VIS_PRE = False
VIS_MID = False
VIS_POST = True

"""
HELPFUL NOTES:

CODE REPETITION:
Every algorithm in this lab is very similar to the last.
As with the first lab, you'll likely do a lot of copy and paste, with small
(but crucial!) updates between algorithms. This is okay, but this DOES mean you'll
want to be SURE that your earlier algorithms are SOLID before moving forward
(and to apply any later corrections to all your earlier work).

RECURSION and INNER FUNCTIONS:
Every one of the algorithms in this lab use recursion.
You may wish to write "helper" inner functions for the recursion, since
the parameters of the algorithms may not be changed, and it is cumbersome
to pass all the parameters every time you make a recursive call.
Any parameters or variables declared in the outer function before the inner function
definition are accessible by inner functions.
So you can keep the recursive parameters minimal this way.
See RandChoice for an example of this.

LAMBDA:

lambda is a very useful keyword in java for making short, anonymous functions that can be
passed as parameters
Template:
    lambda param1, param2, ... : computedValueToBeReturned
Examples:
    lambda x : x * x        #square function
    lambda l : l[0] + l[-1] #sum of first and last items in a list
    lambda : False          # takes no params, returns false always
    lambda *args, **kw : other_fn() # takes any number of params, calls & returns from other_fn


OTHER:

Some useful built-in python methods:
    # any(list-like) - returns if at least one True
    # all(list-like) - returns if all are True
    # sum(list-like) - returns sum of all (??)

    random.shuffle(list) - shuffles a list IN-PLACE (returns None)
    sorted(list, [key= sort_by_fn, reversed = bool]) - returns a sorted (smallest to greatest)
                copy of the list. Can be sorted by an optional key function, and reversed.

"""

"""
Provided below is a simple search algorithm RandChoice which can serve as a model and starting point
for your algorithms.

It takes similar parameters and returns the same 4-tuple as the algorithms you must write in Parts 1 and 2.
"""

def RandChoice(initial_state,
    util_fn,                        # Endgame Utility Evaluation function. Takes a state and the maximizing player as parameters
    eval_fn = always_zero,          # Cutoff Heuristic Evaluation function. Takes a state and the maximizing player as parameters
    cutoff = INF,                   # Cutoff depth
        # state_callback_fn is a callback function for communicating with a GUI.
        # Pass it a state and its value (None if not calculated) to have it displayed.
        # If it returns True, terminate
    state_callback_fn = lambda state, state_value : False,
        # Some things to keep count of.
        # Increment counter['num_endgame_evals'] whenever util_fn is called.
        # Increment counter['num_heuristic_evals'] whenever eval_fn is called.
    counter = {'num_nodes_seen':0,'num_endgame_evals':0, 'num_heuristic_evals':0}, # A counter for tracking stats
    random_move_order = False,     # If true, consider moves in random order [IGNORED]
    transposition_table = False    # If true, use a transposition table. [IGNORED]
    ):

    """
    Searches down a single path of the game tree.
    Chooses randomly for both players, returning
    the action chosen, the final "expected" state, the "expected" utility and
    whether or not the search was terminated early by the state_callback_fn
    """
    # A recursive helper function.
    # Has access to all the parameters of the outer function,
    # avoids excessive passing of unchanging parameters
    def RandChoice_helper(state):
        counter['num_nodes_seen'] += 1
        # Base case - endgame leaf node:
        if state.is_endgame_state() :
            endgame_util = util_fn(state, initial_state.get_current_player())
            counter['num_endgame_evals'] += 1
            # Visualize leaf node with utility, check for early termination signal
            terminated = state_callback_fn(state, endgame_util) if VIS_ENDGAME else False

            return None, state, endgame_util, terminated

        # Early cutoff evaluation:
        if state.get_path_length() - initial_state.get_path_length() >= cutoff:

            heuristic_eval = eval_fn(state, initial_state.get_current_player())
            counter['num_heuristic_evals'] += 1

            # Visualize leaf node with evaluation, check for early termination signal
            terminated = state_callback_fn(state, heuristic_eval) if VIS_CUTOFF else False

            return None, state, heuristic_eval, terminated


        # Visualize on downwards traversal.
        state_callback_fn(state,None) if VIS_PRE else False

        # Recursive step - pick a valid action at random
        action = random.choice(state.get_all_actions())

        # What child state results from that action?
        child_state = state.generate_next_state(action)

        # Search from the child_state
        # Would normally do early termination check, but already finished!
        child_action, leaf_node, exp_util, terminated = RandChoice_helper(child_state)

        # Visualize on upwards traversal, now with updated utility!
        state_callback_fn(state, exp_util) if VIS_POST else False


        return action, leaf_node, exp_util, terminated
        ### End of recursive helper function ###

    # Simply call the helper function on the initial_state.
    return RandChoice_helper(initial_state)
    #     return (None, None, 0, False)


    # return a tuple of the following:
    # (best action to take from initial_state, leaf statenode of best/expected path, expected utility of best action (i.e. initial_state))


### Part 1: Searching the game tree  #################################################

"""
Each algorithm in Part 1 and Part 2 works slightly differently, but all
has the same parameters and return the same things:

initial_state : GameStateNode, current state of the game. Algorithm should take the
    perspective of the player whose turn it is currently is. (i.e. That player is the maximizer)

    Use the GameStateNode API and NOT any properties or methods
    of any particular subclass of GameStateNode (i.e. ConnectFourGameState).
    By doing so, the algorithms can be applied to any subclass of GameStateNode, not just one.

util_fn: Endgame utility evaluation function. Use to calculate the utility of any endgame state.
Takes 2 parameters:
    1) a state
    2) the player number of the maximizing player.

eval_fn: Heuristic evaluation function. Use to calculate the estimated utility of any non-endgame state.
Also takes 2 parameters:
    1) a state
    2) the player number of the maximizing player.

cutoff: Maximum depth to search to in the game tree.

state_callback_fn: GUI callback function. It takes two parameters:
    1) a state to visualize
    2) the expected utility of that state.

    You must use state_callback_fn whenever the state's value is *finalized*, but you
    may also call whenever you want to visualize other parts of the tree traversal.

    You must also heed the termination signal being returned from state_callback_fn
    and terminate search as soon as possible.  If possible some result should still
    be returned, though those results will be (most likely) incorrect.

counter: A dict with stats to maintain count of. Count the number of nodes seen (visited),
    and the number of endgame/heuristic evaluations performed (calls to util_fn and eval_fn).

random_move_order: A True/False flag indicating whether moves should be
    considered in random order or default order.

transposition_table: A True/False flag indicating whether or not a transposition
    table should be used. For Part 1 you may ignore this parameter, but Part 2
    requires that each algorithm address this. You may, of course, implement it early
    for Part 1 submission, though it will not be tested.

Returns the following 4-tuple.
    1) The "best" action to take from initial_state.
    2) State at the end of the expected path in the search tree. (GameStateNode)
            (For Expectimax, however, this should always be None)
    3) Expected Utility of the action. (float)
    4) Whether or not terminated search early from the state_callback_fn (True/False)
"""

def MaximizingDFS(initial_state,
    util_fn,
    eval_fn = always_zero,
    cutoff = INF,
    state_callback_fn = lambda state, state_value : False, # A callback function for the GUI. If it returns True, terminate
    counter = {'num_nodes_seen':0,'num_endgame_evals':0, 'num_heuristic_evals':0}, # A counter for tracking stats,
    random_move_order = False,     # If true, consider moves in random order
    transposition_table = False    # If true, use a transposition table. [IGNORE until Part 2]
    ):
    """
    Searches down ALL paths of the game tree, performing Maximizing Depth First Search
    Both players are modeled as maximizing the utility for the first player.
    This could be interpreted as an optimistic model of your opponents behavior.
    """
    if transposition_table:
        t_table = {}

    maximizer = initial_state.get_current_player()

    # A recursive helper function.
    # Has access to all the parameters of the outer function,
    # avoids excessive passing of unchanging parameters
    def MaximizingDFS_helper(state):
        counter['num_nodes_seen'] += 1
        if transposition_table and state in t_table:
            best_leaf_node, best_exp_util = t_table[state]
            terminated = state_callback_fn(state, best_exp_util) if VIS_POST else False
            return None, None, best_exp_util, terminated #could return best_leaf_node but might be funky?

        # Base case - endgame leaf node:
        if state.is_endgame_state() :
            counter['num_endgame_evals'] += 1
            endgame_util = util_fn(state, maximizer)
            # Visualize leaf node with utility, check for early termination signal
            if transposition_table:
                t_table[state] =  state, endgame_util
            terminated = state_callback_fn(state, endgame_util) if VIS_ENDGAME else False
            return None, state, endgame_util, terminated

        # Early cutoff evaluation:
        if state.get_path_length() - initial_state.get_path_length() >= cutoff:
            counter['num_heuristic_evals'] += 1
            heuristic_eval = eval_fn(state, maximizer)
            if transposition_table:
                t_table[state] =  state, heuristic_eval

            # Visualize leaf node with evaluation, check for early termination signal
            terminated = state_callback_fn(state, heuristic_eval) if VIS_CUTOFF else False

            return None, state, heuristic_eval, terminated

        # Recursive step - maximize expected utility amongst actions
        # This is expanding!
        maximize = (maximizer == state.get_current_player())

        # Visualize on downwards traversal.
        state_callback_fn(state,None) if VIS_PRE else False

        best_action , best_leaf_node, best_exp_util, terminated = None, None, None, False
        all_actions = state.get_all_actions()
        if random_move_order:
            random.shuffle(all_actions)
        for action in all_actions:
            # What child state results from that action?
            child_state = state.generate_next_state(action)
            # Recursively Search from the child_state
            child_action, leaf_node, exp_util, terminated = MaximizingDFS_helper(child_state)

            if best_exp_util == None or (exp_util > best_exp_util):
                best_action , best_leaf_node, best_exp_util = action, leaf_node, exp_util,

            # Visualize mid-expansion, now with partial updated utility!
            if VIS_MID:
                terminated = state_callback_fn(state, best_exp_util)
            if terminated : # early termination - dont go down more branches
                break

        # Visualize on upwards traversal, now with fully updated utility!
        if transposition_table:
            t_table[state] = best_leaf_node, best_exp_util
        terminated = state_callback_fn(state, best_exp_util) if VIS_POST else False

        return best_action , best_leaf_node, best_exp_util, terminated
        ### End of recursive helper function ###


    # Simply call the helper function on the initial_state.
    return MaximizingDFS_helper(initial_state)
    #     return (None, None, 0, False)
    return None, None, 0, False

def MinimaxSearch(initial_state,
    util_fn,
    eval_fn = always_zero,
    cutoff = INF,
    state_callback_fn = lambda state, state_value : False, # A callback function for the GUI. If it returns True, terminate
    counter = {'num_nodes_seen':0,'num_endgame_evals':0, 'num_heuristic_evals':0}, # A counter for tracking stats
    random_move_order = False,     # If true, consider moves in random order
    transposition_table = False    # If true, use a transposition table. [IGNORE until Part 2]
    ):
    """
    Searches down ALL paths of the game tree, performing Minimax.
    Both players are modeled as either maximizing the utility for themselves,
    or maximizing / minimizing the first player (maximizer)'s utility.
    This could be interpreted as a pessimistic model of your opponents behavior.
    """
    if transposition_table:
        t_table = {}
    maximizer = initial_state.get_current_player()

    # A recursive helper function.
    # Has access to all the parameters of the outer function,
    # avoids excessive passing of unchanging parameters
    def MinimaxSearch_helper(state):
        counter['num_nodes_seen'] += 1
        if transposition_table and state in t_table:
            best_leaf_node, best_exp_util = t_table[state]
            terminated = state_callback_fn(state, best_exp_util) if VIS_POST else False
            return None, None, best_exp_util, terminated #could return best_leaf_node but might be funky?
        is_maximizer = state.get_current_player() == maximizer

        # Base case - endgame leaf node:
        if state.is_endgame_state() :
            counter['num_endgame_evals'] += 1
            endgame_util = util_fn(state, maximizer)
            if transposition_table:
                t_table[state] =  state, endgame_util
            # Visualize leaf node with utility, check for early termination signal
            terminated = state_callback_fn(state, endgame_util) if VIS_ENDGAME else False
            return None, state, endgame_util, terminated

        # Early cutoff evaluation:
        if state.get_path_length() - initial_state.get_path_length() >= cutoff:
            counter['num_heuristic_evals'] += 1
            heuristic_eval = eval_fn(state, maximizer)
            if transposition_table:
                t_table[state] =  state, heuristic_eval
            # Visualize leaf node with evaluation, check for early termination signal
            terminated = state_callback_fn(state, heuristic_eval) if VIS_CUTOFF else False

            return None, state, heuristic_eval, terminated

        # Recursive step - maximize expected utility amongst actions
        # This is expanding!
        maximize = (maximizer == state.get_current_player())
        # Visualize on downwards traversal.
        state_callback_fn(state,None) if VIS_PRE else False

        best_action , best_leaf_node, best_exp_util, terminated = None, None, None, False
        all_actions = state.get_all_actions()
        if random_move_order:
            random.shuffle(all_actions)
        for action in all_actions:
            # What child state results from that action?
            child_state = state.generate_next_state(action)
            # Recursively Search from the child_state
            child_action, leaf_node, exp_util, terminated = MinimaxSearch_helper(child_state)

            if best_exp_util == None or (exp_util > best_exp_util if maximize else exp_util < best_exp_util):
                best_action , best_leaf_node, best_exp_util = action, leaf_node, exp_util,

            # Visualize mid-expansion, now with partial updated utility!
            if VIS_MID:
                terminated = state_callback_fn(state, best_exp_util)
            if terminated : # early termination - dont go down more branches
                break

        # Visualize on upwards traversal, now with fully updated utility!
        if transposition_table:
            t_table[state] = best_leaf_node, best_exp_util
        terminated = state_callback_fn(state, best_exp_util) if VIS_POST else False
        return best_action, best_leaf_node, best_exp_util, terminated #could return best_leaf_node but might be funky?        ### End of recursive helper function ###

    # Simply call the helper function on the initial_state.
    return MinimaxSearch_helper(initial_state)


def ExpectimaxSearch(initial_state,
    util_fn,
    eval_fn = always_zero,
    cutoff = INF,
    state_callback_fn = lambda state, state_value : False, # A callback function for the GUI. If it returns True, terminate
    counter = {'num_nodes_seen':0,'num_endgame_evals':0, 'num_heuristic_evals':0}, # A counter for tracking stats
    random_move_order = False,     # If true, consider moves in random order
    transposition_table = False    # If true, use a transposition table. [IGNORE until Part 2]
    ):
    """
    Searches down ALL paths of the game tree, performing Expectimax.
    The initial player is modeled as maximizing the utility for themselves,
    while the other player is modeled as equally likely to choose any action.
    The value of such states are calculated by an average of the possible
    results.
    This could be interpreted as a cautiously optimistic model of your opponents behavior.

    Since there is no single leaf node that represents the expected outcome,
    return None for the second return value.
    """
    if transposition_table:
        t_table = {}
    maximizer = initial_state.get_current_player()

    # A recursive helper function.
    # Has access to all the parameters of the outer function,
    # avoids excessive passing of unchanging parameters
    def Expectimax_helper(state):
        counter['num_nodes_seen'] += 1
        if transposition_table and state in t_table:
            best_leaf_node, best_exp_util = t_table[state]
            terminated = state_callback_fn(state, best_exp_util) if VIS_POST else False
            return None, None, best_exp_util, terminated #could return best_leaf_node but might be funky?

        is_maximizer = state.get_current_player() == maximizer

        # Base case - endgame leaf node:
        if state.is_endgame_state() :
            counter['num_endgame_evals'] += 1
            endgame_util = util_fn(state, maximizer)
            if transposition_table:
                t_table[state] =  state, endgame_util
            # Visualize leaf node with utility, check for early termination signal
            terminated = state_callback_fn(state, endgame_util) if VIS_ENDGAME else False
            return None, state, endgame_util, terminated

        # Early cutoff evaluation:
        if state.get_path_length() - initial_state.get_path_length() >= cutoff:
            counter['num_heuristic_evals'] += 1
            heuristic_eval = eval_fn(state, maximizer)
            if transposition_table:
                t_table[state] =  state, heuristic_eval
            # Visualize leaf node with evaluation, check for early termination signal
            terminated = state_callback_fn(state, heuristic_eval) if VIS_CUTOFF else False

            return None, state, heuristic_eval, terminated

        # Recursive step - maximize expected utility amongst actions
        # This is expanding!
        maximize = (maximizer == state.get_current_player())
        # Visualize on downwards traversal.
        state_callback_fn(state,None) if VIS_PRE else False

        best_action , best_leaf_node, best_exp_util, terminated = None, None, None, False


        if maximize:
            all_actions = state.get_all_actions()
            if random_move_order:
                random.shuffle(all_actions)
            for action in all_actions:
                # What child state results from that action?
                child_state = state.generate_next_state(action)
                # Recursively Search from the child_state
                child_action, leaf_node, exp_util, terminated = Expectimax_helper(child_state)

                if best_exp_util == None or (exp_util > best_exp_util):
                    best_action , best_leaf_node, best_exp_util = action, leaf_node, exp_util,

                # Visualize mid-expansion, now with partial updated utility!
                if VIS_MID:
                    terminated = state_callback_fn(state, best_exp_util)
                if terminated : # early termination - dont go down more branches
                    break

        else: #uniform average instead of min
            # we'll return None for best_leaf_node and best_action, since we're not concerned about that.
            sum_util  = 0
            all_actions = state.get_all_actions()
            for action in all_actions:
                # What child state results from that action?
                child_state = state.generate_next_state(action)
                # Recursively Search from the child_state
                _, _, exp_util, terminated = Expectimax_helper(child_state)
                sum_util += exp_util

                # Visualize mid-expansion, now with partial updated utility!
                if VIS_MID:
                    terminated = state_callback_fn(state, best_exp_util)
                if terminated : # early termination - dont go down more branches
                    break

            # best_exp_util is really average expected utility
            best_exp_util = sum_util / len(all_actions)

        # Visualize on upwards traversal, now with fully updated utility!
        if transposition_table:
            t_table[state] = best_leaf_node, best_exp_util
        terminated = state_callback_fn(state, best_exp_util) if VIS_POST else False
        return best_action , None, best_exp_util, terminated
        ### End of recursive helper function ###

    # Simply call the helper function on the initial_state.
    return Expectimax_helper(initial_state)
    #     return (None, None, 0, False)

### Part 2: Pruning the tree - Transposition Tables, Alpha-Beta Pruning, Move ordering #################################################

"""
    Task #1) Go back and add a transposition table to MaximizingDFS, MinimaxSearch,
    and ExpectimaxSearch. You should only use it if the transposition_table parameter
    is True. Then test it out and see how many fewer evaluations are done!

Background:
So far, all our algorithms require searching every branch of the game tree to
determine a state's value and policy. We've used pre-existing game-specific
knowledge to implement a cutoff which helps when we can't afford to search all
the way to the root of the tree.

But there are many clever techniques to use knowledge gained *during* the search
process to avoid searching many branches of the tree that are unecessary.
This is called "pruning" and is an enormous area of focus in game-playing AI.

The first pruning technique we will apply is a "transposition table."
It is essentially a lookup table that stores old results from states
already searched; if that state is encountered again while searching a different
part of the tree, we can avoid re-searching that entire subtree.
This is very similar to the idea of extended state filters from goal-based search!

This technique can be very useful in certain kinds of games where identical states
can be reached multiple ways. TicTacToe, Nim, and ConnectFour all have many such
states. However, Roomba Race does not - so using a transposition table there will
not help very much or at all.

Transposition tables have a major downside - they may be memory-expensive because there
may be many, many states to remember! In practice, transposition tables are usually size
limited with some replacement scheme to estimate which stored states are least useful and
safe to replace. However, you do not need to implement any such size
limitation or replacement scheme in this lab.

NOTE:
    If using a transposition table, you may return None for
    the best leaf state found. This is because transposition tables cut off
    search branches that may, in fact, contain the best leaf state!
    You can certainly still handle best leaf states, though the move history
    may sometimes come out looking funny... can you figure out why?
    However, your algorithms should still guarantee a correctly historied
    best leaf state returned if transposition_table is False.
"""

"""
    Task #2) Implement Minimax using alpha-beta pruning below. With standard
    move-ordering, it should return the EXACT same result as Minimax,
    but will generally search significantly fewer branches
    and thus perform fewer evaluations.

Background:
Since Minimax assumes the opponent will play a purely, perfectly
adversarial strategy, certain branches can be pruned off if you know that
a player will certainly not choose that action because a better option can be
guaranteed elsewhere. This technique is called alpha-beta pruning, and it can be
extremely powerful - potentially cutting down the tree to the square root of its full size!

Alpha-beta pruning can be hard to wrap your brain around, but this short video
does an excellent job explaining it: https://youtu.be/l-hh51ncgDI?t=313

The effectiveness of alpha-beta pruning depends on what order moves
are explored. Generally speaking, "better" moves should be explored first.
Randomized move ordering may help performance, especially where the
default ordering of actions / next states is actually quite bad.

NOTE:
    CAREFUL with caching values in a transposition table during alpha-beta
    pruning - if a cutoff occurs on a node, the true value remains unknown.
    This can be dealt with in various ways, but in this lab
    we may simply store values ONLY when they are certain (i.e. no alpha-beta
    cutoff)

OPTIONAL :
    You may edit get_all_actions in the various GameStateNode Subclasses
    and customize the ordering of the moves in order to present
    alpha-beta pruning with the likely best moves first.
    Keep the default ordering if custom_move_ordering = False.

    You may then call the game state methods get_all_actions() or
    generate_next_states_and_actions() with the optional parameter
    custom_move_ordering = True to use that ordering. If it is better than the
    default ordering, you will likely see a significant improvement in performance.
"""

def MinimaxAlphaBetaSearch(initial_state,
    util_fn,
    eval_fn = always_zero,
    cutoff = INF,
    state_callback_fn =  (lambda state, state_value = 0 : False) , # A callback function for the GUI. If it returns True, terminate
    counter = {'num_nodes_seen':0,'num_endgame_evals':0, 'num_heuristic_evals':0}, # A counter for tracking stats
    random_move_order = False,     # If true, consider moves in random order
    transposition_table = False,    # If true, use a transposition table.
    ):
    """
    Searches SOME branches of the game tree by performing Minimax with alpha-beta pruning.
    "Pruning" means safely ignored branches that are certain to not
    change the value of the initial state.

    Again, both players are modeled as either maximizing the utility for themselves,
    or maximizing / minimizing the first player (maximizer)'s utility.
    This could be interpreted as a pessimistic model of your opponents behavior.
    """

    maximizer = initial_state.get_current_player()
    if transposition_table:
        t_table = {}
    # A recursive helper function.
    # Has access to all the parameters of the outer function,
    # avoids excessive passing of unchanging parameters
    def MinimaxAlphaBetaSearch_helper(state, _alpha_, _beta_):
        counter['num_nodes_seen'] += 1
        if transposition_table and state in t_table:
            best_leaf_node, best_exp_util = t_table[state]
            terminated = state_callback_fn(state, best_exp_util) if VIS_POST else False
            return None, None, best_exp_util, terminated #could return best_leaf_node but might be funky?
        is_maximizer = state.get_current_player() == maximizer

        # Base case - endgame leaf node:
        if state.is_endgame_state() :
            counter['num_endgame_evals'] += 1
            endgame_util = util_fn(state, maximizer)
            if transposition_table:
                t_table[state] =  state, endgame_util
            # Visualize leaf node with utility, check for early termination signal
            terminated = state_callback_fn(state, endgame_util) if VIS_ENDGAME else False
            return None, state, endgame_util, terminated

        # Early cutoff evaluation:
        if state.get_path_length() - initial_state.get_path_length() >= cutoff:
            counter['num_heuristic_evals'] += 1
            heuristic_eval = eval_fn(state, maximizer)
            if transposition_table:
                t_table[state] =  state, heuristic_eval
            # Visualize leaf node with evaluation, check for early termination signal
            terminated = state_callback_fn(state, heuristic_eval) if VIS_CUTOFF else False

            return None, state, heuristic_eval, terminated

        # Recursive step - maximize expected utility amongst actions

        # Visualize on downwards traversal.
        state_callback_fn(state,None) if VIS_PRE else False

        maximize = (maximizer == state.get_current_player())

        best_action , best_leaf_node, best_exp_util, terminated = None, None, None, False
        all_actions = state.get_all_actions()
        if random_move_order:
            random.shuffle(all_actions)
        for action in all_actions:
            # What child state results from that action?
            child_state = state.generate_next_state(action)
            # Recursively Search from the child_state
            child_action, leaf_node, exp_util, terminated = MinimaxAlphaBetaSearch_helper(child_state, _alpha_, _beta_)

            if maximize:
                if best_exp_util == None or exp_util > best_exp_util:
                    best_action , best_leaf_node, best_exp_util = action, leaf_node, exp_util,
                    _alpha_ = max(best_exp_util, _alpha_)
            else: #minimizing
                if best_exp_util == None or exp_util < best_exp_util:
                    best_action , best_leaf_node, best_exp_util = action, leaf_node, exp_util,
                    _beta_ = min(best_exp_util, _beta_)


            # Visualize mid-expansion, now with partial updated utility!
            if VIS_MID:
                terminated = state_callback_fn(state, best_exp_util)
            if terminated : # early termination - dont go down more branches
                break

            if _alpha_ >= _beta_:
                break

        if transposition_table and not(_alpha_ >= _beta_): # CAREFUL - don't update table if unsure.
            t_table[state] = best_leaf_node, best_exp_util
        # Visualize on upwards traversal, now with fully updated utility!
        terminated = state_callback_fn(state, best_exp_util) if VIS_POST else False
        return best_action , best_leaf_node, best_exp_util, terminated
        ### End of recursive helper function ###


    # Simply call the helper function on the initial_state.

    # Simply call the helper function on the initial_state.
    return MinimaxAlphaBetaSearch_helper(initial_state, -INF, INF)
    #     return (None, None, 0, False)

### Part 3: Progressive Deepening Algorithms #################################################

"""
Useful functions for this section:
time(): the current system time in seconds. You can measure elapsed time this way
sorted(list [key= ..., reversed =..]):  returns a sorted (smallest to greatest) copy of the list.
    Optional parameters: key is a function by which to sort the elements of the list.
    reversed = True will make sorting go from greatest to smallest.
"""

"""
So far, all our search algorithms are hard commitments - we don't get a reliable
answer until they finish completely. This is not very practical, especially if we
don't know how deep we can afford to search.

Progressive Deepening (or Iterative Deepening) repeatedly performs
Minimax with alpha-beta pruning with progressively deepening cutoff depths.
It is sometimes called an "anytime algorithm" because it can be stopped at any
time and be able to yield the best answer it has from the deepest search thus far.
So instead of a cutoff depth limit, a time limit is provided.

The algorithm terminates when either
    1) state_callback_fn returns True as before,
    2) the time limit is reached, or
    3) the search is completely certain about the initial state's value and policy
        because it has reached the endgame on all branches it searched.

Upon termination,
these algorithms return a slightly different 4-tuple:
    1) A *list* of the best actions from each complete search (lowest to highest cutoff).
    2) A *list* of the leaf state at the end of the expected path from each complete search (lowest to highest cutoff).
    3) A *list* of expected utility from each complete search (lowest to highest cutoff).
    4) The highest cutoff searched to completion.

Ostensibly, the results used from the deepest search would be used by the caller.
However, the test GUI will print out results from each depth.
"""

def ProgressiveDeepening (initial_state,
    util_fn,
    eval_fn = always_zero,
    time_limit = INF,
    state_callback_fn =  (lambda state, state_value = 0 : False) , # A callback function for the GUI. If it returns True, terminate
    counter = {'num_nodes_seen':[0], 'num_endgame_evals':[0], 'num_heuristic_evals':[0]}, # A counter for tracking stats
    random_move_order = False,     # If true, consider moves in random order
    transposition_table = False,
    ):
    """
    Performs progressively deepening Minimax search w/ alpha beta pruning.

    If transposition_table is true,
    each search uses the state values calculated by previous searches
    to reorder the moves (after randomizing move ordering, if applicable).
    This helps explore "better" branches earlier, improving pruning.
    This improvement often makes up for the costs of repeatedly searching
    shallower depths.
    """
    end_time = time() + time_limit
    if transposition_table:
        t_table = {}
        old_values = {}

    maximizer = initial_state.get_current_player()
    cutoff = 0

    # A recursive helper function.
    # Has access to all the parameters of the outer function,
    # avoids excessive passing of unchanging parameters
    def MinimaxAlphaBetaSearch_helper(state, _alpha_, _beta_):
        counter['num_nodes_seen'][0] += 1
        counter['num_nodes_seen'][-1] += 1
        if transposition_table and state in t_table:
            best_leaf_node, best_exp_util = t_table[state]
            terminated = state_callback_fn(state, best_exp_util) if VIS_POST else False
            return None, None, best_exp_util, terminated #could return best_leaf_node but might be funky?
        is_maximizer = state.get_current_player() == maximizer

        # Base case - endgame leaf node:
        if state.is_endgame_state() :
            counter['num_endgame_evals'][0] += 1
            counter['num_endgame_evals'][-1] += 1
            endgame_util = util_fn(state, maximizer)
            if transposition_table:
                t_table[state] =  state, endgame_util
            # Visualize leaf node with utility, check for early termination signal
            terminated = state_callback_fn(state, endgame_util) if VIS_ENDGAME else False
            if time() >  end_time :
                terminated = True

            return None, state, endgame_util, terminated

        # Early cutoff evaluation:
        if state.get_path_length() - initial_state.get_path_length() >= cutoff:
            counter['num_heuristic_evals'][0] += 1
            counter['num_heuristic_evals'][-1] += 1
            heuristic_eval = eval_fn(state, maximizer)
            if transposition_table:
                t_table[state] =  state, heuristic_eval
            # Visualize leaf node with evaluation, check for early termination signal
            terminated = state_callback_fn(state, heuristic_eval) if VIS_CUTOFF else False
            if time() >  end_time :
                terminated = True

            return None, state, heuristic_eval, terminated

        # Recursive step - maximize expected utility amongst actions
        # This is expanding!
        # Visualize on downwards traversal.
        state_callback_fn(state,None) if VIS_PRE else False

        maximize = (maximizer == state.get_current_player())

        best_action , best_leaf_node, best_exp_util, terminated = None, None, None, False

        states_and_actions = state.generate_next_states_and_actions()
        if random_move_order:
            random.shuffle(states_and_actions)
        if transposition_table:
            states_and_actions = sorted(states_and_actions,
                key = lambda st_ac: old_values[st_ac[0]] if st_ac[0] in old_values else (_alpha_ if maximize else _beta_),
                reverse = maximize)

        # MOVE ORDERING BY OLD SEARCH VALUES
        for child_state, action in states_and_actions:

            # Recursively Search from the child_state
            child_action, leaf_node, exp_util, terminated = MinimaxAlphaBetaSearch_helper(child_state, _alpha_, _beta_)

            if maximize:
                if best_exp_util == None or exp_util > best_exp_util:
                    best_action , best_leaf_node, best_exp_util = action, leaf_node, exp_util,
                    _alpha_ = max(best_exp_util, _alpha_)
            else: #minimizing
                if best_exp_util == None or exp_util < best_exp_util:
                    best_action , best_leaf_node, best_exp_util = action, leaf_node, exp_util,
                    _beta_ = min(best_exp_util, _beta_)

            # Visualize mid-expansion, now with partial updated utility!
            if VIS_MID:
                terminated = state_callback_fn(state, best_exp_util)
            if terminated : # early termination - dont go down more branches
                break
            if _alpha_ >= _beta_:
                break

        # Visualize on upwards traversal, now with fully updated utility!
        if transposition_table and not(_alpha_ >= _beta_): # CAREFUL - don't update table if unsure because of cutoff.
            t_table[state] = best_leaf_node, best_exp_util
        terminated = (state_callback_fn(state, best_exp_util) if VIS_POST else False)
        if time() >  end_time :
            terminated = True
        return best_action , best_leaf_node, best_exp_util, terminated
        ### End of recursive helper function ###



    best_actions , best_leaf_nodes, best_exp_utils, terminated = [], [], [], False


    while not terminated:
        cutoff += 1
        for count in counter:
            counter[count].append(0)

        # Simply call the helper function on the initial_state.
        best_action , best_leaf_node, best_exp_util, terminated = MinimaxAlphaBetaSearch_helper(initial_state, _alpha_ = -INF, _beta_ = INF)

        if not terminated:
            best_actions.append(best_action)
            best_leaf_nodes.append(best_leaf_node)
            best_exp_utils.append(best_exp_util)
            if transposition_table :
                for state in t_table:
                    old_values[state] = t_table[state][1]
                t_table = {}

        # If no heuristic evals done on this iteration, reached endgame depth
        if counter['num_heuristic_evals'][-1] == 0:
            cutoff += 1
            break

    return best_actions, best_leaf_nodes, best_exp_utils, cutoff - 1

### EXTENSION: Monte Carlo Tree Search #################################################

"""
Extension - meaning not required, entirely optional, just for fun.
This is for those who are intrigued by the state-of-the-art
game playing algorithms and are intrested in challenging themselves.

MCTS is the algorithm at the core of AlphaGo and AlphaZero,
which are at the cutting edge of AI game playing.
It a beautiful algorithm, but more complex than the rest of the lab!
Ensure that you are finished solidly with the other algorithms first.
However, if you succeed, the GUIs and text-game players will work with it!

You may want to do some research online (there are many decent tutorials and blogs)
to understand the concept.
"""

def MonteCarloTreeSearch (initial_state,
    util_fn,
    exploration_bias = 1000,
    time_limit = INF,
    state_callback_fn =  (lambda state, state_value = 0 : False) , # A callback function for the GUI. If it returns True, terminate
    counter = {'num_simulations':0} # A counter for tracking stats
    ):
    """
    Monte Carlo Tree Search builds a tree asymetrically, starting with just the root
    and its children, via randomized simulations.

    It grows the tree by repeating these steps:

    1) select: the most promising leaf with unexplored children. Traverse the tree
        using UCT (Upper Confidence bounds for Trees) with the exploration_bias
        parameter (* sqrt(2)) as the exploration bias factor.
    2) expand: choose one of the unexplored children of the selected leaf
    3) rollout: perform a randomized simulated game from that child and
    4) backpropagation: use the result of the rollout to update statistics of
        expected (average) utility, walking from the expanded child back up
        to the root state node,

    The process terminates when time_limit is reached, or state_callback_fn returns False.

    It then returns the following 4-tuple:
    1) The "best" action to take from initial_state, based on the gathered statistics.
    2) State at the end of the expected path in the grown search tree. (GameStateNode)
    3) Expected utility of the action.
    4) The number of rollouts performed.
    """

    node_values = defaultdict(lambda : [0,0]) #v_i, n_i. Note that v_i is from the parent's perspective.
    def get_est_util(state):
        n_vals = node_values[s]
        return n_vals[0] / n_vals[1]

    terminate_early = False
    def UCB(state):
        v_i, n_i = node_values[state]

        N = node_values[state.parent][1]
        return v_i/n_i + exploration_bias * math.sqrt(2 * math.log(N) / n_i)
        # if n_i <= 0, should not have been called



    ## select promising leaf node (node with unexplored children).
    def selection(state):
        # Visualize on downwards traversal.
        terminate_early = state_callback_fn(state,get_est_util(state)) if VIS_PRE else False
        children = [child for child, action in state.generate_next_states_and_actions()]
        if any(child not in node_values for child in children) or state.is_endgame_state():
            return state

        # otherwise recurse for best leaf
        best = max(children, key = UCB)
        return selection(best)

    ## select unvisited child of state for expansion
    def expansion(state):
        children = [child for child, action in state.generate_next_states_and_actions() if child not in node_values]
        # Maybe, sort children for preferred order of actions?
        # If no unexpanded children,
        if len(children) < 1 and state.is_endgame_state():
            return state
        # Visualize on downwards traversal.
        terminate_early = state_callback_fn(children[0],None) if VIS_PRE else False
        return children[0]

    def rollout(state):
        _, endgame_state, final_util, terminate_early = RandChoice(state, util_fn
        # , state_callback_fn = state_callback_fn
        # , counter = counter
        )
        terminate_early = state_callback_fn(endgame_state, final_util) if VIS_ENDGAME else False
        return final_util

    def backpropagate(state, value):
        node_values[initial_state][1] += 1 # update root game count
        for s in reversed(state.get_path()[1:]):
            n_vals = node_values[s]
            #tricky part - value of node is from parent's perspective.
            # If that matches the perspective of the rollout state
            # add the value, otherwise subtract it.
            if s.parent.current_player == state.current_player:
                n_vals[0] += value
            else:
                n_vals[0] -= value
            n_vals[1] += 1
            terminate_early = state_callback_fn(s, n_vals[0] / n_vals[1]) if VIS_POST else False

    end_time = time() + time_limit
    while (not terminate_early) and time() < end_time:
        # print("Beginning Selection")
        leaf = selection(initial_state)
        # print("Selection done: found the following leaf.\n" + str(leaf))
        unvisited_state = expansion(leaf)
        terminate_early = state_callback_fn(unvisited_state, None)
        # print("Expanding the following child state.\n" + str(unvisited_state))
        result = rollout(unvisited_state)
        counter['num_simulations'] += 1
        backpropagate(unvisited_state, result)

    # get best state/ action
    best_next_state, best_action = max(initial_state.generate_next_states_and_actions(), key = lambda s_a: node_values[s_a[0]][1])
    best_final_state = best_next_state
    # #get expected path of best states
    while best_final_state in node_values and not best_final_state.is_endgame_state():
        best_final_state, _ = max(best_final_state.generate_next_states_and_actions(), key = lambda s_a: node_values[s_a[0]][1])

    v_i, n_i = node_values[best_next_state]
    return best_action, best_final_state, v_i / n_i, node_values[initial_state][1]
