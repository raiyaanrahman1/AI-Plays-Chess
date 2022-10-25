from .piece import Piece
from ..constants import KING
from ..utilities import in_bounds
from ..move import Move


class King(Piece):
    def __init__(self, id, loc, colour):
        super().__init__(id, loc, colour)
        self.short_castle_rights = True
        self.long_castle_rights = True

    def get_type(self):
        return KING

    def get_name(self) -> str:
        return 'King'

    def __str__(self) -> str:
        return '♔' if self.colour == 'white' else '♚'

    def calculate_moves(self, board, move_history) -> None:
        up = (self.row + 1, self.col)
        down = (self.row - 1, self.col)
        left = (self.row, self.col - 1)
        right = (self.row, self.col + 1)
        up_left = (up[0], left[1])
        down_left = (down[0], left[1])
        up_right = (up[0], right[1])
        down_right = (down[0], right[1])

        move_to_locs = (
            up, down, left, right, up_left, down_left, up_right, down_right
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
                self.legal_moves.append(Move(self.loc, loc, board))
