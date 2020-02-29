"""
Play games between 2 agents on the GUI

Usage:
    python lab2_play_gui.py [GAME] [INITIAL_STATE_FILE] [AGENT_1] [AGENT_2] ...")
    GAME can be tictactoe, nim, connectfour, or roomba
    INITIAL_STATE_FILE is a path to a text file or 'default'
    AGENT_# can be human, random, maxdfs, minimax, expectimax, alphabeta, progressive, or montecarlo
"""

from traceback import format_exc
from sys import argv
from time import time, sleep
from tkinter import * # Tk, Canvas, Frame, Listbox, Button, Checkbutton, IntVar, StringVar, Spinbox, Label
from lab2_algorithms import *
from gamestatenode import GameStateNode
from connectfour_gamestate import ConnectFourGameState
from tictactoe_gamestate import TicTacToeGameState
from nim_gamestate import NimGameState
from roomba_gamestate import RoombaRaceGameState, FLOOR, WALL, CLEANED
from game_playing_agents import *


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

CUTOFF_OPTIONS = tuple( ['INF'] + list(range(1,100)))

INITIAL_WAITING = 0
SEARCHING_RUNNING = 1
TERMINATING_EARLY = 4
FINISHED_COMPLETE = 5
FINISHED_NO_ACTION = 11
SEARCH_ERROR = -1


VALID_STATUS_TRANSITIONS = {
    None: (INITIAL_WAITING,),
    INITIAL_WAITING : (SEARCHING_RUNNING, INITIAL_WAITING, FINISHED_COMPLETE, TERMINATING_EARLY),
    SEARCHING_RUNNING : (TERMINATING_EARLY, FINISHED_COMPLETE, FINISHED_NO_ACTION, SEARCH_ERROR, INITIAL_WAITING),
    TERMINATING_EARLY : (FINISHED_COMPLETE,FINISHED_NO_ACTION,SEARCH_ERROR),
    FINISHED_COMPLETE : (INITIAL_WAITING,SEARCH_ERROR),
    FINISHED_NO_ACTION : (INITIAL_WAITING,SEARCH_ERROR),
    SEARCH_ERROR : tuple()
}

STATUS_TEXT = { INITIAL_WAITING: "[P{}] {}'s turn: Waiting...",
                SEARCHING_RUNNING:"[P{}] {}'s turn: Thinking...",
                TERMINATING_EARLY: "[P{}] {}'s turn: Giving up...",
                FINISHED_COMPLETE: "[P{}] {}'s turn: Move chosen!",
                FINISHED_NO_ACTION: "[P{}] {}'s turn: No move chosen, forfeits!",
                SEARCH_ERROR: "[P{}] {}'s turn: Something went wrong during search. Check the console for the exception stack trace."
                }

