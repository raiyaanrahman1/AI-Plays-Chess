from .pieces.pawn import Pawn
from .pieces.knight import Knight
from .pieces.bishop import Bishop
from .pieces.rook import Rook
from .pieces.queen import Queen
from .pieces.king import King
from .constants import PIECE_TYPES
from .constants import KING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import PlayerPieces, ColourType, NonZeroDirectionType

PAWNS, KNIGHTS, BISHOPS, ROOKS, QUEENS = PIECE_TYPES


class Player:
    def __init__(self, colour: 'ColourType') -> None:
        self.colour = colour
        self.direction: 'NonZeroDirectionType' = 1 if self.colour == 'white' else -1
        self.pieces = self.setup_pieces()
        self.num_legal_moves = 0

    def setup_pieces(self) -> 'PlayerPieces':
        pieces: 'PlayerPieces' = {}
        base_row = 0 if self.colour == 'white' else 7
        pawn_row = base_row + (base_row == 0) - (base_row != 0)
        pieces[PAWNS] = {}
        for i in range(8):
            pieces[PAWNS][i] = Pawn(i, (pawn_row, i), self.colour)
        pieces[ROOKS] = {
            0: Rook(0, (base_row, 0), self.colour),
            1: Rook(1, (base_row, 7), self.colour)
        }
        pieces[KNIGHTS] = {
            0: Knight(0, (base_row, 1), self.colour),
            1: Knight(1, (base_row, 6), self.colour)
        }
        pieces[BISHOPS] = {
            0: Bishop(0, (base_row, 2), self.colour),
            1: Bishop(1, (base_row, 5), self.colour)
        }
        pieces[QUEENS] = {0: Queen(0, (base_row, 3), self.colour)}
        pieces[KING] = King(0, (base_row, 4), self.colour)
        return pieces
