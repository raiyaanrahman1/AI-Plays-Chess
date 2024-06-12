# python -m cProfile -s time test_calculate_deep_moves.py > timed_results.txt

from game_classes.game import Game
from game_classes.ai import GameState, ChessAI, TreeNode
import cProfile
# from .game_classes.game_logic import Logic
from game_classes import settings
# from pprint import pprint
# import json
from timeit import default_timer as timer
import random
import debugpy

# 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
# debugpy.listen(5678)
# print("Waiting for debugger attach")
# debugpy.wait_for_client()
# debugpy.breakpoint()
# print('break on this line')

random.seed(100)

settings.init()
settings.set_debug(True)

game = Game()
game.calculate_legal_moves()

for i in range(8):
    minimax_depth = 2
    k = 3
    beam_depth = 2
    ChessAI.beam_search(game.move_tree, minimax_depth, k, beam_depth)
    print(game.move_tree.eval, game.move_tree.best_move)

    best_move_node = game.move_tree.best_move_node
    best_move = game.move_tree.best_move
    while best_move_node is not None:
        print(best_move_node.move_before_current_state, end=' ')
        best_move_node = best_move_node.best_move_node

    print()
    print()

    game.make_move(best_move.from_loc, best_move.to_loc, best_move.special_move)
