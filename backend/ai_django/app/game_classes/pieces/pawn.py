from .piece import Piece
from ..utilities import in_bounds


class Pawn(Piece):

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

        if (in_bounds(left_diag)
                and board[left_diag[0]][left_diag[1]] is not None
                and board[left_diag[0]][left_diag[1]].colour != self.colour):
            self.legal_moves.append(left_diag)

        if (in_bounds(right_diag)
                and board[right_diag[0]][right_diag[1]] is not None
                and board[right_diag[0]][right_diag[1]].colour != self.colour):
            self.legal_moves.append(right_diag)

        # TODO: for en-passent, also need to check if the pawn moved 2 spaces, not 1
        if (self.row == starting_row + self.direction * 3
                and in_bounds(left_diag)
                and board[self.row][self.col - 1] is not None
                and isinstance(board[self.row][self.col - 1], Pawn)
                and board[self.row][self.col - 1].colour != self.colour
                and len(move_history) > 0
                and isinstance(move_history[-1].piece, Pawn)
                and move_history[-1].piece.id ==
                board[self.row][self.col - 1].id):
            self.legal_moves.append(left_diag)

        if (self.row == starting_row + self.direction * 3
                and in_bounds(right_diag)
                and board[self.row][self.col + 1] is not None
                and isinstance(board[self.row][self.col + 1], Pawn)
                and board[self.row][self.col - 1].colour != self.colour
                and len(move_history) > 0
                and isinstance(move_history[-1].piece, Pawn)
                and move_history[-1].piece.id ==
                board[self.row][self.col + 1].id):
            self.legal_moves.append(right_diag)
