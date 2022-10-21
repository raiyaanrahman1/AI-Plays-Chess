from abc import abstractmethod


class Piece:
    def __init__(self, id, loc, colour) -> None:
        self.id = id
        self.row, self.col = loc
        self.loc = (self.row, self.col)
        self.colour = colour
        self.direction = 1 if self.colour == 'white' else -1
        self.legal_moves = []

    @abstractmethod
    def get_type(self) -> str:
        pass

    @abstractmethod
    def calculate_moves(self, board, move_history) -> None:
        pass
