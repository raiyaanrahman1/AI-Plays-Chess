from .piece import Piece
from ..utilities import in_bounds


class Knight(Piece):
    def calculate_moves(self, board, move_history) -> None:
        direction = 1 if self.colour == 'white' else -1

        up_two_left = (self.row + 2 * direction, self.col - 1)
        up_two_right = (self.row + 2 * direction, self.col + 1)
        left_two_up = (self.row + 1 * direction, self.col - 2)
        left_two_down = (self.row - 1 * direction, self.col - 2)
        right_two_up = (self.row + 1 * direction, self.col + 2)
        right_two_down = (self.row - 1 * direction, self.col + 2)
        down_two_left = (self.row - 2 * direction, self.col - 1)
        down_two_right = (self.row - 2 * direction, self.col + 1)

        moves = (
            up_two_left,
            up_two_right,
            left_two_up,
            left_two_down,
            right_two_up,
            right_two_down,
            down_two_left,
            down_two_right
        )

        self.legal_moves = list(
            filter(
                lambda move: in_bounds(move) and (
                    board[move[0]][move[1]] is None
                    or board[move[0]][move[1]].colour != self.colour
                ),
                moves
            )
        )
