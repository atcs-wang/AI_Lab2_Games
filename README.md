A educational visualizer for Game Tree Search algorithms, including
- Minimax, Alpha-Beta pruning, (Uniform) Expectimax, and Monte Carlo Tree Search.
- tree, iterative deepening, limited depth, and anytime variants. 

The game tree model (`gamestatenode.py`), agents (`game_playing_agents.py`), game algorithms (`lab2_algorithms.py`, and runners (remaining `lab2_` prefixed files) are all abstractly generalized; the other files with `_gamestate.py` suffixes refer to concrete game models that inherit from the abstract game tree model.

These concrete environments include:
- `connectfour` 
- `tictactoe`
- `nim` - take rocks from piles until all rocks are gone
- `roomba` - a "tron lightbike"-like game

To run one of the visualizers, use one of the following commands

1. To run a game in a GUI between two agents:
  ```
  > python lab2_play_gui.py [GAME] [INITIAL_STATE_FILE] [AGENT_1] [AGENT_2]
  ```
2. To run a game in the console between two agents:
  ```
  > python lab2_play_text.py [GAME] [INITIAL_STATE_FILE] [AGENT_1] [AGENT_2]
  ```
3. To run various algorithms in a more freely choosable manner suitable for testing, debugging, and demonstration:
  ```
  > python lab2_test_gui.py [GAME] [INITIAL_STATE_FILE]
  ```

> The command line arguments:
> 
> `[GAME]` can be 'roomba' or 'tictactoe' or 'connectfour' or 'nim'
>
> `[INITIAL_STATE_FILE]` is a path to a text file, OR "default". Several valid files are in the `initial_states` folder.
>
> `[AGENT_#]` should be one of the following: ['human', 'random', 'maxdfs', 'minimax', 'expectimax', 'alphabeta', 'progressive', 'montecarlo']
>
> If the command line arguments are omitted, you will be prompted with similar instructions.





Can be used as an assignment, by replacing any files with versions of the files in the `assignment_starter_files`. 
