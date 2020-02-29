from lab2_algorithms import *
from time import time
from math import sqrt
from lab2_util_eval import all_fn_dicts, always_zero
from connectfour_gamestate import ConnectFourGameState
from tictactoe_gamestate import TicTacToeGameState
from roomba_gamestate import RoombaRaceGameState
from nim_gamestate import NimGameState

INF = float('inf')

QUIT = ['q', 'Q', 'quit', 'Quit', 'QUIT']
YES = ['y', 'yes', 'Y', 'Yes', 'YES']
NO = ['n', 'no', 'N', 'No', 'NO']
NO_LIMIT = ['inf', 'INF', "Inf", 'infinity', 'infinite', "Infinity", "Infinite",
            'INFINITY', 'INFINITE', 'none', "None", "NONE"]

def ask_yes_no(prompt):
    while True:
        inp = input(prompt)
        if inp in QUIT:
            quit()
        elif inp in YES:
            return True
        elif inp in NO:
            return False
        else :
            print("Oops, please type either 'y[es]' or 'n[o]'.")

def pick_from_dict(prompt, d):
    print("Options: {}.".format(str(list(d.keys()))))
    while True:
        inp = input(prompt)
        if inp in QUIT:
            quit()
        elif inp in d:
            return d[inp]
        else :
            print("Oops, please pick from the following options: {}.".format(str(list(d.keys()))))

def get_int_or_inf(prompt):
    while True:
        inp = input(prompt)
        if inp in QUIT:
            quit()
        elif inp in NO_LIMIT:
            return INF
        try :
            return int(inp)
        except :
            print("Oops, please enter either an int or 'none'/'inf'.")

def get_int(prompt):
    while True:
        inp = input(prompt)
        if inp in QUIT:
            quit()
        try :
            return int(inp)
        except :
            print("Oops, please enter an int.")

def get_float(prompt):
    while True:
        inp = input(prompt)
        if inp in QUIT:
            quit()
        try :
            return float(inp)
        except :
            print("Oops, please enter a float.")

class GamePlayingAgent:
    """ An abstract class for Game Playing Agents, either human or AI.
    """
    def __init__(self, game_class, name = None):
        self.name = name
        self.game_class = game_class

    def set_up(self, **kwargs):
        """
        For instantiating settings, including name.
        Should prompt user (via command prompt).
        """
        raise NotImplementedError

    def choose_action(self, state, **kwargs):
        """
        Return an action for the state and its expected utility (from the perspective of the current player).
        Return None as action to forfeit the game.
        May return additional things!
        """
        raise NotImplementedError

class HumanTextInputAgent(GamePlayingAgent) :

    def __init__(self, game_class, name="Human Player"):
        super().__init__(game_class, name)

    def set_up(self, **kwargs):
        """
        For instantiating settings, including name.
        Should prompt user (via command prompt)
        """
        for kw in kwargs:
            self.kw = kwargs[kw]

        if 'name' not in kwargs:
            new_name= input("Name: >>> ")
            if new_name != "":
                self.name = new_name

        if 'verbose' not in kwargs:
            self.verbose = ask_yes_no("Be verbose? (Print time elapsed) >>> ")

        if 'GUI' in kwargs and kwargs['GUI']:
            self.show_thinking = False


    def choose_action(self, state, **kwargs):
        """
        Return an action for the state and its expected utility (from the perspective of the current player).
        Return None as action to forfeit the game.
        """
        action = None
        search_start_time = time()

        while action is None:
            inp = input("Player {} ({}): Choose your action >>> ".format(state.get_current_player(), self.name))

            # Allow the player to quit gracefully
            if inp in QUIT:
                return None

            try:
                action = self.game_class.str_to_action(inp)
                if action not in state.get_all_actions():
                    print("Invalid action '{}'.Your valid actions include: {}".format(self.game_class.action_to_str(action),
                        str([self.game_class.action_to_str(x) for x in state.get_all_actions()])))
                    action = None
                    continue

            except:
                print("Invalid input '{}'. Your valid actions include: {}".format(inp,
                        str([self.game_class.action_to_str(x) for x in state.get_all_actions()])))
                continue
        elapsed_time = time() - search_start_time
        if self.verbose:
            print("Total elapsed time: {:.4f}".format(elapsed_time))
        return action, None

