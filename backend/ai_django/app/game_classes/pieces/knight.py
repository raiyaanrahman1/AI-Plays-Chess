from .piece import Piece


class Knight(Piece):
    def calculate_moves(self, board, move_history) -> None:
        direction = 1 if self.colour == 'white' else -1

        up_two_left_loc = (self.row + 2 * direction, self.col - 1)
        up_two_right_loc = (self.row + 2 * direction, self.col + 1)
        left_two_up_loc = (self.row + 1 * direction, self.col - 2)
        left_two_down_loc = (self.row - 1 * direction, self.col - 2)
        right_two_up_loc = (self.row + 1 * direction, self.col + 2)
        right_two_down_loc = (self.row - 1 * direction, self.col + 2)
        down_two_left_loc = (self.row - 2 * direction, self.col - 1)
        down_two_right_loc = (self.row - 2 * direction, self.col + 1)

        moves = (
                    up_two_left_loc,
                    up_two_right_loc,
                    left_two_up_loc,
                    left_two_down_loc,
                    right_two_up_loc,
                    right_two_down_loc,
                    down_two_left_loc,
                    down_two_right_loc
                )

        self.legal_moves = list(
            filter(
                (
                    lambda move: 0 <= move[0] <= 7
                    and 0 <= move[1] <= 7
                    and (
                        board[move[0]][move[1]] is None
                        or board[move[0]][move[1]].colour != self.colour
                    )
                ),
                moves
            )
        )
