"""
Visualizing GUI for your solutions to Lab 2.
Use it to test your algorithms, evaluation functions, and game representations.

Usage:
    python lab2_test_gui.py [GAME] [INITIAL_STATE_FILE]
    GAME can be tictactoe, nim, connectfour, or roomba
    INITIAL_STATE_FILE is a path to a text file or 'default'
"""
from traceback import format_exc
from sys import argv
from time import time, sleep
from math import sqrt
from tkinter import * # Tk, Canvas, Frame, Listbox, Button, Checkbutton, IntVar, StringVar, Spinbox, Label
from lab2_algorithms import *
from gamestatenode import GameStateNode
from connectfour_gamestate import ConnectFourGameState
from tictactoe_gamestate import TicTacToeGameState
from nim_gamestate import NimGameState
from roomba_gamestate import RoombaRaceGameState, FLOOR, WALL, CLEANED
from lab2_util_eval import all_fn_dicts


### GUI too big? Change this number
MAX_HEIGHT = 350


INF = float('inf')
# For tic-tac-toe, connectfour, and nim
PIECE_1, PIECE_2, FRAME , EMPTY, TEXT = 'piece_1', 'piece_2','frame', 'empty', 'text'
# For nim
STONE = 'stone'
# For roomba race
AGENT, PATH = (None,'agent_1', 'agent_2'), (None,'path_1', 'path_2')

COLORS = {FLOOR : 'pale green', WALL : 'gray25', CLEANED[1] : 'tomato', CLEANED[2]: 'light blue',
          AGENT[1]:"orange red", AGENT[2]:"blue", PATH[1]:"orange red", PATH[2]:"blue",
          PIECE_1 : 'red', PIECE_2 : 'yellow', FRAME: 'blue',EMPTY: 'white' , TEXT: 'black',
          STONE : 'grey'}


PROVIDED_ALGORITHMS = {"0) Random Policy" : RandChoice}
CLASSIC_ALGORITHMS = {"0) Random Policy" : RandChoice, "1) Max-DFS" : MaximizingDFS, "2) Minimax" : MinimaxSearch, "3) Expectimax" : ExpectimaxSearch, "4) Alpha-beta" : MinimaxAlphaBetaSearch}
PROGRESSIVE_ALGORITHMS = {"5) Prog. Deepening" : ProgressiveDeepening}
ANYTIME_ALGORITHMS = {"5) Prog. Deepening" : ProgressiveDeepening,  "6) MonteCarloTreeSearch": MonteCarloTreeSearch}
ASYMMETRIC_ALGORITHMS = {"6) MonteCarloTreeSearch": MonteCarloTreeSearch}
ALGORITHMS =  {"0) Random Policy" : RandChoice,
                "1) Max-DFS" : MaximizingDFS, "2) Minimax" : MinimaxSearch, "3) Expectimax" : ExpectimaxSearch,
                "4) Alpha-beta" : MinimaxAlphaBetaSearch, "5) Prog. Deepening" : ProgressiveDeepening,
                "6) MonteCarloTreeSearch": MonteCarloTreeSearch}


STEP_TIME_OPTIONS = (0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09,
                    0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 2.0, 5.0)

CUTOFF_OPTIONS = tuple( ['INF'] + list(range(0,100)))

INITIAL_WAITING = 0
SEARCHING_RUNNING = 1
SEARCHING_PAUSED = 2
SEARCHING_STEP = 3
TERMINATING_EARLY = 4
FINISHED_COMPLETE = 5
FINISHED_INCOMPLETE = 6
FINISHED_COMPLETE_DISP_LEAF = 9
FINISHED_INCOMPLETE_DISP_LEAF = 10
FINISHED_NO_RESULT = 11
SEARCH_ERROR = -1


VALID_STATUS_TRANSITIONS = {
    None: (INITIAL_WAITING,),
    INITIAL_WAITING : (SEARCHING_RUNNING, SEARCHING_PAUSED, SEARCHING_STEP),
    SEARCHING_RUNNING : (SEARCHING_PAUSED, SEARCHING_STEP, TERMINATING_EARLY, FINISHED_COMPLETE, FINISHED_NO_RESULT, SEARCH_ERROR, INITIAL_WAITING),
    SEARCHING_PAUSED : (SEARCHING_RUNNING, SEARCHING_STEP, TERMINATING_EARLY, FINISHED_COMPLETE, FINISHED_NO_RESULT, SEARCH_ERROR, INITIAL_WAITING),
    SEARCHING_STEP : (SEARCHING_RUNNING, SEARCHING_PAUSED, TERMINATING_EARLY, FINISHED_COMPLETE, FINISHED_NO_RESULT, SEARCH_ERROR, INITIAL_WAITING),
    TERMINATING_EARLY : (FINISHED_COMPLETE, FINISHED_INCOMPLETE, FINISHED_NO_RESULT),
    FINISHED_COMPLETE : (FINISHED_COMPLETE_DISP_LEAF,INITIAL_WAITING),
    FINISHED_INCOMPLETE : (FINISHED_INCOMPLETE_DISP_LEAF,INITIAL_WAITING),
    FINISHED_COMPLETE_DISP_LEAF : (FINISHED_COMPLETE,INITIAL_WAITING),
    FINISHED_INCOMPLETE_DISP_LEAF : (FINISHED_INCOMPLETE,INITIAL_WAITING),
    FINISHED_NO_RESULT : (INITIAL_WAITING,),
    SEARCH_ERROR : tuple()
}

STATUS_TEXT = { INITIAL_WAITING: "Player {}: Pick a search algorithm or click to input a move.",
                SEARCHING_RUNNING:"{} ({}, {}) is searching...",
                SEARCHING_PAUSED: "{} ({}, {}) is paused.",
                SEARCHING_STEP:   "{} ({}, {}) is paused.",
                TERMINATING_EARLY: "{} ({}, {}) is terminating early...",
                FINISHED_COMPLETE: "{} ({}, {}) completed successfully. Displaying best move found.",
                FINISHED_INCOMPLETE: "{} ({}, {}) terminated early. Displaying best move found.",
                FINISHED_COMPLETE_DISP_LEAF: "{} ({}, {}) completed successfully. Displaying expected leaf node.",
                FINISHED_INCOMPLETE_DISP_LEAF: "{} ({}, {}) terminated early. Displaying expected leaf node.",
                FINISHED_NO_RESULT: "{} ({}, {}) returned no best move, leaf node, and/or exp utility. If endgame, this is correct.",
                SEARCH_ERROR: "Something went wrong during search. Check the console for the exception stack trace."
                }

