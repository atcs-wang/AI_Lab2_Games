# Lab 2: Games (Connect-4, Roomba Race)
# Name(s): Mr. Wang
# Email(s): matwan@bergen.org

from connectfour_gamestate import ConnectFourGameState
from tictactoe_gamestate import TicTacToeGameState
from nim_gamestate import NimGameState
from roomba_gamestate import RoombaRaceGameState

"""
Some useful built-in python methods:
    any(list-like) - returns if at least one True
    all(list-like) - returns if all are True
    sum(list-like) - returns sum of all (??)
    listobj.count(item) - returns count of items in list

"""

## General purpose evaluation functions: ###########

def basic_endgame_utility(state, maximizer_player_num):
    """ Given an endgame state and the player number of the "maximizer",
    returns utility 1000 if the maximizer has won,
    -1000 if the minimizer has won, or 0 in case of a tie.
    """
    winner = state.endgame_winner()
    if winner == 0:
        return 0
    elif winner ==  maximizer_player_num:
        return 1000
    else:
        return -1000

def faster_endgame_utility(state, maximizer_player_num):
    """ Given an endgame state and the player number of the "maximizer",
    returns 0 in case of a tie, or a utility with abs(score) >= 1000,
    returning larger absolute scores for winning/losing sooner.
    This incentivizes winning more quickly, and losing later.
    """
    winner = state.endgame_winner()
    if winner == 0:
        return 0
    elif winner ==  maximizer_player_num:
        return 1000 + (1 / (state.get_path_length()))
    else:
        return -(1000 + (1 / (state.get_path_length())))



def always_zero(state, maximizer_player_num):
    """ Always returns zero.
    Works as a dummy heuristic evaluation function for any situation.
    Truly useful heuristic evaluation functions must almost always be game-specific!
    """
    return 0


## Nim specific evaluation functions: ###########

def empty_rows_eval_nim(state, maximizer_player_num):
    """ Given a non-endgame NimGameState, estimate the value
    (expected utility) of the state from maximizer_player_num's view.

    Return the fraction of rows that are empty. The more empty rows, the better.
    This is not a zero-sum evaluation - both max and min get the same est. utility.
    Still, this can be helpful because usually forcing rows to empty is good.
    """
    return [state.get_stones_in_pile(p) for p in range(state.get_num_piles())].count(0) / state.get_num_piles()

nim_functions = {
    "endgame_util_fn_dict" : {"basic": basic_endgame_utility,
                         "faster": faster_endgame_utility},

    "heuristic_eval_fn_dict" : {"zero": always_zero,
                                "empty rows": empty_rows_eval_nim}
}


## TicTacToe specific evaluation functions: ###########

## Edges are valued least, center valued highest.
space_values_tictactoe = {  (0,0):2, (0,1):1, (0,2):2,
                            (1,0):1, (1,1):3, (1,2):1,
                            (2,0):2, (2,1):1, (2,2):2}

def space_values_eval_tictactoe(state, maximizer_player_num):
    """ Given a non-endgame TicTacToeGameState, estimate the value
    (expected utility) of the state from maximizer_player_num's view.

    Return a linearly weighted sum of the "value" of each piece's position.
    Maximizer's pieces are + value, Minimizer's pieces are - value.
    """
    eval_score = 0
    for r in range(TicTacToeGameState.num_rows):
        for c in range(TicTacToeGameState.num_cols):
            piece = state.board_array[r][c]
            if piece == 0:
                continue
            elif piece == maximizer_player_num:
                eval_score += space_values_tictactoe[(r,c)]
            else:
                eval_score -= space_values_tictactoe[(r,c)]
    return eval_score

