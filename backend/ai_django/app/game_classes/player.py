from utilities import in_bounds
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
        self.direction = 1 if self.colour == 'white' else -1
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
        for piece_type in PIECE_TYPES:
            for piece in self.pieces[piece_type]:
                piece.calculate_moves(board, move_history)

    # filters the pieces moves such that after the move is made, the player's king is not in check
    def validate_moves(self, board, piece):
        pass

    def in_check(self, board, other_player) -> bool:
        for piece_type in [KNIGHTS, BISHOPS, ROOKS, QUEENS]:
            for piece in other_player[piece_type]:
                if self.pieces[KING].loc in other_player[piece_type][piece].legal_moves:
                    return True

        # the other King can't actually put the player in check
        # this is simply to prevent the kings from being adjacent
        if self.pieces[KING].loc in other_player[KING].legal_moves:
            return True

        left_diag = (self.row + 1 * self.direction, self.col - 1)
        right_diag = (self.row + 1 * self.direction, self.col + 1)

        for loc in (left_diag, right_diag):
            if not in_bounds(loc):
                continue
            board_at_loc = board[loc[0]][loc[1]]
            if (
                board_at_loc is not None
                and board_at_loc.colour != self.colour
                and isinstance(board_at_loc, Pawn)
            ):
                return True

        return False
