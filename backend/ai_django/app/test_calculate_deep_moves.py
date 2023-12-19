# python -m cProfile -s time test_calculate_deep_moves.py > timed_results.txt

from game_classes.game import Game
# from .game_classes.game_logic import Logic
from game_classes import settings
# from pprint import pprint
# import json
from timeit import default_timer as timer
import debugpy

# 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
# debugpy.listen(5678)
# print("Waiting for debugger attach")
# debugpy.wait_for_client()
# debugpy.breakpoint()
# print('break on this line')

settings.init()
settings.set_debug(True)

game = Game()
game.calculate_legal_moves()

for _ in range(4):
    start = timer()

    game.update_move_tree(2)

    end = timer()

    print(game.move_tree['best_move'])
    print(game.move_tree['eval'])
    print(f'Time taken: {end - start}')

    best_move = game.move_tree['best_move']

    game.make_move(best_move.from_loc, best_move.to_loc, best_move.special_move)
