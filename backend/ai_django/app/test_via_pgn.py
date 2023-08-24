# How to run this test:
# First, make sure you are in the backend/ai_django directory
# Then run: python -m app.test_via_pgn

import os
import re
import traceback
from multiprocessing import Pool
from .game_classes.game import Game
from pprint import pformat
from .game_classes import settings
from .game_classes.constants import PIECE_TYPES
from timeit import default_timer as timer
PAWNS, KNIGHTS, BISHOPS, ROOKS, QUEENS, KINGS = PIECE_TYPES

MAX_GAMES = 1000
PRINT_TRACE_BACK = True

# import debugpy


def check_move_made_in_piece_moves(move_made, pieces):
    for piece in pieces:
        for piece_move in piece:
            if piece_move['move_str'] in move_made and (
                'O-O-O' not in move_made
                or piece_move['move_str'] != 'O-O'
            ):
                return piece_move
    return None


def test_game(game):
    game_num, game_str = game
    settings.init()
    settings.set_debug(True)
    UPDATE_INTERVAL = MAX_GAMES / 10
    if game_num % UPDATE_INTERVAL == 0:
        print(f'Processing game number {game_num}')
    try:
        return test_game_helper(game_num, game_str)
    except Exception as e:
        print(str(e))
        if PRINT_TRACE_BACK:
            print(traceback.format_exc())
        print(f'Game Number: {game_num}')


def test_game_helper(game_num, game_str):
    game_moves = [move for move in game_str.split() if '.' not in move][:-1]  # gets rid of the result and move numbers
    game = Game()
    game.calculate_legal_moves()

    for move_num, move_played in enumerate(game_moves):
        if re.search('[RBNQ][a-h][1-8]x?[a-h][1-8]', move_played):
            move_played = move_played[0] + move_played[2:]  # Seems to be a bug where lichess will write Rd1d2 instead of R1d2 in pgn

        legal_moves = game.get_all_legal_moves()
        colour = 'white' if move_num % 2 == 0 else 'black'
        piece_type = move_played[0] if move_played[0] in PIECE_TYPES else PAWNS
        if 'O-O' in move_played or 'O-O-O' in move_played:
            piece_type = KINGS

        pieces = legal_moves[colour][piece_type]
        move = check_move_made_in_piece_moves(move_played, pieces)
        error_info = {
            'game_num': game_num,
            'move_num': move_num,
            'move number': move_num // 2 + 1,
            'move_played': move_played,
            'legal_moves': pieces
        }
        assert move is not None, pformat(error_info) + game_str
        game.make_move(
            move['from_loc'],
            move['to_loc'],
            move['special_move']
        )
    return len(game_moves)


if __name__ == '__main__':
    # 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
    # debugpy.listen(5678)
    # print("Waiting for debugger attach")
    # debugpy.wait_for_client()
    # debugpy.breakpoint()
    # print('break on this line')

    pool = Pool()

    games = []
    print('loading in games...')
    with open(f'{os.path.dirname(__file__)}/game_data/lichess_db_standard_rated_2013-01.pgn') as file:
        for line in file:
            if not line.startswith('[') and len(line.strip()) != 0:
                games.append(re.sub('{.*?}', '', line))

    print('testing games...')
    games = games[0:MAX_GAMES]
    num_moves_processed = 0

    start = timer()
    moves_per_game = pool.map(test_game, enumerate(games))
    try:
        num_moves_processed = sum(moves_per_game)
    except TypeError:
        num_moves_processed = sum([num_moves for num_moves in moves_per_game if num_moves is not None])
        print('ERROR OCCURED')
    end = timer()

    print(f'Average number of moves processed per second: {num_moves_processed/(end-start)}')
    print(f'Time taken: {end-start}s')
