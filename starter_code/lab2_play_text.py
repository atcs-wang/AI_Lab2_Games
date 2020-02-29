"""
Play games between 2 agents on the console with text

Usage:
    python lab2_play_text.py [GAME] [INITIAL_STATE_FILE] [AGENT_1] [AGENT_2] ...")
    GAME can be tictactoe, nim, connectfour, or roomba
    INITIAL_STATE_FILE is a path to a text file or 'default'
    AGENT_# can be human, random, maxdfs, minimax, expectimax, alphabeta, progressive, or montecarlo
"""
from sys import argv
from time import sleep, time
from connectfour_gamestate import ConnectFourGameState
from tictactoe_gamestate import TicTacToeGameState
from nim_gamestate import NimGameState
from roomba_gamestate import RoombaRaceGameState
from game_playing_agents import *

GAME_CLASSES = {"connectfour":ConnectFourGameState, "tictactoe": TicTacToeGameState, "nim": NimGameState, "roomba": RoombaRaceGameState}

PLAYING_AGENTS = {"human":HumanTextInputAgent, "random":RandChoiceAgent,
                    "maxdfs": MaximizingDFSAgent, "minimax":MinimaxSearchAgent,
                    "expectimax": ExpectimaxSearchAgent, "alphabeta": MinimaxAlphaBetaSearchAgent,
                    "progressive":ProgressiveDeepeningSearchAgent, "montecarlo":MonteCarloTreeSearchAgent}

if len(argv) < 2 :
    print("Usage:    python lab2_play_text.py [GAME] [INITIAL_STATE_FILE] [AGENT_1] [AGENT_2] ...")
    print("          GAME can be " + " or ".join("'{}'".format(game) for game in gamestates_and_guis))
    print("          INITIAL_STATE_FILE is a path to a text file, OR \"default\"")
    print("          AGENT_# should be one of the following: {}".format(str(list(PLAYING_AGENTS.keys()))))

    quit()

if (argv[1] not in GAME_CLASSES):
    print("1st argument should be one of the following: {}".format(str(list(GAME_CLASSES.keys()))))
    quit()

game_class = GAME_CLASSES[argv[1]]

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
    agent.set_up()

# Run the game
game_state = initial_state
print(game_state)
while not game_state.is_endgame_state():

    current_player = game_state.get_current_player()
    current_agent = playing_agents[current_player]
    print("[P{}] {}'s turn:".format(current_player, current_agent.name))

    start_time = time()
    action, exp_util = current_agent.choose_action(game_state)

    time_elapsed = time() - start_time
    if time_elapsed < 1:
        sleep(1 - time_elapsed)

    if action == None:
        print("[P{}] {} forfeits!".format(current_player, current_agent.name))
        quit()
    print("[P{}] {} chooses {}".format(current_player, current_agent.name, game_class.action_to_pretty_str(action)))

    game_state = game_state.generate_next_state(action)
    print(game_state)

winning_player = game_state.endgame_winner()
if winning_player != 0:
    print("[P{}] {} wins!".format(winning_player, playing_agents[winning_player].name))
else :
    print("It's a tie!")