class Lab2GUI_PLAY:
    def __init__(self, master, initial_state, canvas_height, canvas_width, playing_agents):
        self.playing_agents = playing_agents
        self.current_player = initial_state.get_current_player()
        self.current_agent = playing_agents[self.current_player]

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

        if any(agent.show_thinking for agent in self.playing_agents.values()):

            status_output_settings_frame = Frame(master, padx = 3,width = 30)
            status_output_settings_frame.grid(row = 3, columnspan = 5,sticky = NW)

            self.step_time_label = Label(status_output_settings_frame, text = "Search Progress Settings:")
            self.step_time_label.grid(row= 0, columnspan = 3, sticky = N)

            self.visualize_extends_state = IntVar()
            self.visualize_extends_state.set(1)
            self.visualize_extends_checkbox = Checkbutton(status_output_settings_frame, text='Visualize search steps?', variable=self.visualize_extends_state)
            self.visualize_extends_checkbox.grid(row= 1, column = 1, sticky = NW)

            self.print_status_state = IntVar()
            self.print_status_state.set(1)
            self.print_status_checkbox = Checkbutton(status_output_settings_frame, text='Print search progress?', variable=self.print_status_state)
            self.print_status_checkbox.grid(row= 1, column = 2, sticky = NW)

            step_time_spinbox_frame = Frame(status_output_settings_frame)
            step_time_spinbox_frame.grid(row = 1, column = 0,sticky = NW)

            self.step_time_label = Label(step_time_spinbox_frame, text = "Step time: ")
            self.step_time_label.grid(row= 0, column = 0, sticky = NW)

            self.step_time_spinbox = Spinbox(step_time_spinbox_frame,
            values=STEP_TIME_OPTIONS, format="%3.2f", width = 4)
            self.step_time_spinbox.grid(row= 0, column = 1, sticky = NW)
            while(self.step_time_spinbox.get() != "0.1") :
                self.step_time_spinbox.invoke('buttonup')


        ###############################################################
        # Run the game - correct loop?
        self.continue_game()

    def continue_game(self):
        self.visualize_state(self.current_state.clone_as_root())
        while not self.current_state.is_endgame_state():
            self.current_player = self.current_state.get_current_player()
            self.current_agent = self.playing_agents[self.current_player]
            self.update_status_and_ui(INITIAL_WAITING)
            try:
                self.search_root_state = self.current_state.clone_as_root()
                start_time = time()
                if not self.run_agent_choose_action(): # break if human player
                    return # wait for him to pick a move and resume the game
                time_elapsed = time() - start_time
                if time_elapsed < 1:
                    sleep(1 - time_elapsed)

                if self.search_result_best_action != None and self.status != TERMINATING_EARLY:
                    self.visualize_state(self.search_root_state.generate_next_state(self.search_result_best_action)) #display the next best move.
                    self.update_text(self.search_result_best_exp_util)
                    self.update_status_and_ui(FINISHED_COMPLETE)
                    sleep(1)
                    self.current_state = self.current_state.generate_next_state(self.search_result_best_action)
                    self.visualize_state(self.current_state.clone_as_root())
                else:
                    self.update_status_and_ui(FINISHED_NO_ACTION)
                    break

            except Exception:
                print(format_exc())
                self.update_status_and_ui(SEARCH_ERROR)
                break


        if self.current_state.is_endgame_state():
            self.update_status_and_ui(INITIAL_WAITING)
            winning_player = self.current_state.endgame_winner()
            if winning_player != 0:
                self.status_text.set("[P{}] {} wins!".format(winning_player, self.playing_agents[winning_player].name))
            else :
                self.status_text.set("It's a tie!")
            self.master.update()

    def run_agent_choose_action(self):
        # Human Agent
        if type(self.current_agent) is HumanTextInputAgent:
            self.search_result_best_exp_util = None
            self.search_result_best_action = None
            return False

        # AI agents
        if self.current_agent.search_alg in CLASSIC_ALGORITHMS.values():
            self.counter_dict =  {'num_nodes_seen':0, 'num_endgame_evals':0, 'num_heuristic_evals':0 }
        elif self.current_agent.search_alg in PROGRESSIVE_ALGORITHMS.values():
            self.counter_dict =  {'num_nodes_seen':[0], 'num_endgame_evals':[0], 'num_heuristic_evals':[0]}
        elif self.current_agent.search_alg in ASYMMETRIC_ALGORITHMS.values():
            self.counter_dict = {'num_simulations': 0}

        callback = self.alg_callback if (self.current_agent.show_thinking) else self.alg_callback_blind

        self.update_status_and_ui(SEARCHING_RUNNING)
        self.search_result_best_action, self.search_result_best_exp_util = self.current_agent.choose_action(self.search_root_state,
            state_callback_fn = callback,
            counter = self.counter_dict)
        return True

    def is_human_turn(self):
        return type(self.current_agent) == HumanTextInputAgent

    def update_status_and_ui(self, newstatus = INITIAL_WAITING):
        if newstatus == self.status: # No change?
            return

        assert newstatus in VALID_STATUS_TRANSITIONS[self.status]


        self.status = newstatus
        self.status_text.set(STATUS_TEXT[self.status].format(self.current_player, self.current_agent.name))

        if newstatus == INITIAL_WAITING :
            self.restart_button['text'] = "Restart Game"
            self.restart_button['state'] = NORMAL
            self.restart_button['bg'] = 'orange red'
            self.undo_move_button['state'] = NORMAL if self.is_human_turn() else DISABLED
            self.undo_move_button['bg'] = 'DodgerBlue2'  if self.is_human_turn() else 'grey'
            self.history_button['state'] = NORMAL
            self.history_button['bg'] = 'orchid1'

        elif newstatus in (SEARCHING_RUNNING,):
            self.restart_button['text'] = "Terminate Turn"
            self.undo_move_button['state'] = DISABLED
            self.undo_move_button['bg'] = 'grey'
            self.history_button['state'] = DISABLED
            self.history_button['bg'] = 'grey'


        elif newstatus in (TERMINATING_EARLY,):
            self.restart_button['state'] = DISABLED
            self.restart_button['bg'] = 'grey'
            self.history_button['state'] = DISABLED
            self.history_button['bg'] = 'grey'

        elif newstatus in (FINISHED_NO_ACTION,) :
            self.restart_button['text'] = "Restart Game"
            self.restart_button['state'] = NORMAL
            self.restart_button['bg'] = 'orange red'
            self.undo_move_button['state'] = DISABLED
            self.undo_move_button['bg'] = 'grey'
            self.history_button['state'] = DISABLED
            self.history_button['bg'] = 'grey'

        elif newstatus in (FINISHED_COMPLETE,) :
            self.restart_button['text'] = "Restart Game"
            self.restart_button['state'] = NORMAL
            self.restart_button['bg'] = 'orange red'
            self.undo_move_button['state'] = DISABLED
            self.undo_move_button['bg'] = 'grey'
            self.history_button['state'] = DISABLED
            self.history_button['bg'] = 'grey'

        elif newstatus in (SEARCH_ERROR,):
            self.restart_button['state'] = DISABLED
            self.restart_button['bg'] = 'grey'
            self.undo_move_button['state'] = DISABLED
            self.undo_move_button['bg'] = 'grey'
            self.history_button['state'] = DISABLED
            self.history_button['bg'] = 'grey'

        self.master.update()
        return newstatus


    def restart_game(self, event = None) :
        if self.status in (INITIAL_WAITING,FINISHED_COMPLETE, FINISHED_NO_ACTION):
            self.current_state = self.initial_state
            self.visualize_state(self.current_state.clone_as_root())
            self.update_status_and_ui(INITIAL_WAITING)
            self.continue_game()
        elif self.status in (SEARCHING_RUNNING,):
            self.update_status_and_ui(TERMINATING_EARLY)

    def undo_last_move(self, event = None):
        if self.status in (INITIAL_WAITING,):
            if self.current_state.get_parent() != None:
                # back to last human turn
                self.current_state = self.current_state.get_parent()
                self.current_player = self.current_state.get_current_player()
                self.current_agent = self.playing_agents[self.current_player]
                while not self.is_human_turn():
                    self.current_state = self.current_state.get_parent()
                    self.current_player = self.current_state.get_current_player()
                    self.current_agent = self.playing_agents[self.current_player]

                self.continue_game()

    def alg_callback(self, state, cur_value):
        self.restart_button.update()
        self.visualize_extends_checkbox.update()
        self.print_status_checkbox.update()

        if self.print_status_state.get():
            self.update_text(cur_value)
        if self.visualize_extends_state.get() :
            self.visualize_state(state)
        if self.status == SEARCHING_RUNNING :
            sleep(float(self.step_time_spinbox.get()))

        return (self.status == TERMINATING_EARLY)

    def alg_callback_blind (self, state, cur_value):
        return False

    def update_text(self, exp_util):
        if self.is_human_turn():
            self.counter_text_1.set("")
            self.eval_fn_result_text.set('Expected utility of state: {:7s}'.format('????'))
            return

        if self.current_agent.search_alg in PROGRESSIVE_ALGORITHMS.values():
            self.counter_text_1.set(
                'Max Depth {} : Nodes seen: {} | Endgame evals: {} | Cutoff evals: {}\n Total: Nodes seen: {} | Endgame evals: {} | Cutoff evals: {}'.format(
                    len(self.counter_dict['num_nodes_seen']) - 1, self.counter_dict['num_nodes_seen'][-1], self.counter_dict['num_endgame_evals'][-1], self.counter_dict['num_heuristic_evals'][-1],
                    self.counter_dict['num_nodes_seen'][0], self.counter_dict['num_endgame_evals'][0], self.counter_dict['num_heuristic_evals'][0]))
        elif self.current_agent.search_alg in ASYMMETRIC_ALGORITHMS.values():
            self.counter_text_1.set(
                'Simulated Games: {}'.format(
                    self.counter_dict['num_simulations']))
        elif self.current_agent.search_alg in CLASSIC_ALGORITHMS.values():
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
            self.master.update()

    def visualize_state(self, state):
        self.display_state = state
        self.draw_path_to_state()
        self.canvas.update()

    def click_canvas_attempt_action(self, event = None):
        if self.status == INITIAL_WAITING and self.is_human_turn():
            action = self.click_canvas_to_action(event)
            if action in self.current_state.get_all_actions():
                player_action = action

            if player_action != None :

                self.update_status_and_ui(FINISHED_COMPLETE)
                self.visualize_state(self.current_state.clone_as_root().generate_next_state(player_action)) #display the next best move.
                self.update_text(self.search_result_best_exp_util)
                sleep(1)
                self.current_state = self.current_state.generate_next_state(player_action)
                self.visualize_state(self.current_state.clone_as_root())
            else:
                self.update_status_and_ui(FINISHED_NO_ACTION)
            self.continue_game()




    def draw_path_to_state(self, event = None):
        raise NotImplementedError

    def draw_background(self, event = None):
        raise NotImplementedError

    def click_canvas_to_action(self, event = None):
        raise NotImplementedError