def win_paths_eval_tictactoe(state, maximizer_player_num):
    """ Given a non-endgame TicTacToeGameState, estimate the value
    (expected utility) of the state from maximizer_player_num's view.

    Return the difference in the number of possible winning paths for
    each player. More precisely:
    Return E(n) = M(n) - O(n)
    where M(n) is the total of Maximizer's possible winning lines
    O(n) is the total of Minimizer's possible winning lines.
    """

    def seq_paths(seq):
        if not any(p == minimizer_player_num for p in seq):
            return 1
        if not any(p == maximizer_player_num  for p in seq):
            return -1
        return 0

    eval_score = 0
    minimizer_player_num = maximizer_player_num % 2 + 1
    # horizontal
    for r in range(TicTacToeGameState.num_rows):
        eval_score += seq_paths([state.board_array[r][c] for c in range(TicTacToeGameState.num_cols)])
    # vertical
    for c in range(TicTacToeGameState.num_cols):
        eval_score += seq_paths([state.board_array[r][c] for r in range(TicTacToeGameState.num_rows)])

    # diagonal down-right
    eval_score += seq_paths([state.board_array[i][i] for i in range(TicTacToeGameState.num_cols)])

    # diagonal up-right
    eval_score += seq_paths([state.board_array[TicTacToeGameState.num_rows - i - 1][i] for i in range(TicTacToeGameState.num_cols)])

    return eval_score

tictactoe_functions = {
    "endgame_util_fn_dict" : {"basic": basic_endgame_utility,
                         "faster": faster_endgame_utility},

    "heuristic_eval_fn_dict" : {"zero": always_zero,
                                "space values": space_values_eval_tictactoe,
                                "win paths": win_paths_eval_tictactoe}
}

## Connect-four specific evaluation functions: ###########

chain_scores = {0:0, 1:1, 2:3, 3:10, 4:100, -1:-1, -2:-3, -3:-10, -4:-100}
def score_chains_connectfour(state, maximizer_player_num):
    """
    Given a non-endgame ConnectFourGameState, estimate the value
    (expected utility) of the state
    from maximizer_player_num's view.

    Utilizes the number of piece chains found for both players.
    """
    score = 0
    minimizer_player_num = maximizer_player_num %2 + 1
    for chain_len in range(1,4):
        score += state.get_num_chains(chain_len,maximizer_player_num) * chain_scores[chain_len]
        score -= state.get_num_chains(chain_len, minimizer_player_num) * chain_scores[chain_len]
    return score


def count_open_sequence(seq, maximizer_player_num):
    """
    Given a list of piece numbers and 0s, seq:
    If only open spaces and maximizer pieces, return how many pieces.
    If only open spaces and minimizer pieces, return negative how many pieces.
    If any mix of maximizer or minimizer pieces, return 0.
    """
    count = 0
    for piece in seq:
        if piece == 0:
            continue
        elif piece == maximizer_player_num:
            if count >= 0:
                count += 1
            else :
                return 0
        else :
            if count <= 0:
                count -= 1
            else :
                return 0
    return count


open_path_scores = {0:0, 1:1, 2:3, 3:10, 4:100, -1:-1, -2:-3, -3:-10, -4:-100}
win_len = 4
def open_paths_connectfour(state, maximizer_player_num):
    """
    Given a non-endgame ConnectFourGameState, estimate the value
    (expected utility) of the state
    from maximizer_player_num's view.

    Uses
    """
    total_score = 0
    counts = [0 for i in range(-4,4)]
    # Horizontal seqeuences
    # Each leftmost position of a horizontal 4 sequence
    for r in range(ConnectFourGameState.num_rows):
        for c in range(ConnectFourGameState.num_cols - win_len + 1):
            seq = [state.board_array[r][c+i] for i in range(win_len)]
            counts[count_open_sequence(seq, maximizer_player_num)] += 1
    # Vertical seqeuences
    # Each uppermost position of a vertical 4 sequence
    for c in range(ConnectFourGameState.num_cols):
        for r in range(ConnectFourGameState.num_rows - win_len + 1):
            seq = [state.board_array[r+i][c] for i in range(win_len)]
            counts[count_open_sequence(seq, maximizer_player_num)] += 1
    # Diagonal down-right seqeuences
    # Each leftmost position of a diagonal down 4 sequence
    for r in range(ConnectFourGameState.num_rows - win_len + 1):
        for c in range(ConnectFourGameState.num_cols - win_len + 1):
            seq = [state.board_array[r+i][c+i] for i in range(win_len)]
            counts[count_open_sequence(seq, maximizer_player_num)] += 1
    # Diagonal up seqeuences
    # Each leftmost position of a diagonal up-right 4 sequence
    for r in range(win_len - 1, ConnectFourGameState.num_rows):
        for c in range(ConnectFourGameState.num_cols - win_len + 1):
            seq = [state.board_array[r-i][c+i] for i in range(win_len)]
            counts[count_open_sequence(seq, maximizer_player_num)] += 1
    # Sum up scores
    for i in range(-4,4):
        total_score += counts[i] * open_path_scores[i]
    return total_score

