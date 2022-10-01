from .piece import Piece


class Pawn(Piece):

    def calculate_moves(self, board, move_history) -> None:
        starting_row = 1 if self.colour == 'white' else 6
        direction = 1 if self.colour == 'white' else -1

        self.legal_moves = []

        one_up_loc = (self.row + 1 * direction, self.col)
        two_up_loc = (self.row + 2 * direction, self.col)
        left_diag_loc = (self.row + 1 * direction, self.col - 1)
        right_diag_loc = (self.row + 1 * direction, self.col + 1)

        one_up = {'loc': one_up_loc}
        two_up = {'loc': two_up_loc}
        left_diag = {'loc': left_diag_loc}
        right_diag = {'loc': right_diag_loc}

        for move in (one_up, two_up, left_diag, right_diag):
            move['inBounds'] = 0 <= move['loc'][0] <= 7 and \
                0 <= move['loc'][1] <= 7

        if one_up['inBounds'] and board[one_up_loc[0]][one_up_loc[1]] is None:
            self.legal_moves.append(one_up_loc)

        if (self.row == starting_row
                and two_up['inBounds']
                and board[two_up_loc[0]][two_up_loc[1]] is None):
            self.legal_moves.append(two_up_loc)

        if (left_diag['inBounds']
                and (
                        board[left_diag_loc[0]][left_diag_loc[1]] is None
                        or board[left_diag_loc[0]][left_diag_loc[1]].colour
                        != self.colour
                    )):
            self.legal_moves.append(left_diag_loc)

        if (right_diag['inBounds']
                and (
                        board[right_diag_loc[0]][right_diag_loc[1]] is None
                        or board[right_diag_loc[0]][right_diag_loc[1]].colour
                        != self.colour
                    )):
            self.legal_moves.append(right_diag_loc)

        if (self.row == starting_row + direction * 3
                and left_diag['inBounds']
                and board[self.row][self.col - 1] is not None
                and isinstance(board[self.row][self.col - 1], Pawn)
                and board[self.row][self.col - 1].colour != self.colour
                and len(move_history) > 0
                and isinstance(move_history[-1].piece, Pawn)
                and move_history[-1].piece.id ==
                board[self.row][self.col - 1].id):
            self.legal_moves.append(left_diag_loc)

        if (self.row == starting_row + direction * 3
                and right_diag['inBounds']
                and board[self.row][self.col + 1] is not None
                and isinstance(board[self.row][self.col + 1], Pawn)
                and board[self.row][self.col - 1].colour != self.colour
                and len(move_history) > 0
                and isinstance(move_history[-1].piece, Pawn)
                and move_history[-1].piece.id ==
                board[self.row][self.col + 1].id):
            self.legal_moves.append(right_diag_loc)