class Lab2GUI_SEARCH:
    def __init__(self, master, initial_state, canvas_height, canvas_width):
        self.master = master

        self.initial_state = initial_state
        self.current_state = initial_state

        self.search_root_state = initial_state
        self.display_state = initial_state

        self.search_result_best_leaf_state = None
        self.search_result_best_action = None

        self.search_start_time = None

        #########################################################################################

        self.canvas = Canvas(master, height=canvas_height, width=canvas_width, bg='white')

        self.canvas.grid(row = 0, columnspan = 5) #pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', lambda *args : self.draw_background() or self.draw_path_to_state() )
        self.canvas.bind('<Button-1>', self.click_canvas_attempt_action)

        ################################################

        gameplay_button_frame = Frame(master)
        gameplay_button_frame.grid(row = 1, columnspan = 5, sticky = N, padx = 3)

        self.restart_button = Button(gameplay_button_frame, text="Restart Game",
                    command= self.restart_game, width = 15, pady = 3)
        self.restart_button.grid(row = 0, column = 0, sticky = NE)

        self.undo_move_button = Button(gameplay_button_frame, text="Undo Last Move",
                    command= self.undo_last_move, width = 15, pady = 3)
        self.undo_move_button.grid(row = 0, column = 1, sticky = NW)

        self.history_button = Button(gameplay_button_frame, text="Toggle History",
                    command= self.toggle_display_history, width = 15, pady = 3)
        self.history_button.grid(row = 0, column = 2, sticky = NW)

        ###################################################

        status_output_frame = Frame(master, padx = 3)
        status_output_frame.grid(row = 2, columnspan = 5,sticky = N)

        self.status = None

        self.status_text = StringVar()
        self.status_label = Label(status_output_frame, textvariable = self.status_text, anchor = CENTER, bg = "lightblue", pady = 3, justify = CENTER, relief = GROOVE)
        self.status_label.grid(row= 0,sticky = N)


        self.counter_dict = {}

        self.eval_fn_result_text = StringVar()
        self.eval_fn_result_text.set('Expected utility of state: {:7s}'.format("TBD"))

        self.eval_fn_result_label = Label(status_output_frame, textvariable = self.eval_fn_result_text, bg = "lightgreen", justify = CENTER, anchor = CENTER, relief = GROOVE)
        self.eval_fn_result_label.config(font=("Courier", 12))
        self.eval_fn_result_label.grid(row= 1,sticky = N)

        self.counter_text_1 = StringVar()
        self.counter_label_1 = Label(status_output_frame, textvariable = self.counter_text_1, fg = "blue", anchor = CENTER)
        self.counter_label_1.grid(row= 2,sticky = N)




        #########################################################################################


        algorithm_frame = Frame(master)
        algorithm_frame.grid(row = 3, column = 0, sticky = NW, padx = 3)

        algorithm_label = Label(algorithm_frame, text="Game Search Algorithm:")
        algorithm_label.grid(row = 0, sticky = NW)

        self.algorithm_listbox = Listbox(algorithm_frame, selectmode = BROWSE, height = len(ALGORITHMS), exportselection = 0)
        self.algorithm_listbox.grid(row= 1, sticky = NW)
        for item in sorted(ALGORITHMS.keys()):
            self.algorithm_listbox.insert(END, item)
        self.algorithm_listbox.select_set(0) # This only sets focus on the first item.
        self.algorithm_listbox.bind('<<ListboxSelect>>', self.on_alg_changed)
        self.algorithm_listbox.event_generate("<<ListboxSelect>>")

        self.current_algorithm_name = self.get_alg_selection()


        #########################################################################################


        eval_fn_frame = Frame(master)
        eval_fn_frame.grid(row = 3, column = 1, sticky = NW, padx = 3)


        endgame_util_fn_label = Label(eval_fn_frame, text="Endgame (Utility) Eval Func:")
        endgame_util_fn_label.grid(row = 0, sticky = NW)

        # set self.endgame_util_fn_dict in init of subclass
        if not hasattr(self, 'endgame_util_fn_dict'):
            self.endgame_util_fn_dict = {}
        self.endgame_util_fn_listbox = Listbox(eval_fn_frame, selectmode = BROWSE, height = len(self.endgame_util_fn_dict), exportselection = 0)
        self.endgame_util_fn_listbox.grid(row= 1, sticky = NW)
        for item in sorted(self.endgame_util_fn_dict.keys()):
            self.endgame_util_fn_listbox.insert(END, item)
        self.endgame_util_fn_listbox.select_set(0) # This only sets focus on the first item.
        self.endgame_util_fn_listbox.event_generate("<<ListboxSelect>>")

        self.current_endgame_util_fn = self.get_endgame_util_fn_selection()


        heuristics_label = Label(eval_fn_frame, text="Cutoff (Heuristic) Eval Func:")
        heuristics_label.grid(row = 2, sticky = NW)
        # set self.heuristic_eval_fn_dict in init of subclass
        if not hasattr(self, 'endgame_util_fn_dict'):
            self.endgame_util_fn_dict = GameStateNode.endgame_util_fn_dict
        if not hasattr(self, 'heuristic_eval_fn_dict'):
            self.heuristic_eval_fn_dict = GameStateNode.heuristic_eval_fn_dict

        self.heuristic_eval_fn_listbox = Listbox(eval_fn_frame, selectmode = BROWSE, height = len(self.heuristic_eval_fn_dict), exportselection = 0)
        self.heuristic_eval_fn_listbox.grid(row= 3, sticky = NW)
        for item in sorted(self.heuristic_eval_fn_dict.keys()):
            self.heuristic_eval_fn_listbox.insert(END, item)
        self.heuristic_eval_fn_listbox.select_set(0) # This only sets focus on the first item.
        self.heuristic_eval_fn_listbox.event_generate("<<ListboxSelect>>")

        self.current_heuristic_eval_fn = self.get_heuristic_eval_fn_selection()

        #########################################################################################
        search_options_frame = Frame(master)
        search_options_frame.grid(row = 3, column = 2, sticky = NW, padx = 3)

        cutoff_frame = Frame(search_options_frame)
        cutoff_frame.grid(row = 0, sticky = NW, pady = 3)

        self.cutoff_time_limit_label = Label(cutoff_frame, text="Cutoff Depth:")
        self.cutoff_time_limit_label.grid(row = 0, column = 0, sticky = NW)

        self.cutoff_time_limit_spinbox = Spinbox(cutoff_frame,
            values=CUTOFF_OPTIONS, width = 5, wrap = True)
        self.cutoff_time_limit_spinbox.grid(row= 0, column = 1, sticky = NW, padx = 5)
        while(self.cutoff_time_limit_spinbox.get() != "INF") :
            self.cutoff_time_limit_spinbox.invoke('buttonup')

        self.recent_time_limit = "INF"
        self.recent_cutoff = "INF"

        self.random_move_order_state = IntVar()
        self.random_move_order_state.set(0)
        self.random_move_order_checkbox = Checkbutton(search_options_frame, text='Randomize move order?', variable=self.random_move_order_state)
        self.random_move_order_checkbox.grid(row= 1, column = 0, sticky = NW)

        self.transposition_table_state = IntVar()
        self.transposition_table_state.set(0)
        self.transposition_table_checkbox = Checkbutton(search_options_frame, text='Transposition table?', variable=self.transposition_table_state)
        self.transposition_table_checkbox.grid(row= 2, column = 0, sticky = NW)

        exploration_bias_frame = Frame(search_options_frame)
        exploration_bias_frame.grid(row = 3, sticky = NW, pady = 3)

        self.exploration_bias_label = Label(exploration_bias_frame, text="Expl. Bias:" )
        self.exploration_bias_label.grid(row = 0, column = 0, sticky = NW)
        self.exploration_bias_state = DoubleVar()
        self.exploration_bias_state.set(1000)
        self.exploration_bias_entry = Entry(exploration_bias_frame, textvariable = self.exploration_bias_state, width = 6)
        self.exploration_bias_entry.grid(row = 0, column = 1, sticky = NW)
        self.exploration_bias_label_2 = Label(exploration_bias_frame, text="* sqrt(2)")
        self.exploration_bias_label_2.grid(row = 0, column = 2, sticky = NW)

        #########################################################################################

        run_options_frame = Frame(master)
        run_options_frame.grid(row = 3, column = 3, sticky = NW, padx = 3)

        self.reset_button = Button(run_options_frame, text="Terminate Search", # Discard Search Results
                            command= self.terminate_search_or_discard_results, width = 15, pady = 3)
        self.reset_button.grid(row = 1, column = 0, sticky = NW)


        self.run_pause_button = Button(run_options_frame, text="Start Search", # Pause Search, Play Move
                            command= self.toggle_run_pause_or_play_move, width = 15, pady = 3)
        self.run_pause_button.grid(row= 2, column = 0, sticky = NW)

        self.step_button = Button(run_options_frame, text="Step Search", # Display Search [Move/Exp Leaf Node]
                            command=self.step_or_toggle_display_action_leaf, width = 15, pady = 3)
        self.step_button.grid(row= 3, column = 0, sticky = NW)


        self.fly_blind_search_button = Button(run_options_frame, text="FLY BLIND SEARCH", # Pause Search, Play Move
                            command= self.fly_blind_search, width = 15, pady = 3, fg = 'blue')
        self.fly_blind_search_button.grid(row = 4, column = 0, sticky = NW)

        #########################################################################################

        status_output_settings_frame = Frame(master, padx = 3,width = 30)
        status_output_settings_frame.grid(row = 3, column = 4,sticky = NW)



        self.visualize_extends_state = IntVar()
        self.visualize_extends_state.set(1)
        self.visualize_extends_checkbox = Checkbutton(status_output_settings_frame, text='Visualize search steps?', variable=self.visualize_extends_state)
        self.visualize_extends_checkbox.grid(row= 1, column = 0, sticky = NW)

        self.print_status_state = IntVar()
        self.print_status_state.set(1)
        self.print_status_checkbox = Checkbutton(status_output_settings_frame, text='Print search progress?', variable=self.print_status_state)
        self.print_status_checkbox.grid(row= 2, column = 0, sticky = NW)

        step_time_spinbox_frame = Frame(status_output_settings_frame)
        step_time_spinbox_frame.grid(row = 3, column = 0,sticky = NW)

        self.step_time_label = Label(step_time_spinbox_frame, text = "Step time: ")
        self.step_time_label.grid(row= 0, column = 0, sticky = NW)

        self.step_time_spinbox = Spinbox(step_time_spinbox_frame,
        values=STEP_TIME_OPTIONS, format="%3.2f", width = 4)
        self.step_time_spinbox.grid(row= 0, column = 1, sticky = NW)
        while(self.step_time_spinbox.get() != "0.1") :
            self.step_time_spinbox.invoke('buttonup')

        self.print_path_states_button = Button(status_output_settings_frame, text="Print Current Search Path.", #Print Expected Path
                            command=self.print_path_states,width = 20, pady = 3)
        self.print_path_states_button.grid(row= 4, column = 0, sticky = NW)


        ###############################################################

        self.update_status_and_ui(INITIAL_WAITING)


    def update_status_and_ui(self, newstatus = INITIAL_WAITING):
        if newstatus == self.status: # No change?
            return

        assert newstatus in VALID_STATUS_TRANSITIONS[self.status]

        self.status = newstatus
        if self.status != INITIAL_WAITING:
            self.status_text.set(STATUS_TEXT[self.status].format(self.current_algorithm_name, self.current_endgame_util_fn, self.current_heuristic_eval_fn))
        else:
            self.status_text.set(STATUS_TEXT[self.status].format(self.current_state.get_current_player()))

        if newstatus == INITIAL_WAITING :
            self.restart_button['state'] = NORMAL
            self.restart_button['bg'] = 'orange red'
            self.undo_move_button['state'] = NORMAL
            self.undo_move_button['bg'] = 'DodgerBlue2'
            self.history_button['state'] = NORMAL
            self.history_button['bg'] = 'orchid1'

            self.reset_button['state'] = DISABLED
            self.reset_button['text'] = 'Terminate Search'
            self.reset_button['bg'] = 'grey'

            # Can choose new algorithm settings
            self.cutoff_time_limit_spinbox['state'] = NORMAL
            self.algorithm_listbox['state'] = NORMAL
            self.endgame_util_fn_listbox['state'] = NORMAL
            self.heuristic_eval_fn_listbox['state'] = NORMAL
            self.random_move_order_checkbox['state'] = NORMAL
            self.transposition_table_checkbox['state'] = NORMAL
            self.exploration_bias_label['state'] = NORMAL
            self.exploration_bias_label_2['state'] = NORMAL
            self.exploration_bias_entry['state'] = NORMAL
            self.on_alg_changed() # set certain UI features based on alg

            self.run_pause_button['state'] = NORMAL
            self.run_pause_button['text'] = 'Start Search'
            self.run_pause_button['bg'] = 'green'

            self.step_button['state'] = NORMAL
            self.step_button['text'] = 'Step Search'
            self.step_button['bg'] = 'yellow'

            self.print_path_states_button['state'] = DISABLED
            self.print_path_states_button['text'] = "Print Current Search Path"

            self.fly_blind_search_button['state'] = NORMAL
            self.fly_blind_search_button['bg'] = 'VioletRed1'


        elif newstatus in (SEARCHING_RUNNING,
                            SEARCHING_PAUSED, SEARCHING_STEP):
            self.restart_button['state'] = DISABLED
            self.restart_button['bg'] = 'grey'
            self.undo_move_button['state'] = DISABLED
            self.undo_move_button['bg'] = 'grey'
            self.history_button['state'] = DISABLED
            self.history_button['bg'] = 'grey'

            self.reset_button['state'] = NORMAL
            self.reset_button['text'] = 'Terminate Search'
            self.reset_button['bg'] = 'red'

            # Cannot choose new algorithm settings
            self.cutoff_time_limit_spinbox['state'] = DISABLED
            self.algorithm_listbox['state'] = DISABLED
            self.endgame_util_fn_listbox['state'] = DISABLED
            self.heuristic_eval_fn_listbox['state'] = DISABLED
            self.random_move_order_checkbox['state'] = DISABLED
            self.transposition_table_checkbox['state'] = DISABLED
            self.exploration_bias_label['state'] = DISABLED
            self.exploration_bias_label_2['state'] = DISABLED
            self.exploration_bias_entry['state'] = DISABLED

            self.step_button['state'] = NORMAL
            self.run_pause_button['state'] = NORMAL

            self.print_path_states_button['state'] = NORMAL
            self.print_path_states_button['text'] = "Print Current Search Path"

            if newstatus == SEARCHING_RUNNING:
                self.run_pause_button['text'] = 'Pause Search'
                self.run_pause_button['bg'] = 'orange'
            elif newstatus == SEARCHING_PAUSED: # moving away == starting searching
                self.run_pause_button['text'] = 'Continue Search'
                self.run_pause_button['bg'] = 'green'
            elif newstatus == SEARCHING_STEP: # moving away == starting searching
                self.run_pause_button['text'] = 'Continue Search'
                self.run_pause_button['bg'] = 'green'
                # If we're stepping, obviously user means to see things
                self.visualize_extends_state.set(1)
                self.print_status_state.set(1)

            self.fly_blind_search_button['state'] = DISABLED
            self.fly_blind_search_button['bg'] = 'grey'

        elif newstatus in (TERMINATING_EARLY,):
            self.reset_button['state'] = DISABLED
            self.run_pause_button['state'] = DISABLED
            self.step_button['state'] = DISABLED
            self.print_path_states_button['state'] = DISABLED

        elif newstatus in (FINISHED_INCOMPLETE, FINISHED_COMPLETE):
            self.reset_button['state'] = NORMAL
            self.reset_button['text'] = 'Discard Search'
            self.reset_button['bg'] = 'red'

            self.run_pause_button['state'] = NORMAL
            self.run_pause_button['text'] = 'Play Best Move'
            self.run_pause_button['bg'] = 'green'

            if self.search_result_best_leaf_state != None:
                self.step_button['state'] = NORMAL
                self.step_button['text'] = 'Show Expected Path'
                self.step_button['bg'] = 'violet'
            else:
                self.step_button['state'] = DISABLED
                self.step_button['text'] = 'Show Expected Path'
                self.step_button['bg'] = 'grey'

            self.print_path_states_button['state'] = NORMAL
            self.print_path_states_button['text'] = "Print Expected Path"

        elif newstatus in (FINISHED_INCOMPLETE_DISP_LEAF, FINISHED_COMPLETE_DISP_LEAF):
            self.step_button['state'] = NORMAL
            self.step_button['text'] = 'Show Best Move'

        elif newstatus in (FINISHED_NO_RESULT,) :
            self.reset_button['state'] = NORMAL
            self.reset_button['text'] = 'Discard Search Result'

            self.run_pause_button['state'] = DISABLED
            self.run_pause_button['text'] = 'Play Best Move'
            self.run_pause_button['bg'] = 'grey'

            self.step_button['state'] = DISABLED
            self.step_button['text'] = 'Show Expected Path'
            self.run_pause_button['bg'] = 'grey'

            self.print_path_states_button['state'] = DISABLED
            self.print_path_states_button['text'] = "Print Expected Path"
        elif newstatus in (SEARCH_ERROR,):
            self.restart_button['state'] = DISABLED
            self.undo_move_button['state'] = DISABLED
            self.history_button['state'] = DISABLED
            self.reset_button['state'] = DISABLED
            # Cannot choose new algorithm settings
            self.cutoff_time_limit_spinbox['state'] = DISABLED
            self.algorithm_listbox['state'] = DISABLED
            self.endgame_util_fn_listbox['state'] = DISABLED
            self.heuristic_eval_fn_listbox['state'] = DISABLED
            self.random_move_order_checkbox['state'] = DISABLED

            self.run_pause_button['state'] = DISABLED
            self.step_button['state'] = DISABLED
            self.print_path_states_button['state'] = DISABLED
            self.fly_blind_search_button['state'] = DISABLED

        return newstatus

    def print_path_states(self) :

        if self.status in (FINISHED_COMPLETE, FINISHED_INCOMPLETE, FINISHED_COMPLETE_DISP_LEAF, FINISHED_INCOMPLETE_DISP_LEAF):
            print_state = self.search_result_best_leaf_state
            print_str = "Expected Path states: (length {})"
        else:
            print_state = self.display_state
            print_str = "Current Search Path states: (length {})"

        if print_state == None:
            print("No path to print.")
            return

        print(print_str.format(print_state.get_path_length()))
        for n, state in enumerate(print_state.get_path()):
            if n > 0:
                print('{}: {} chooses {}'.format(str(n), state.parent.current_player,
                        self.game_class.action_to_pretty_str(state.previous_action)))
            print(str(state))


    # def print_path_actions(self) :
    #     print_state = self.display_state if self.status not in (FINISHED_COMPLETE, FINISHED_INCOMPLETE) else self.best_leaf_state
    #     print("Expected Path actions: (length {})".format(print_state.get_path_length()))
    #     for n, state in enumerate(print_state.get_path()):
    #         if n > 0:
    #             print('{}: {}'.format(str(n), state.describe_previous_action()))

    def on_alg_changed(self, event = None):
        alg = self.get_alg_selection()

        if alg in ANYTIME_ALGORITHMS:
            if self.cutoff_time_limit_label['text'] != "Time Limit (s)":
                self.recent_cutoff = self.cutoff_time_limit_spinbox.get()
                self.cutoff_time_limit_label['text'] = "Time Limit (s)"
                while(self.cutoff_time_limit_spinbox.get() != self.recent_time_limit) :
                    self.cutoff_time_limit_spinbox.invoke('buttonup')

        else:
            if self.cutoff_time_limit_label['text'] != "Cutoff Depth":
                self.recent_time_limit = self.cutoff_time_limit_spinbox.get()
                self.cutoff_time_limit_label['text'] = "Cutoff Depth"
                while(self.cutoff_time_limit_spinbox.get() != self.recent_cutoff) :
                    self.cutoff_time_limit_spinbox.invoke('buttonup')

        if alg in ASYMMETRIC_ALGORITHMS or alg in PROVIDED_ALGORITHMS:
            self.transposition_table_checkbox['state'] = DISABLED
            self.random_move_order_checkbox['state'] = DISABLED
        else:
            self.transposition_table_checkbox['state'] = NORMAL
            self.random_move_order_checkbox['state'] = NORMAL

        if alg in ASYMMETRIC_ALGORITHMS:
            self.exploration_bias_label['state'] = NORMAL
            self.exploration_bias_label_2['state'] = NORMAL
            self.exploration_bias_entry['state'] = NORMAL
        else:
            self.exploration_bias_label['state'] = DISABLED
            self.exploration_bias_label_2['state'] = DISABLED
            self.exploration_bias_entry['state'] = DISABLED

    def get_alg_selection(self) :
        return self.algorithm_listbox.get(self.algorithm_listbox.curselection()[0])

    def get_heuristic_eval_fn_selection(self) :
        return self.heuristic_eval_fn_listbox.get(self.heuristic_eval_fn_listbox.curselection()[0])

    def get_endgame_util_fn_selection(self) :
        return self.endgame_util_fn_listbox.get(self.endgame_util_fn_listbox.curselection()[0])


    def verify_parameters(self, fly_blind):
        if self.current_algorithm_name in PROVIDED_ALGORITHMS or self.current_algorithm_name in CLASSIC_ALGORITHMS:
            try:
                cutoff = float(self.cutoff_time_limit_spinbox.get())
            except Exception:
                self.update_status_and_ui(INITIAL_WAITING)
                self.status_text.set("Cutoff not a valid number. ('INF' for no limit)")
                return False
        if self.current_algorithm_name in ANYTIME_ALGORITHMS:
            try:
                time_limit = float(self.cutoff_time_limit_spinbox.get())
                if fly_blind and (time_limit == INF) :
                    self.update_status_and_ui(INITIAL_WAITING)
                    self.status_text.set("Woah there - don't \"fly blind\" with no time limit!")
                    return False
            except Exception:
                self.update_status_and_ui(INITIAL_WAITING)
                self.status_text.set("Time Limit not a valid number. ('INF' for no limit)")
                return False

        if self.current_algorithm_name in ASYMMETRIC_ALGORITHMS:
            try:
                exploration_bias = self.exploration_bias_state.get()
            except Exception:
                self.update_status_and_ui(INITIAL_WAITING)
                self.status_text.set("Exploration Bias is not a valid number. (Default 1000)")
                return False

        return True


    def run_search(self, fly_blind):
        search_alg = ALGORITHMS[self.current_algorithm_name]
        endgame_util_fn = self.endgame_util_fn_dict[self.current_endgame_util_fn]
        heuristic_eval_fn = self.heuristic_eval_fn_dict[self.current_heuristic_eval_fn]

        if self.current_algorithm_name in CLASSIC_ALGORITHMS:
            self.counter_dict = {'num_nodes_seen':0,'num_endgame_evals':0, 'num_heuristic_evals':0}
            search_start_time = time()
            self.search_result_best_action , self.search_result_best_leaf_state , self.search_result_best_exp_util, terminated = search_alg(
                                initial_state = self.search_root_state,
                                util_fn = endgame_util_fn,
                                eval_fn = heuristic_eval_fn,
                                cutoff = float(self.cutoff_time_limit_spinbox.get()),
                                state_callback_fn =  self.alg_callback_blind if fly_blind  else self.alg_callback ,
                                counter = self.counter_dict,
                                random_move_order = bool(self.random_move_order_state.get()),
                                transposition_table = bool(self.transposition_table_state.get())
                                )
            elapsed_time = time() - search_start_time
            print("{} finished in {:.4f} seconds.".format(self.current_algorithm_name,elapsed_time))
            print('Nodes seen: {} | Endgame evals: {} | Cutoff evals: {}'.format(
                    self.counter_dict['num_nodes_seen'], self.counter_dict['num_endgame_evals'], self.counter_dict['num_heuristic_evals']))
            if None in (self.search_result_best_action, self.search_result_best_exp_util):
                self.update_status_and_ui(FINISHED_NO_RESULT)
            elif self.search_result_best_leaf_state == None and not bool(self.transposition_table_state.get()) and search_alg != ExpectimaxSearch:
                self.update_status_and_ui(FINISHED_NO_RESULT)
            elif (terminated is True):
                self.update_status_and_ui(FINISHED_INCOMPLETE)
            else:
                self.update_status_and_ui(FINISHED_COMPLETE)
        elif self.current_algorithm_name in PROGRESSIVE_ALGORITHMS:
            self.counter_dict = {'num_nodes_seen':[0], 'num_endgame_evals':[0], 'num_heuristic_evals':[0] }
            search_start_time = time()
            best_actions, best_leaf_nodes, best_exp_utils, max_cutoff = search_alg(
                                    initial_state = self.search_root_state,
                                    util_fn = endgame_util_fn,
                                    eval_fn = heuristic_eval_fn,
                                    time_limit = float(self.cutoff_time_limit_spinbox.get()),
                                    state_callback_fn =  self.alg_callback_blind  if fly_blind  else self.alg_callback , # A callback function for the GUI. If it returns True, terminate
                                    counter = self.counter_dict, # A counter for tracking stats
                                    random_move_order = bool(self.random_move_order_state.get()),
                                    transposition_table = bool(self.transposition_table_state.get())
                                    )
            elapsed_time = time() - search_start_time
            print("Progressive Deepening search results: ")
            for c in range(1,max_cutoff+1):
                print("Cutoff {}: Best action is {} at exp value {:.4f}.\n{} nodes seen, {} endgame evals, {} cutoff evals.".format(
                c, best_actions[c-1], best_exp_utils[c-1],
                self.counter_dict['num_nodes_seen'][c], self.counter_dict['num_endgame_evals'][c], self.counter_dict['num_heuristic_evals'][c]
                ))

            print('Total:\n Nodes seen: {} | Endgame evals: {} | Cutoff evals: {}'.format(
                    self.counter_dict['num_nodes_seen'][0], self.counter_dict['num_endgame_evals'][0], self.counter_dict['num_heuristic_evals'][0]))
            print("{} finished in {:.4f} seconds.".format(self.current_algorithm_name,elapsed_time))

            if any((l == None or len(l) < 1) for l in (best_actions, best_leaf_nodes, best_exp_utils)):
                self.update_status_and_ui(FINISHED_NO_RESULT)
                self.search_result_best_action, self.search_result_best_leaf_state , self.search_result_best_exp_util= None, None, None
            else:
                self.update_status_and_ui(FINISHED_COMPLETE)
                self.search_result_best_action , self.search_result_best_leaf_state , self.search_result_best_exp_util = best_actions[-1], best_leaf_nodes[-1], best_exp_utils[-1]


        elif self.current_algorithm_name in ASYMMETRIC_ALGORITHMS:
            self.counter_dict = {'num_simulations': 0}
            search_start_time = time()
            self.search_result_best_action, self.search_result_best_leaf_state , self.search_result_best_exp_util, num_simulations = search_alg(
                                    initial_state = self.search_root_state,
                                    util_fn = endgame_util_fn,
                                    exploration_bias = float(self.exploration_bias_state.get()) * sqrt(2),
                                    time_limit = float(self.cutoff_time_limit_spinbox.get()),
                                    state_callback_fn =  self.alg_callback_blind  if fly_blind  else self.alg_callback , # A callback function for the GUI. If it returns True, terminate
                                    counter = self.counter_dict # A counter for tracking stats
                                    )
            elapsed_time = time() - search_start_time
            print("{} finished in {:.4f} seconds.".format(self.current_algorithm_name,elapsed_time))
            print('Simulated Games: {}'.format(self.counter_dict['num_simulations']))
            if None in (self.search_result_best_action, self.search_result_best_leaf_state , self.search_result_best_exp_util):
                self.update_status_and_ui(FINISHED_NO_RESULT)
            else:
                self.update_status_and_ui(FINISHED_COMPLETE)



    def start_search(self, event = None, initial_status = SEARCHING_RUNNING, fly_blind = False):
        self.current_algorithm_name = self.get_alg_selection()
        self.current_endgame_util_fn = self.get_endgame_util_fn_selection()
        self.current_heuristic_eval_fn = self.get_heuristic_eval_fn_selection()

        self.update_status_and_ui(initial_status)
        if not self.verify_parameters(fly_blind):
            return
        try:
            self.search_root_state = self.current_state.clone_as_root()
            self.run_search(fly_blind)
            if self.search_result_best_action != None :
                self.visualize_state(self.search_root_state.generate_next_state(self.search_result_best_action)) #display the next best move.
                self.update_text(self.search_result_best_exp_util)
            else:
                self.visualize_state(self.search_root_state) #display the next best move.
        except Exception:
            print(format_exc())
            self.update_status_and_ui(SEARCH_ERROR)

    def restart_game(self, event = None) :
        if self.status in (INITIAL_WAITING,):
            self.current_state = self.initial_state
            self.visualize_state(self.current_state.clone_as_root())
            self.update_status_and_ui(INITIAL_WAITING)

    def terminate_search_or_discard_results(self, event = None) :
        if self.status in (FINISHED_COMPLETE, FINISHED_INCOMPLETE, FINISHED_COMPLETE_DISP_LEAF, FINISHED_INCOMPLETE_DISP_LEAF, FINISHED_NO_RESULT):
            self.visualize_state(self.search_root_state)
            self.update_status_and_ui(INITIAL_WAITING)
        elif  self.status in (SEARCHING_RUNNING, SEARCHING_PAUSED, SEARCHING_STEP):
            self.update_status_and_ui(TERMINATING_EARLY)


    def fly_blind_search(self, event = None):
        if self.status in (INITIAL_WAITING,):
            # if self.get_alg_selection() in ANYTIME_ALGORITHMS and self.cutoff_time_limit_spinbox.get() == "INF":
            #     self.status_text.set("Woah there - don't \"fly blind\" with INF time limit!")
            #     return
            self.start_search(initial_status = SEARCHING_RUNNING, fly_blind = True)

    def toggle_run_pause_or_play_move(self, event = None):
        if self.status in (INITIAL_WAITING,): # Run
            self.start_search(initial_status = SEARCHING_RUNNING)

        elif self.status in (SEARCHING_PAUSED, SEARCHING_STEP) : # Continue
            self.update_status_and_ui(SEARCHING_RUNNING)

        elif self.status in (SEARCHING_RUNNING, ) : # Pause
            self.update_status_and_ui(SEARCHING_PAUSED)

        elif self.status in (FINISHED_INCOMPLETE, FINISHED_COMPLETE, FINISHED_COMPLETE_DISP_LEAF, FINISHED_INCOMPLETE_DISP_LEAF): # Play move
            self.current_state = self.current_state.generate_next_state(self.search_result_best_action)
            self.visualize_state(self.current_state.clone_as_root())
            self.update_status_and_ui(INITIAL_WAITING)

    def step_or_toggle_display_action_leaf(self, event = None):
        if self.status in (INITIAL_WAITING,) : # Run + Step
            self.start_search(initial_status = SEARCHING_PAUSED)

        elif  self.status in (SEARCHING_RUNNING, SEARCHING_PAUSED) : # Step
            self.update_status_and_ui(SEARCHING_STEP)

        elif self.status in (FINISHED_COMPLETE,FINISHED_INCOMPLETE, FINISHED_COMPLETE_DISP_LEAF, FINISHED_INCOMPLETE_DISP_LEAF) : # Display Search Leaf

            goto = {FINISHED_COMPLETE: FINISHED_COMPLETE_DISP_LEAF, FINISHED_INCOMPLETE: FINISHED_INCOMPLETE_DISP_LEAF,
            FINISHED_COMPLETE_DISP_LEAF: FINISHED_COMPLETE, FINISHED_INCOMPLETE_DISP_LEAF : FINISHED_INCOMPLETE}

            self.update_status_and_ui(goto[self.status])

            if self.status in (FINISHED_COMPLETE, FINISHED_INCOMPLETE):
                self.visualize_state(self.search_root_state.generate_next_state(self.search_result_best_action)) #display the next best move.
            elif self.status in (FINISHED_COMPLETE_DISP_LEAF, FINISHED_INCOMPLETE_DISP_LEAF):
                self.visualize_state(self.search_result_best_leaf_state) #display the exp path.

    def undo_last_move(self, event = None):
        if self.status in (INITIAL_WAITING,):
            if self.current_state.get_parent() != None:
                self.current_state = self.current_state.get_parent()
                self.visualize_state(self.current_state.clone_as_root())
                self.update_status_and_ui(INITIAL_WAITING)

    def alg_callback(self, state, cur_value):
        self.run_pause_button.update()
        self.step_button.update()
        self.reset_button.update()
        self.visualize_extends_checkbox.update()
        self.print_status_checkbox.update()

        if self.print_status_state.get():
            self.update_text(cur_value)
        if self.visualize_extends_state.get() :
            self.visualize_state(state)

        while self.status == SEARCHING_PAUSED :
            sleep(.1)
            self.run_pause_button.update()
            self.step_button.update()
            self.reset_button.update()
            self.print_path_states_button.update()


        if self.status == SEARCHING_STEP:
            self.update_status_and_ui(SEARCHING_PAUSED)

        if self.status == SEARCHING_RUNNING :
            sleep(float(self.step_time_spinbox.get()))

        return (self.status == TERMINATING_EARLY)

    def alg_callback_blind (self, state, cur_value):
        return False

    def update_text(self, exp_util):
        if self.current_algorithm_name in PROGRESSIVE_ALGORITHMS:
            self.counter_text_1.set(
                'Max Depth {} : Nodes seen: {} | Endgame evals: {} | Cutoff evals: {}\n Total: Nodes seen: {} | Endgame evals: {} | Cutoff evals: {}'.format(
                    len(self.counter_dict['num_nodes_seen']) - 1, self.counter_dict['num_nodes_seen'][-1], self.counter_dict['num_endgame_evals'][-1], self.counter_dict['num_heuristic_evals'][-1],
                    self.counter_dict['num_nodes_seen'][0], self.counter_dict['num_endgame_evals'][0], self.counter_dict['num_heuristic_evals'][0]))
        elif self.current_algorithm_name in ASYMMETRIC_ALGORITHMS:
            self.counter_text_1.set(
                'Simulated Games: {}'.format(
                    self.counter_dict['num_simulations']))
        else:
            self.counter_text_1.set(
                'Nodes seen: {} | Endgame evals: {} | Cutoff evals: {}'.format(
                    self.counter_dict['num_nodes_seen'], self.counter_dict['num_endgame_evals'], self.counter_dict['num_heuristic_evals']))

        if exp_util != None:
            self.eval_fn_result_text.set('Expected utility of state: {:7.2f}'.format(exp_util))
        else :
            self.eval_fn_result_text.set('Expected utility of state: {:7s}'.format("TBD"))

    def toggle_display_history(self):
        if self.status == INITIAL_WAITING:
            if self.display_state is self.current_state:
                self.visualize_state(self.current_state.clone_as_root())
            else:
                self.visualize_state(self.current_state)

    def visualize_state(self, state):
        self.display_state = state
        self.draw_path_to_state()
        self.canvas.update()

    def click_canvas_attempt_action(self, event = None):
        if self.status == INITIAL_WAITING:
            action = self.click_canvas_to_action(event)
            if action in self.current_state.get_all_actions():
                self.current_state = self.current_state.generate_next_state(action)
                self.visualize_state(self.current_state.clone_as_root())
            self.status_text.set(STATUS_TEXT[INITIAL_WAITING].format(self.current_state.get_current_player()))


    def draw_path_to_state(self, event = None):
        raise NotImplementedError

    def draw_background(self, event = None):
        raise NotImplementedError

    def click_canvas_to_action(self, event = None):
        raise NotImplementedError

