from game_classes.game import Game
import cProfile
from game_classes.game_logic import Logic
from game_classes import settings
from pprint import pprint
import json
from timeit import default_timer as timer
import debugpy

# 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
# debugpy.listen(5678)
# print("Waiting for debugger attach")
# debugpy.wait_for_client()

settings.init()
settings.set_debug(True)

game = Game()
game.calculate_legal_moves()

max_iters = 3
depth = 2
player_index = len(game.move_history) % 2
move_tree = Logic.greedy_search(
    game.board,
    game.move_history,
    game.material,
    game.players[player_index],
    game.players[1-player_index],
    game.game_status,
    max_iters,
    depth
)

# pprint(move_tree)
# while 'best_move' in move_tree and move_tree['best_move'] is not None:
#     child_move = move_tree['best_move']
#     child = move_tree['children'][str(child_move.from_loc) + str(child_move.to_loc) + str(child_move.special_move)]
#     move_tree = child

print(move_tree['game_state_after_move']['move_history_str'])
print(move_tree['eval'])