class ClassicSearchAgent(GamePlayingAgent) :
    def __init__(self, game_class,  search_alg, name="Classic Search Player"):
        self.search_alg = search_alg
        super().__init__(game_class, name)

    def set_up(self, **kwargs):
        """
        For instantiating settings, including name.
        Should prompt user (via commnand prompt)
        """
        for kw in kwargs:
            self.kw = kwargs[kw]

        if 'name' not in kwargs:
            new_name= input("Name: >>> ")
            if new_name != "":
                self.name = new_name

        if 'util_fn' not in kwargs:
            self.util_fn = pick_from_dict("Pick endgame utility func: >>> ",
                                        all_fn_dicts[self.game_class]['endgame_util_fn_dict'])

        if 'cutoff' not in kwargs:
            self.cutoff = get_int_or_inf("Cutoff (Max Search Depth): >>> ")

        if 'eval_fn' not in kwargs:
            if self.cutoff == INF:
                self.eval_fn = always_zero
            else:
                self.eval_fn = pick_from_dict("Pick heuristic cutoff evaluation func: >>> ",
                                        all_fn_dicts[self.game_class]['heuristic_eval_fn_dict'])
        if self.search_alg != RandChoice:
            if 'random_move_order' not in kwargs:
                self.random_move_order = ask_yes_no("Random move order? >>> ")
            if 'transposition_table' not in kwargs:
                self.transposition_table = ask_yes_no("Use a transposition table? >>> ")
        else:
            self.random_move_order = False
            self.transposition_table = False

        if 'verbose' not in kwargs:
            self.verbose = ask_yes_no("Be verbose? >>> ")

        if 'GUI' in kwargs and kwargs['GUI']:
            self.show_thinking = ask_yes_no("Show thinking? (slower) >>> ")


    def choose_action(self, state, **kwargs):
        """
        Return an action for the state and its expected utility (from the perspective of the current player).
        Return None as action to forfeit the game.
        kwargs (optional keyword arguments)
        may include 'state_callback_fn', 'counter'
        """

        if 'state_callback_fn' not in kwargs:
            kwargs['state_callback_fn'] = lambda s, v :False
        if 'counter' not in kwargs :
            kwargs['counter'] = {'num_nodes_seen':0, 'num_endgame_evals':0, 'num_heuristic_evals':0}

        search_start_time = time()
        action, leaf_node, exp_util, terminated = self.search_alg(
            initial_state = state,
            util_fn = self.util_fn,
            eval_fn = self.eval_fn,
            cutoff = self.cutoff,
            state_callback_fn = kwargs['state_callback_fn'],
            counter = kwargs['counter'],
            random_move_order = self.random_move_order,
            transposition_table = self.transposition_table
            )
        elapsed_time = time() - search_start_time
        if self.verbose:
            print("{} values this state at utility {:.4f}".format(self.name, exp_util))
            print("{} nodes seen, {} endgame evals, {} heuristic evals ".format(kwargs['counter']['num_nodes_seen'], kwargs['counter']['num_endgame_evals'],kwargs['counter']['num_heuristic_evals']))
            print("Total elapsed time: {:.4f}".format(elapsed_time))
        return action, exp_util


class RandChoiceAgent(ClassicSearchAgent) :

    def __init__(self, game_class, name="Random Player"):
        super().__init__(game_class, search_alg = RandChoice, name = name)

class MaximizingDFSAgent(ClassicSearchAgent) :

    def __init__(self, game_class, name="MaximizingDFS (Optimistic) Player"):
        super().__init__(game_class, search_alg = ExpectimaxSearch, name = name)


class MinimaxSearchAgent(ClassicSearchAgent) :

    def __init__(self, game_class, name="Minimax (Pessimistic) Player"):
        super().__init__(game_class, search_alg = MinimaxSearch, name = name)

class ExpectimaxSearchAgent(ClassicSearchAgent) :

    def __init__(self, game_class, name="Expectimax (Cautiously Optimistic) Player"):
        super().__init__(game_class, search_alg = ExpectimaxSearch, name = name)


class MinimaxAlphaBetaSearchAgent(ClassicSearchAgent) :

    def __init__(self, game_class, name="Minimax w/ Alpha-Beta (Pessimistic Pruning) Player"):
        super().__init__(game_class, search_alg = MinimaxAlphaBetaSearch, name = name)


