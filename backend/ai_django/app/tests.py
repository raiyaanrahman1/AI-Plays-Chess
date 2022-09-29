from django.test import TestCase
from .game_classes.game import Game


class GameTests(TestCase):
    def test_game(self):
        game = Game()
        print(game.board)
