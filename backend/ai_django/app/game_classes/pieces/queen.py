from .piece import Piece
from ..constants import QUEENS
from .bishop import Bishop
from .rook import Rook
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import BoardType, MoveHisType


class Queen(Piece):
    def get_type(self) -> str:
        return QUEENS

    def get_name(self) -> str:
        return 'Queen'

    def __str__(self) -> str:
        return '♕' if self.colour == 'white' else '♛'

    def calculate_moves(self, board: 'BoardType', move_history: 'MoveHisType', board_str: str) -> None:
        bishop = Bishop(-1, (self.row, self.col), self.colour)
        rook = Rook(-1, (self.row, self.col), self.colour)
        bishop.calculate_moves(board, move_history, board_str)
        rook.calculate_moves(board, move_history, board_str)
        self.legal_moves = bishop.legal_moves + rook.legal_moves
