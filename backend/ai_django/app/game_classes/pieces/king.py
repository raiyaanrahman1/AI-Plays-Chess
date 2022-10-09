from .piece import Piece
from ..utilities import in_bounds


class King(Piece):
    def __init__(self, id, loc, colour):
        super().__init__(id, loc, colour)
        self.short_castle_rights = True
        self.long_castle_rights = True

    # TODO: finish - figure out check and castling
    def calculate_moves(self, board, move_history) -> None:
        up = (self.row + 1, self.col)
        down = (self.row - 1, self.col)
        left = (self.row, self.col - 1)
        right = (self.row, self.col + 1)
        up_left = (up[0], left[1])
        down_left = (down[0], left[1])
        up_right = (up[0], right[1])
        down_right = (down[0], right[1])

        moves = (
            up, down, left, right, up_left, down_left, up_right, down_right
        )

        self.legal_moves = list(
            filter(
                lambda move: in_bounds(move) and (
                    board[move[0]][move[1]] is None or
                    board[move[0]][move[1]].colour != self.colour
                ),
                moves
            )
        )
