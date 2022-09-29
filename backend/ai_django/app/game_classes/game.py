from .board import Board


class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.moves = []

    def make_move(self, from_loc, to_loc):
        try:
            self.board.make_move(from_loc, to_loc)
        except Exception as err:
            print(str(err))
