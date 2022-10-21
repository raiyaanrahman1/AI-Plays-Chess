from .piece import Piece
from ..constants import PAWNS
from ..utilities import in_bounds


class Pawn(Piece):
    def get_type(self):
        return PAWNS

    def calculate_moves(self, board, move_history) -> None:
        starting_row = 1 if self.colour == 'white' else 6

        self.legal_moves = []

        one_up = (self.row + 1 * self.direction, self.col)
        two_up = (self.row + 2 * self.direction, self.col)
        left_diag = (self.row + 1 * self.direction, self.col - 1)
        right_diag = (self.row + 1 * self.direction, self.col + 1)

        if in_bounds(one_up) and board[one_up[0]][one_up[1]] is None:
            self.legal_moves.append(one_up)

        if (self.row == starting_row
                and in_bounds(two_up)
                and board[two_up[0]][two_up[1]] is None):
            self.legal_moves.append(two_up)

        for loc in (left_diag, right_diag):
            if (
                in_bounds(loc)
                and board[loc[0]][loc[1]] is not None
                and board[loc[0]][loc[1]].colour != self.colour
            ):
                self.legal_moves.append(loc)

            # TODO: for en-passent, also need to check if the pawn moved 2 spaces, not 1
            if (
                self.row == starting_row + self.direction * 3
                and in_bounds(loc)
                and board[self.row][loc[1]] is not None
                and board[self.row][loc[1]].get_type() == PAWNS
                and board[self.row][loc[1]].colour != self.colour
                and len(move_history) > 0
                and move_history[-1].piece.get_type() == PAWNS
                and move_history[-1].piece.id == board[self.row][loc[1]].id
            ):
                self.legal_moves.append(loc)
