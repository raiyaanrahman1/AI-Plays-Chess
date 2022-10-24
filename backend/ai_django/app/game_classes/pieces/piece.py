from abc import abstractmethod


class Piece:
    def __init__(self, id, loc, colour) -> None:
        self.id = id
        self.row, self.col = loc
        self.loc = loc
        self.colour = colour
        self.direction = 1 if self.colour == 'white' else -1
        self.legal_moves = []

    def set_loc(self, loc) -> None:
        self.row, self.col = loc
        self.loc = loc

    @abstractmethod
    def get_type(self) -> str:
        pass

    @abstractmethod
    def calculate_moves(self, board, move_history) -> None:
        pass