connectfour_functions = {
    "endgame_util_fn_dict" : {"basic": basic_endgame_utility,
                            "faster": faster_endgame_utility},

    "heuristic_eval_fn_dict" : {"zero": always_zero,
                              "simple heuristic": score_chains_connectfour,
                              "advanced heuristic": open_paths_connectfour}
}


## Roomba Race specific evaluation functions: ###########




def manhattan_distance_between_players(state):
    max_r, max_c = state.get_position(1)
    min_r, min_c = state.get_position(2)
    return abs(max_r - min_r) + abs(max_c - min_c)

def freedom_eval_roomba(state, maximizer_player_num):
    """ Given a non-endgame RoombaRaceGameState, estimate the value
    (expected utility) of the state
    from maximizer_player_num's view.

    The more degrees of freedom (available actions) for me (maximizer) and less for
    opponent, the better. Depends on turn.
    """
    # if state.current_player == maximizer_player_num:
    #     return len(state.get_all_actions()) / 4
    # else :
    #     return - len(state.get_all_actions()) / 4
    minimizer_player_num = maximizer_player_num %2 + 1
    grid = state.get_grid()
    width = state.get_width()
    height = state.get_height()
    def local_freedom_bfs(r, c, depth, visited_set):
        if (r >= height or r < 0 or c >= width or c < 0 or
            (r,c) in visited_set or grid[r][c] != '.'):
            return

        visited_set.add((r,c))
        if depth > 0:
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                local_freedom_bfs(r + dr, c + dc, depth - 1, visited_set)

    max_r, max_c = state.get_position(maximizer_player_num)
    min_r, min_c = state.get_position(minimizer_player_num)
    p_dist = manhattan_distance_between_players(state)

    diff = 0
    start_dist = max(4,p_dist)
    dist = start_dist
    while diff == 0 and dist < (start_dist + 5):
        nearby_open = set()
        local_freedom_bfs(max_r, max_c, dist , nearby_open)
        max_freedom = len(nearby_open)
        
        nearby_open = set()
        local_freedom_bfs(min_r, min_c, dist, nearby_open)
        min_freedom = len(nearby_open)

        diff = max_freedom - min_freedom
        dist += 1
    return diff    


def minimize_distance_eval_roomba(state, maximizer_player_num):
    """
    Given a non-endgame RoombaRaceGameState, estimate the value
    (expected utility) of the state
    from maximizer_player_num's view.

    The closer to the opponent, the better.
    """
    return 500 - manhattan_distance_between_players(state)


roomba_functions = {
    "endgame_util_fn_dict" : {"basic": basic_endgame_utility,
                         "faster": faster_endgame_utility},

    "heuristic_eval_fn_dict" : {"zero": always_zero,
                                "aggression": minimize_distance_eval_roomba,
                                "freedom": freedom_eval_roomba}
}



## Dictionary mapping games to their appropriate evaluation functions. Used by the GUIs
all_fn_dicts = { RoombaRaceGameState: roomba_functions,
    ConnectFourGameState: connectfour_functions,
    TicTacToeGameState: tictactoe_functions,
    NimGameState: nim_functions}
