from django.test import TestCase
import sys


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
        with self.assertRaises(InvalidStartPosError):
            game.make_move((3, 4), (4, 4))
        with self.assertRaises(InvalidPlayerError):
            game.make_move((7, 0), (6, 0))
        with self.assertRaises(IllegalMoveError):
            game.make_move((1, 4), (1, 4))
        with self.assertRaises(IllegalMoveError):
            game.make_move((1, 4), (2, 5))
        with self.assertRaises(IllegalMoveError):
            game.make_move((0, 4), (1, 4))

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
