from .piece import Piece
from ..constants import KNIGHTS
from ..utilities import in_bounds
from ..move import Move


class Knight(Piece):
    def get_type(self):
        return KNIGHTS

    def get_name(self) -> str:
        return 'Knight'

    def __str__(self) -> str:
        return '♘' if self.colour == 'white' else '♞'

    def calculate_moves(self, board, move_history, player_pieces) -> None:
        up_two_left = (self.row + 2 * self.direction, self.col - 1)
        up_two_right = (self.row + 2 * self.direction, self.col + 1)
        left_two_up = (self.row + 1 * self.direction, self.col - 2)
        left_two_down = (self.row - 1 * self.direction, self.col - 2)
        right_two_up = (self.row + 1 * self.direction, self.col + 2)
        right_two_down = (self.row - 1 * self.direction, self.col + 2)
        down_two_left = (self.row - 2 * self.direction, self.col - 1)
        down_two_right = (self.row - 2 * self.direction, self.col + 1)

        move_to_locs = (
            up_two_left,
            up_two_right,
            left_two_up,
            left_two_down,
            right_two_up,
            right_two_down,
            down_two_left,
            down_two_right
        )

        self.legal_moves = []

        for loc in move_to_locs:
            if (
                    in_bounds(loc) and
                    (
                        board[loc[0]][loc[1]] is None or
                        board[loc[0]][loc[1]].colour != self.colour
                    )
            ):
                self.legal_moves.append(Move(self.loc, loc, board, None, player_pieces))
