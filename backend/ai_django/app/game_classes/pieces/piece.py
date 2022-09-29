from abc import abstractmethod


class Piece:
    def __init__(self, id, loc) -> None:
        self.id = id
        self.legal_moves = []
        self.loc = loc

    @abstractmethod
    def calculate_moves(self) -> None:
        pass
