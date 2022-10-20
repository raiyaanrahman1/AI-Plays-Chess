from abc import abstractmethod


class Piece:
    def __init__(self, id, loc, colour) -> None:
        self.id = id
        self.loc = loc
        self.row, self.col = loc
        self.colour = colour
        self.direction = 1 if self.colour == 'white' else -1
        self.legal_moves = []

    @abstractmethod
    def calculate_moves(self, board, move_history) -> None:
        pass
