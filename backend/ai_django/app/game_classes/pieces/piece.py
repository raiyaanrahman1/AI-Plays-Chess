from abc import abstractmethod


class Piece:
    def __init__(self, id, loc, colour) -> None:
        self.id = id
        self.row, self.col = loc
        self.colour = colour
        self.legal_moves = []

    @abstractmethod
    def calculate_moves(self, board) -> None:
        pass
