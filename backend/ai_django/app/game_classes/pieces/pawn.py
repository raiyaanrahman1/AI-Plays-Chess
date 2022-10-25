from .piece import Piece
from ..constants import PAWNS
from ..utilities import in_bounds
from ..move import Move


class Pawn(Piece):
    def get_type(self):
        return PAWNS

    def get_name(self) -> str:
        return 'Pawn'

    def __str__(self) -> str:
        return '♙' if self.colour == 'white' else '♟︎'

    def calculate_moves(self, board, move_history) -> None:
        starting_row = 1 if self.colour == 'white' else 6

        self.legal_moves = []

        one_up = (self.row + 1 * self.direction, self.col)
        two_up = (self.row + 2 * self.direction, self.col)
        left_diag = (self.row + 1 * self.direction, self.col - 1)
        right_diag = (self.row + 1 * self.direction, self.col + 1)

        if in_bounds(one_up) and board[one_up[0]][one_up[1]] is None:
            self.legal_moves.append(Move(self.loc, one_up, board))

        if (self.row == starting_row
                and in_bounds(two_up)
                and board[two_up[0]][two_up[1]] is None):
            self.legal_moves.append(Move(self.loc, two_up, board))

        for loc in (left_diag, right_diag):
            if (
                in_bounds(loc)
                and board[loc[0]][loc[1]] is not None
                and board[loc[0]][loc[1]].colour != self.colour
            ):
                self.legal_moves.append(Move(self.loc, loc, board))

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
                symbol = '<-x' if loc == left_diag else 'x->'
                self.legal_moves.append(Move(self.loc, loc, board, symbol))
