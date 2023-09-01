from .game_classes.game import Game
from .game_classes.game_logic import Logic
from .game_classes import settings
from pprint import pprint
# import json
from timeit import default_timer as timer
import debugpy

# 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
debugpy.listen(5678)
print("Waiting for debugger attach")
debugpy.wait_for_client()
debugpy.breakpoint()
print('break on this line')

settings.init()
settings.set_debug(True)

game = Game()
game.calculate_legal_moves()

start = timer()

game.update_move_tree(2)

end = timer()

print(f'Time taken: {end - start}')
print(game.move_tree['eval'])
print(game.move_tree['best_move'])

best_move = game.move_tree['best_move']

game.make_move(best_move.from_loc, best_move.to_loc, best_move.special_move)

start = timer()

game.update_move_tree(2)

end = timer()

print(f'Time taken: {end - start}')
print(game.move_tree['eval'])
print(game.move_tree['best_move'])

# pprint(result)
# for state in result['children']:
#     if str(state['move_before_current_state']) == 'e4':
#         print(state)