class RoombaRaceGUI(Lab2GUI_PLAY):
    def __init__(self, master, current_state, playing_agents):
        master.title("Roomba Race Visualizer")
        self.game_class = RoombaRaceGameState
        self.maze_width = current_state.get_width()
        self.maze_height = current_state.get_height()

        self.endgame_util_fn_dict = all_fn_dicts[RoombaRaceGameState]['endgame_util_fn_dict']
        self.heuristic_eval_fn_dict = all_fn_dicts[RoombaRaceGameState]['heuristic_eval_fn_dict']

        self.text_size = MAX_HEIGHT // (self.maze_height * 2)
        super().__init__(master, initial_state, canvas_height = MAX_HEIGHT, canvas_width = MAX_HEIGHT * self.maze_width // self.maze_height, playing_agents = playing_agents)

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


class TicTacToeGUI(Lab2GUI_PLAY):
    def __init__(self, master, initial_state, playing_agents):
        master.title("Tic-Tac-Toe Search Visualizer")
        self.game_class = TicTacToeGameState
        self.num_rows = TicTacToeGameState.num_rows
        self.num_cols = TicTacToeGameState.num_cols
        self.text_size = MAX_HEIGHT // (self.num_rows * 2)
        self.margin = 5
        self.endgame_util_fn_dict = all_fn_dicts[TicTacToeGameState]['endgame_util_fn_dict']
        self.heuristic_eval_fn_dict = all_fn_dicts[TicTacToeGameState]['heuristic_eval_fn_dict']
        super().__init__(master, initial_state, canvas_height = MAX_HEIGHT, canvas_width = MAX_HEIGHT * self.num_cols // self.num_rows , playing_agents = playing_agents)

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

class NimGUI(Lab2GUI_PLAY):
    def __init__(self, master, initial_state, playing_agents):
        master.title("Nim Search Visualizer")
        self.game_class = NimGameState
        self.num_rows = initial_state.get_num_piles()
        self.num_cols = max(initial_state.get_stones_in_pile(p) for p in range(self.num_rows))
        height = min(MAX_HEIGHT, self.num_rows * 60)
        self.text_size = height // (self.num_rows * 2)
        self.margin = 5
        self.endgame_util_fn_dict = all_fn_dicts[NimGameState]['endgame_util_fn_dict']
        self.heuristic_eval_fn_dict = all_fn_dicts[NimGameState]['heuristic_eval_fn_dict']
        super().__init__(master, initial_state, canvas_height = height, canvas_width = height * self.num_cols // self.num_rows ,playing_agents = playing_agents)

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


class ConnectFourGUI(Lab2GUI_PLAY):
    def __init__(self, master, initial_state, playing_agents):
        master.title("Connect Four Search Visualizer")
        self.game_class = ConnectFourGameState
        self.num_rows = ConnectFourGameState.num_rows
        self.num_cols = ConnectFourGameState.num_cols
        self.text_size = MAX_HEIGHT // (self.num_rows * 2)
        self.margin = MAX_HEIGHT // (self.num_rows * 10)
        self.endgame_util_fn_dict = all_fn_dicts[ConnectFourGameState]['endgame_util_fn_dict']
        self.heuristic_eval_fn_dict = all_fn_dicts[ConnectFourGameState]['heuristic_eval_fn_dict']
        super().__init__(master, initial_state, canvas_height = MAX_HEIGHT, canvas_width = MAX_HEIGHT * self.num_cols // self.num_rows, playing_agents = playing_agents)

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


PLAYING_AGENTS = {"human":HumanTextInputAgent, "random":RandChoiceAgent,
                    "maxdfs": MaximizingDFSAgent, "minimax":MinimaxSearchAgent,
                    "expectimax": ExpectimaxSearchAgent, "alphabeta": MinimaxAlphaBetaSearchAgent,
                    "progressive":ProgressiveDeepeningSearchAgent, "montecarlo":MonteCarloTreeSearchAgent}

if len(argv) < 2 :
    print("Usage:    python lab2_play_gui.py [GAME] [INITIAL_STATE_FILE] [AGENT_1] [AGENT_2] ...")
    print("          GAME can be " + " or ".join("'{}'".format(game) for game in GAME_CLASSES_AND_GUIS))
    print("          INITIAL_STATE_FILE is a path to a text file, OR \"default\"")
    print("          AGENT_# should be one of the following: {}".format(str(list(PLAYING_AGENTS.keys()))))

    quit()

if (argv[1] not in GAME_CLASSES_AND_GUIS):
    print("1st argument should be one of the following: {}".format(str(list(GAME_CLASSES_AND_GUIS.keys()))))
    quit()

game_class, GUI = GAME_CLASSES_AND_GUIS[argv[1]]

initial_state = game_class.defaultInitialState() if argv[2] == 'default' else game_class.readFromFile(argv[2])
player_nums = game_class.player_numbers
agent_args =  argv[3:3+len(player_nums)]

if (len(agent_args) < len(player_nums)) or any(s not in PLAYING_AGENTS for s in agent_args):
    print("Final {} arguments choose agents for each player: {}".format(len(player_nums), str(list(PLAYING_AGENTS.keys()))))
    quit()

# Set up agents

playing_agents = {p : PLAYING_AGENTS[s](game_class) for p,s in zip(player_nums, agent_args)}

for p in playing_agents:
    agent = playing_agents[p]
    print("Setting up Player {} ({}):".format(p, agent.name))
    agent.set_up(GUI = True)


root = Tk()
gui = GUI(root, initial_state, playing_agents)
root.mainloop()