class ProgressiveDeepeningSearchAgent(GamePlayingAgent) :
    def __init__(self, game_class, name="Progressive Deepening Player"):
        self.search_alg = ProgressiveDeepening
        super().__init__(game_class, name)

    def set_up(self, **kwargs):
        """
        For instantiating settings, including name.
        Should prompt user (via commnand prompt)
        """
        for kw in kwargs:
            self.kw = kwargs[kw]

        if 'name' not in kwargs:
            new_name= input("Name: >>> ")
            if new_name != "":
                self.name = new_name

        if 'util_fn' not in kwargs:
            self.util_fn = pick_from_dict("Pick endgame utility func: >>> ",
                                        all_fn_dicts[self.game_class]['endgame_util_fn_dict'])

        if 'eval_fn' not in kwargs:
            self.eval_fn = pick_from_dict("Pick heuristic cutoff evaluation func: >>> ",
                                        all_fn_dicts[self.game_class]['heuristic_eval_fn_dict'])

        if 'time_limit' not in kwargs:
            self.time_limit = get_float("Time Limit (seconds): >>> ")

        if 'random_move_order' not in kwargs:
            self.random_move_order = ask_yes_no("Random move order? >>> ")

        if 'transposition_table' not in kwargs:
            self.transposition_table = ask_yes_no("Use a transposition table? >>> ")

        if 'verbose' not in kwargs:
            self.verbose = ask_yes_no("Be verbose? >>> ")
            if self.verbose:
                self.super_verbose = ask_yes_no("Be SUPER verbose? >>> ")

        if 'GUI' in kwargs and kwargs['GUI']:
            self.show_thinking = ask_yes_no("Show thinking? (slower) >>> ")

    def choose_action(self, state, **kwargs):
        """
        Return an action for the state and its expected utility (from the perspective of the current player).
        Return None as action to forfeit the game.
        kwargs (optional keyword arguments)
        may include 'state_callback_fn', 'counter'
        """

        if 'state_callback_fn' not in kwargs:
            kwargs['state_callback_fn'] = lambda s, v :False
        if 'counter' not in kwargs :
            kwargs['counter'] = {'num_nodes_seen':[0],'num_endgame_evals':[0], 'num_heuristic_evals':[0], }

        search_start_time = time()
        best_actions, best_leaf_nodes, best_exp_utils, max_cutoff = self.search_alg(
            initial_state = state,
            util_fn = self.util_fn,
            eval_fn = self.eval_fn,
            time_limit = self.time_limit,
            state_callback_fn = kwargs['state_callback_fn'],
            counter = kwargs['counter'],
            random_move_order = self.random_move_order,
            transposition_table = self.transposition_table

            )
        elapsed_time = time() - search_start_time
        if self.verbose:
            if self.super_verbose:
                for c in range(1,max_cutoff+1):
                    print("Cutoff {}: Best action is {} at exp value {:.4f}.\n{} nodes seen, {} endgame evals, {} cutoff evals".format(
                        c, best_actions[c-1], best_exp_utils[c-1],
                        kwargs['counter']['num_nodes_seen'][c], kwargs['counter']['num_endgame_evals'][c], kwargs['counter']['num_heuristic_evals'][c]
                        ))
            else:
                print("After max cutoff {}: Best action is {} at exp value {:.4f}.".format(
                    max_cutoff, best_actions[-1], best_exp_utils[-1],
                    ))
            print("Total:\n Nodes seen: {} | Endgame evals: {} | Cutoff evals: {}".format(kwargs['counter']['num_nodes_seen'][0],kwargs['counter']['num_endgame_evals'][0],kwargs['counter']['num_heuristic_evals'][0]))
            print("Total elapsed time: {:.4f}".format(elapsed_time))
        if max_cutoff > 0:
            return best_actions[-1], best_exp_utils[-1]
        else :
            return None, None

class MonteCarloTreeSearchAgent(GamePlayingAgent):
    def __init__(self, game_class, name="Monte Carlo Tree Search Player"):
        self.search_alg = MonteCarloTreeSearch
        super().__init__(game_class, name)

    def set_up(self, **kwargs):
        """
        For instantiating settings, including name.
        Should prompt user (via commnand prompt).
        """
        for kw in kwargs:
            self.kw = kwargs[kw]

        if 'name' not in kwargs:
            new_name= input("Name: >>> ")
            if new_name != "":
                self.name = new_name

        if 'util_fn' not in kwargs:
            self.util_fn = pick_from_dict("Pick endgame utility func: >>> ",
                                        all_fn_dicts[self.game_class]['endgame_util_fn_dict'])

        if 'exploration_bias' not in kwargs:
            self.exploration_bias = get_float("Exploration Bias x sqrt(2) (recommended = 1000 [~max utility]): >>> ")

        if 'time_limit' not in kwargs:
            self.time_limit = get_float("Time Limit (seconds): >>> ")

        if 'verbose' not in kwargs:
            self.verbose = ask_yes_no("Be verbose? >>> ")

        if 'GUI' in kwargs and kwargs['GUI']:
            self.show_thinking = ask_yes_no("Show thinking? (slower) >>> ")


    def choose_action(self, state, **kwargs):
        """
        Return an action for the state and its expected utility (from the perspective of the current player).
        Return None as action to forfeit the game.
        kwargs (optional keyword arguments)
        may include 'state_callback_fn', 'counter'
        """

        if 'state_callback_fn' not in kwargs:
            kwargs['state_callback_fn'] = lambda s, v :False
        if 'counter' not in kwargs :
            kwargs['counter'] = {'num_simulations': 0}

        search_start_time = time()
        best_action, best_leaf_state , best_exp_util, num_simulations = MonteCarloTreeSearch(
                                initial_state = state,
                                util_fn = self.util_fn,
                                exploration_bias = self.exploration_bias * sqrt(2),
                                time_limit = self.time_limit,
                                state_callback_fn = kwargs['state_callback_fn'],
                                counter = kwargs['counter']
                                )
        elapsed_time = time() - search_start_time
        if self.verbose:
            print("After {} simulations, best action is {} at exp value {:.4f}.".format(
                num_simulations, best_action, best_exp_util,
                ))
            print("Total elapsed time: {:.4f}".format(elapsed_time))

        return best_action, best_exp_util
