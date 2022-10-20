from django.test import TestCase


class GameTests(TestCase):
    @classmethod
    def setUpClass(cls):
        import django
        super(GameTests, cls).setUpClass()
        django.setup()

    def test_game(self):
        from .game_classes.game import Game
        game = Game()
        game.calculate_legal_moves()
        print(game)
