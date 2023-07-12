from .piece import Piece
from ..constants import PAWNS
from ..constants import (
    ENPASSANT_LEFT,
    ENPASSANT_RIGHT,
    PROMOTE_TO_QUEEN,
    PROMOTE_TO_ROOK,
    PROMOTE_TO_BISHOP,
    PROMOTE_TO_KNIGHT
)
from ..utilities import in_bounds
from ..move import Move


class Pawn(Piece):
    def get_type(self):
        return PAWNS

    def get_name(self) -> str:
        return 'Pawn'

    def __str__(self) -> str:
        return '♙' if self.colour == 'white' else '♟︎'

    def calculate_moves(self, board, move_history, player_pieces) -> None:
        starting_row = 1 if self.colour == 'white' else 6

        self.legal_moves = []

        one_up = (self.row + 1 * self.direction, self.col)
        two_up = (self.row + 2 * self.direction, self.col)
        left_diag = (self.row + 1 * self.direction, self.col - 1)
        right_diag = (self.row + 1 * self.direction, self.col + 1)

        if in_bounds(one_up) and board[one_up[0]][one_up[1]] is None:
            if (
                (one_up[0] == 7 and self.colour == 'white')
                or (one_up[0] == 0 and self.colour == 'black')
            ):
                self.legal_moves.extend(
                    [
                        Move(self.loc, one_up, board, PROMOTE_TO_QUEEN, player_pieces),
                        Move(self.loc, one_up, board, PROMOTE_TO_ROOK, player_pieces),
                        Move(self.loc, one_up, board, PROMOTE_TO_BISHOP, player_pieces),
                        Move(self.loc, one_up, board, PROMOTE_TO_KNIGHT, player_pieces)
                    ]
                )
            else:
                self.legal_moves.append(Move(self.loc, one_up, board, None, player_pieces))

        if (self.row == starting_row
                and in_bounds(two_up)
                and board[two_up[0]][two_up[1]] is None
                and board[one_up[0]][one_up[1]] is None):
            self.legal_moves.append(Move(self.loc, two_up, board, None, player_pieces))

        for loc in (left_diag, right_diag):
            if (
                in_bounds(loc)
                and board[loc[0]][loc[1]] is not None
                and board[loc[0]][loc[1]].colour != self.colour
            ):
                if (
                    (loc[0] == 7 and self.colour == 'white')
                    or (loc[0] == 0 and self.colour == 'black')
                ):
                    self.legal_moves.extend(
                        [
                            Move(self.loc, loc, board, PROMOTE_TO_QUEEN, player_pieces),
                            Move(self.loc, loc, board, PROMOTE_TO_ROOK, player_pieces),
                            Move(self.loc, loc, board, PROMOTE_TO_BISHOP, player_pieces),
                            Move(self.loc, loc, board, PROMOTE_TO_KNIGHT, player_pieces)
                        ]
                    )
                else:
                    self.legal_moves.append(Move(self.loc, loc, board, None, player_pieces))

            if (
                self.row == starting_row + self.direction * 3
                and in_bounds(loc)
                and board[self.row][loc[1]] is not None
                and board[self.row][loc[1]].get_type() == PAWNS
                and board[self.row][loc[1]].colour != self.colour
                and len(move_history) > 0
                and move_history[-1].piece_type == PAWNS
                and move_history[-1].piece_id == board[self.row][loc[1]].id
                and move_history[-1].from_loc[0] == self.row + 2 * self.direction
            ):
                symbol = ENPASSANT_LEFT if loc == left_diag else ENPASSANT_RIGHT
                self.legal_moves.append(Move(self.loc, loc, board, symbol, player_pieces))