class RoombaRaceGUI(Lab2GUI_SEARCH):
    def __init__(self, master, current_state):
        master.title("Roomba Race Visualizer")
        self.game_class = RoombaRaceGameState
        self.maze_width = current_state.get_width()
        self.maze_height = current_state.get_height()

        self.endgame_util_fn_dict = all_fn_dicts[RoombaRaceGameState]['endgame_util_fn_dict']
        self.heuristic_eval_fn_dict = all_fn_dicts[RoombaRaceGameState]['heuristic_eval_fn_dict']

        self.text_size = MAX_HEIGHT // (self.maze_height * 2)
        super().__init__(master, initial_state, canvas_height = MAX_HEIGHT, canvas_width = MAX_HEIGHT * self.maze_width // self.maze_height )

    def calculate_box_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x1 = w * c // self.maze_width
        y1 = h * r // self.maze_height
        x2 = w * (c + 1) // self.maze_width
        y2 = h * (r + 1) // self.maze_height
        return (x1, y1, x2, y2)

    def calculate_center_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x = int(w * (c + .5)) // self.maze_width
        y = int(h * (r + .5)) // self.maze_height
        return (x, y)

    def draw_path_to_state(self, event = None):
        self.canvas.delete('path_line')
        self.canvas.delete('agent')
        self.canvas.delete('cleaned_terrain')

        path = self.display_state.get_path()

        # Draw cleaned terrain
        maze = self.current_state.get_grid()

        for r in range(0,self.maze_height):
            for c in range(0,self.maze_width):
                if maze[r][c] in CLEANED[1:]:
                    x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill= COLORS[maze[r][c]], tag='cleaned_terrain')

        for p in RoombaRaceGameState.player_numbers:
            curr_r, curr_c = self.display_state.get_position(p)
            x1, y1, x2, y2 = self.calculate_box_coords(curr_r,curr_c)
            self.canvas.create_oval(x1, y1, x2, y2, fill= COLORS[AGENT[p]], tag='agent')

            path_rc = [state.get_position(p) for state in path]
            path_coords = [self.calculate_center_coords(r,c)
                            for r,c in path_rc]
            if len(path_coords) > 1:
                self.canvas.create_line(path_coords, fill = COLORS[PATH[p]], width = 3, tag='path_line', )


    def draw_background(self, event = None):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas

        # Clear the background grid and terrain
        self.canvas.delete('grid_line')
        self.canvas.delete('terrain_block')

        # Creates all vertical lines
        for c in range(0, self.maze_width):
            x = w * c // self.maze_width
            self.canvas.create_line([(x, 0), (x, h)], tag='grid_line')

        # Creates all horizontal lines
        for r in range(0, self.maze_height):
            y = h * r // self.maze_height
            self.canvas.create_line([(0, y), (w, y)], tag='grid_line')

        # Draw terrain
        maze = self.initial_state.get_grid()
        for r in range(0,self.maze_height):
            for c in range(0,self.maze_width):
                terrain = maze[r][c]
                x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                self.canvas.create_rectangle(x1, y1, x2, y2, fill= COLORS[terrain], tag='terrain_block')

    def click_canvas_to_action(self, event):
        w = self.canvas.winfo_width() # Get current width of canvas
        col = event.x // (w //  self.maze_width)
        h = self.canvas.winfo_height() # Get current height of canvas
        row = event.y // (h //  self.maze_height)
        # print('clicked {}'.format(col))
        cur_r, cur_c = self.current_state.get_position(self.current_state.current_player)
        dr, dc = row - cur_r, col - cur_c
        return (dr, dc)


