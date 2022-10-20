from .pieces.pawn import Pawn
from .pieces.knight import Knight
from .pieces.bishop import Bishop
from .pieces.rook import Rook
from .pieces.queen import Queen
from .pieces.king import King
from .constants import PIECE_TYPES
from .constants import KING
PAWNS, KNIGHTS, BISHOPS, ROOKS, QUEENS = PIECE_TYPES


class Player:
    def __init__(self, colour) -> None:
        self.colour = colour
        self.pieces = self.setup_pieces()

    def setup_pieces(self) -> None:
        pieces = {}
        base_row = 0 if self.colour == 'white' else 7
        pawn_row = base_row + (base_row == 0) - (base_row != 0)
        pieces[PAWNS] = [
            Pawn(x, (pawn_row, x), self.colour) for x in range(8)
        ]
        pieces[ROOKS] = [
            Rook(0, (base_row, 0), self.colour),
            Rook(1, (base_row, 7), self.colour)
        ]
        pieces[KNIGHTS] = [
            Knight(0, (base_row, 1), self.colour),
            Knight(1, (base_row, 6), self.colour)
        ]
        pieces[BISHOPS] = [
            Bishop(0, (base_row, 2), self.colour),
            Bishop(1, (base_row, 5), self.colour)
        ]
        pieces[QUEENS] = [Queen(0, (base_row, 3), self.colour)]
        pieces[KING] = King(0, (base_row, 4), self.colour)
        return pieces

    def calculate_legal_moves(self, board, move_history):
        self.pieces[KING].calculate_moves(board, move_history)
        for type in PIECE_TYPES:
            for piece in self.pieces[type]:
                piece.calculate_moves(board, move_history)
