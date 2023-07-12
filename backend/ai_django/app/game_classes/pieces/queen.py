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

    def calculate_moves(self, board, move_history, player_pieces) -> None:
        bishop = Bishop(-1, (self.row, self.col), self.colour)
        rook = Rook(-1, (self.row, self.col), self.colour)
        bishop.calculate_moves(board, move_history, player_pieces)
        rook.calculate_moves(board, move_history, player_pieces)
        self.legal_moves = bishop.legal_moves + rook.legal_moves