class TicTacToeGUI(Lab2GUI_SEARCH):
    def __init__(self, master, initial_state):
        master.title("Tic-Tac-Toe Search Visualizer")
        self.game_class = TicTacToeGameState
        self.num_rows = TicTacToeGameState.num_rows
        self.num_cols = TicTacToeGameState.num_cols
        self.text_size = MAX_HEIGHT // (self.num_rows * 2)
        self.margin = 5
        self.endgame_util_fn_dict = all_fn_dicts[TicTacToeGameState]['endgame_util_fn_dict']
        self.heuristic_eval_fn_dict = all_fn_dicts[TicTacToeGameState]['heuristic_eval_fn_dict']
        super().__init__(master, initial_state, canvas_height = MAX_HEIGHT, canvas_width = MAX_HEIGHT * self.num_cols // self.num_rows )

    def calculate_box_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x1 = w * c // self.num_cols
        y1 = h * r // self.num_rows
        x2 = w * (c + 1) // self.num_cols
        y2 = h * (r + 1) // self.num_rows
        return (x1, y1, x2, y2)

    def calculate_center_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x = int(w * (c + .5)) // self.num_cols
        y = int(h * (r + .5)) // self.num_rows
        return (x, y)

    def draw_path_to_state(self, event = None):
        self.canvas.delete('numbers')

        self.canvas.delete('pieces')
        self.canvas.delete('numbers')

        # draw pieces
        for r in range(0,self.num_rows):
            for c in range(0,self.num_cols):
                piece = self.display_state.get_piece_at(r,c)
                if piece != 0:
                    x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                    self.canvas.create_oval(x1 + self.margin, y1 + self.margin, x2 - self.margin, y2 - self.margin, fill= COLORS[PIECE_1 if piece == 1 else PIECE_2], tag='pieces')

        # draw text for path
        path_coords = [self.calculate_center_coords( *state.previous_action ) # r,c coordinates
                        for state in self.display_state.get_path()[1:] ]

        for i, pos in enumerate(path_coords): # don't do the first state
             self.canvas.create_text(pos, fill = COLORS[TEXT], tag = 'numbers',
                 text = str(i+1), font = ('Times New Roman', self.text_size, 'bold' ))

    def draw_background(self, event = None):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        # Clear the background grid frame and empty spots
        self.canvas.delete('grid_line')
        self.canvas.delete('frame')
        self.canvas.delete('empty')

        # Draw all the "frame" - really, background color
        self.canvas.create_rectangle(0, 0, w, h, fill= COLORS[FRAME], tag='frame')

        # Draw all the "empty spots"
        for r in range(0,self.num_rows):
            for c in range(0,self.num_cols):
                piece = self.display_state.get_piece_at(r,c)
                x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                self.canvas.create_oval(x1 + self.margin, y1 + self.margin, x2 - self.margin, y2 - self.margin, fill= COLORS[EMPTY], tag='empty')


        # Creates all vertical lines
        for c in range(0, self.num_cols):
            x = w * c // self.num_cols
            self.canvas.create_line([(x, 0), (x, h)], tag='grid_line', width = 2)

        # Creates all horizontal lines
        for r in range(0, self.num_rows):
            y = h * r // self.num_rows
            self.canvas.create_line([(0, y), (w, y)], tag='grid_line', width = 2)

    def click_canvas_to_action(self, event):
        w = self.canvas.winfo_width() # Get current width of canvas
        col = event.x // (w //  self.num_cols)
        h = self.canvas.winfo_height() # Get current height of canvas
        row = event.y // (h //  self.num_rows)
        return (row, col)

class NimGUI(Lab2GUI_SEARCH):
    def __init__(self, master, initial_state):
        master.title("Nim Search Visualizer")
        self.game_class = NimGameState
        self.num_rows = initial_state.get_num_piles()
        self.num_cols = max(initial_state.get_stones_in_pile(p) for p in range(self.num_rows))
        height = min(MAX_HEIGHT, self.num_rows * 60)
        self.text_size = height // (self.num_rows * 2)
        self.margin = 5
        self.endgame_util_fn_dict = all_fn_dicts[NimGameState]['endgame_util_fn_dict']
        self.heuristic_eval_fn_dict = all_fn_dicts[NimGameState]['heuristic_eval_fn_dict']
        super().__init__(master, initial_state, canvas_height = height, canvas_width = height * self.num_cols // self.num_rows )

    def calculate_box_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x1 = w * c // self.num_cols
        y1 = h * r // self.num_rows
        x2 = w * (c + 1) // self.num_cols
        y2 = h * (r + 1) // self.num_rows
        return (x1, y1, x2, y2)

    def calculate_center_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x = int(w * (c + .5)) // self.num_cols
        y = int(h * (r + .5)) // self.num_rows
        return (x, y)

    def draw_path_to_state(self, event = None):
        self.canvas.delete('pieces')
        self.canvas.delete('numbers')
        self.canvas.delete('STONE_pieces')

        # draw pieces
        for r in range(0,self.num_rows):
            for c in range(0,self.display_state.get_stones_in_pile(r)):
                x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                self.canvas.create_oval(x1 + self.margin, y1 + self.margin, x2 - self.margin, y2 - self.margin, fill= COLORS[STONE], tag='pieces')

        # draw text and colored ovals for STONE stones along path

        # for every action taken
        for i, state in enumerate(self.display_state.get_path()[1:]): # don't do the first state
            pile, rem_stones = state.previous_action
            orig_stones = state.parent.get_stones_in_pile(pile)
            player = state.parent.get_current_player()
            # draw over each stone
            for c in range(orig_stones - rem_stones, orig_stones):
                pos = self.calculate_center_coords(pile,c)
                x1, y1, x2, y2 = self.calculate_box_coords(pile,c)

                self.canvas.create_oval(x1 + self.margin, y1 + self.margin, x2 - self.margin, y2 - self.margin, fill= COLORS[PIECE_1 if player == 1 else PIECE_2], tag='STONE_pieces')

                self.canvas.create_text(pos, fill = COLORS[TEXT], tag = 'numbers',
                     text = str(i+1), font = ('Times New Roman', self.text_size, 'bold' ))

    def draw_background(self, event = None):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        # Clear the empty spots
        self.canvas.delete('empty')
        # Draw all the "empty spots"
        for r in range(0,self.num_rows):
            for c in range(0,self.initial_state.get_stones_in_pile(r)):
                pos = self.calculate_center_coords(r,c)
                x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                self.canvas.create_oval(x1 + self.margin, y1 + self.margin, x2 - self.margin, y2 - self.margin,  fill= '', outline = COLORS[STONE], width = 2, dash = (4,4), tag='empty')


    def click_canvas_to_action(self, event):
        w = self.canvas.winfo_width() # Get current width of canvas
        col = event.x // (w //  self.num_cols)
        h = self.canvas.winfo_height() # Get current height of canvas
        row = event.y // (h //  self.num_rows)
        # print('clicked {}'.format(col))
        pile = row
        rem_stones = self.current_state.get_stones_in_pile(pile) - col
        return (pile, rem_stones)


class ConnectFourGUI(Lab2GUI_SEARCH):
    def __init__(self, master, initial_state):
        master.title("Connect Four Search Visualizer")
        self.game_class = ConnectFourGameState
        self.num_rows = ConnectFourGameState.num_rows
        self.num_cols = ConnectFourGameState.num_cols
        self.text_size = MAX_HEIGHT // (self.num_rows * 2)
        self.margin = MAX_HEIGHT // (self.num_rows * 10)
        self.endgame_util_fn_dict = all_fn_dicts[ConnectFourGameState]['endgame_util_fn_dict']
        self.heuristic_eval_fn_dict = all_fn_dicts[ConnectFourGameState]['heuristic_eval_fn_dict']
        super().__init__(master, initial_state, canvas_height = MAX_HEIGHT, canvas_width = MAX_HEIGHT * self.num_cols // self.num_rows )

    def calculate_box_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x1 = w * c // self.num_cols
        y1 = h * r // self.num_rows
        x2 = w * (c + 1) // self.num_cols
        y2 = h * (r + 1) // self.num_rows
        return (x1, y1, x2, y2)

    def calculate_center_coords(self, r, c):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        x = int(w * (c + .5)) // self.num_cols
        y = int(h * (r + .5)) // self.num_rows
        return (x, y)

    def draw_path_to_state(self, event = None):
        self.canvas.delete('numbers')

        self.canvas.delete('pieces')
        self.canvas.delete('numbers')

        # draw pieces
        for r in range(0,self.num_rows):
            for c in range(0,self.num_cols):
                piece = self.display_state.get_piece_at(r,c)
                if piece != 0:
                    pos = self.calculate_center_coords(r,c)
                    x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                    self.canvas.create_oval(x1 + self.margin, y1 + self.margin, x2 - self.margin, y2 - self.margin, fill= COLORS[PIECE_1 if piece == 1 else PIECE_2], tag='pieces')

        # draw text for path
        path_coords = [self.calculate_center_coords(
                        self.num_rows -  state.get_column_height(state.previous_action) ,state.previous_action ) # r,c coordinates
                        for state in self.display_state.get_path()[1:] ]

        for i, pos in enumerate(path_coords): # don't do the first state
             self.canvas.create_text(pos, fill = COLORS[TEXT], tag = 'numbers',
                 text = str(i+1), font = ('Times New Roman', self.text_size, 'bold' ))

    def draw_background(self, event = None):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        # Clear the background grid frame and empty spots
        self.canvas.delete('grid_line')
        self.canvas.delete('frame')
        self.canvas.delete('empty')

        # Draw all the "frame" - really, background color
        self.canvas.create_rectangle(0, 0, w, h, fill= COLORS[FRAME], tag='frame')

        # Draw all the "empty spots"
        for r in range(0,self.num_rows):
            for c in range(0,self.num_cols):
                piece = self.display_state.get_piece_at(r,c)
                pos = self.calculate_center_coords(r,c)
                x1, y1, x2, y2 = self.calculate_box_coords(r,c)
                self.canvas.create_oval(x1 + self.margin, y1 + self.margin, x2 - self.margin, y2 - self.margin, fill= COLORS[EMPTY], tag='empty')


        # Creates all vertical lines
        for c in range(0, self.num_cols):
            x = w * c // self.num_cols
            self.canvas.create_line([(x, 0), (x, h)], tag='grid_line', width = 2)

        # Creates all horizontal lines
        for r in range(0, self.num_rows):
            y = h * r // self.num_rows
            self.canvas.create_line([(0, y), (w, y)], tag='grid_line', width = 2)


    def click_canvas_to_action(self, event):
        w = self.canvas.winfo_width() # Get current width of canvas
        col = event.x // (w //  self.num_cols)
        # print('clicked {}'.format(col))
        return col



GAME_CLASSES_AND_GUIS = {'roomba': (RoombaRaceGameState, RoombaRaceGUI),
                        'tictactoe': (TicTacToeGameState,TicTacToeGUI),
                        'connectfour': (ConnectFourGameState, ConnectFourGUI),
                        'nim': (NimGameState, NimGUI)}

if len(argv) < 3 :
    print("Usage:    python lab2_search_gui.py [GAME] [INITIAL_STATE_FILE]")
    print("          GAME can be " + " or ".join("'{}'".format(game) for game in GAME_CLASSES_AND_GUIS))
    print("          INITIAL_STATE_FILE is a path to a text file, OR \"default\"")
    quit()

root = Tk()

if argv[1] in GAME_CLASSES_AND_GUIS:
    game_class, GUI = GAME_CLASSES_AND_GUIS[argv[1]]
    initial_state = game_class.defaultInitialState() if argv[2] == 'default' else game_class.readFromFile(argv[2])
    gui = GUI(root, initial_state)
else :
    raise ValueError("First argument should be " + " or ".join("'{}'".format(game) for game in GAME_CLASSES_AND_GUIS))

root.mainloop()
