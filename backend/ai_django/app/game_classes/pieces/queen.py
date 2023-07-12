from .piece import Piece
from ..constants import QUEENS
from .bishop import Bishop
from .rook import Rook


class Queen(Piece):
    def get_type(self):
        return QUEENS

    def get_name(self) -> str:
        return 'Queen'

    def __str__(self) -> str:
        return '♕' if self.colour == 'white' else '♛'

    def calculate_moves(self, board, move_history) -> None:
        bishop = Bishop(-1, (self.row, self.col), self.colour)
        rook = Rook(-1, (self.row, self.col), self.colour)
        bishop.calculate_moves(board, move_history)
        rook.calculate_moves(board, move_history)
        self.legal_moves = bishop.legal_moves + rook.legal_moves
