from django.test import TestCase
import sys
import os
import re
from .game_classes import settings
from .game_classes.constants import PIECE_TYPES, KING
from timeit import default_timer as timer
PAWNS, KNIGHTS, BISHOPS, ROOKS, QUEENS = PIECE_TYPES
ALL_PIECE_TYPES = PIECE_TYPES + (KING,)

settings.init()


def coloured(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)


class GameTests(TestCase):
    @classmethod
    def setUpClass(cls):
        import django
        cls.verbose = '-v' in sys.argv
        super(GameTests, cls).setUpClass()
        django.setup()

    def print(self, text):
        if self.verbose:
            print(text)

    def test_game_errors(self):
        from .game_classes.game import Game
        from .game_classes.game_errors import (
            InvalidStartPosError, InvalidPlayerError, IllegalMoveError
        )
        print(coloured(150, 0, 255, 'Running test_game_errors'))
        game = Game()
        with self.assertRaises(InvalidStartPosError) as context:
            game.make_move((3, 4), (4, 4))
        self.print(context.exception)
        with self.assertRaises(InvalidPlayerError) as context:
            game.make_move((7, 0), (6, 0))
        self.print(context.exception)
        with self.assertRaises(IllegalMoveError) as context:
            game.make_move((1, 4), (1, 4))
        self.print(context.exception)
        with self.assertRaises(IllegalMoveError) as context:
            game.make_move((1, 4), (2, 5))
        self.print(context.exception)
        with self.assertRaises(IllegalMoveError) as context:
            game.make_move((0, 4), (1, 4))
        self.print(context.exception)

    def test_colour_of_square(self):
        from .game_classes.utilities import colour_of_square
        from pprint import pformat
        print(coloured(150, 0, 255, 'Running test_colour_of_square'))
        self.print(pformat([[colour_of_square((i, j)) for j in range(8)] for i in range(8)]))

    def test_game(self):
        from .game_classes.game import Game
        print(coloured(150, 0, 255, 'Running test_game'))
        game = Game()
        game.calculate_legal_moves()
        self.print(game)
        self.print(game.info())
        game.make_move((1, 4), (3, 4))
        self.print(game)
        self.print(game.info())

    def test_game_via_pgn(self):
        def check_move_made_in_piece_moves(move_made, pieces):
            for piece in pieces:
                for piece_move in piece:
                    if piece_move['move_str'] in move_made and (
                        'O-O-O' not in move_made
                        or piece_move['move_str'] != 'O-O'
                    ):
                        return piece_move
            return None
        from .game_classes.game import Game
        from pprint import pformat
        settings.set_debug(True)

        print(coloured(150, 0, 255, 'Running test_game_via_pgn'))

        games = []
        with open(f'{os.path.dirname(__file__)}/game_data/lichess_db_standard_rated_2013-01.pgn') as file:
            for line in file:
                if not line.startswith('[') and len(line.strip()) != 0:
                    games.append(re.sub('{.*?}', '', line))

        MAX_GAMES = 100
        games = games[:MAX_GAMES]
        num_moves_processed = 0
        start = timer()
        for game_num, game_str in enumerate(games):
            game_moves = [move for move in game_str.split() if '.' not in move][:-1]  # gets rid of the result and move numbers
            game = Game()
            game.calculate_legal_moves()

            for move_num, move_played in enumerate(game_moves):
                if re.search('[RNQ][a-h][1-8]x?[a-h][1-8]', move_played):
                    move_played = move_played[0] + move_played[2:]  # Seems to be a bug where lichess will write Rd1d2 instead of R1d2 in pgn

                legal_moves = game.get_all_legal_moves()
                colour = 'white' if move_num % 2 == 0 else 'black'
                piece_type = move_played[0] if move_played[0] in ALL_PIECE_TYPES else PAWNS
                if 'O-O' in move_played or 'O-O-O' in move_played:
                    piece_type = KING

                pieces = [legal_moves[colour][KING]] if piece_type == KING else legal_moves[colour][piece_type]
                move = check_move_made_in_piece_moves(move_played, pieces)
                error_info = {
                    'game_num': game_num,
                    'move_num': move_num,
                    'move number': move_num // 2 + 1,
                    'move_played': move_played,
                    'legal_moves': pieces
                }
                self.assertIsNotNone(move, pformat(error_info) + game_str)
                game.make_move(
                    move['from_loc'],
                    move['to_loc'],
                    move['special_move']
                )
                num_moves_processed += 1
        end = timer()
        self.print(f'Average number of moves processed per second: {num_moves_processed/(end-start)}')
