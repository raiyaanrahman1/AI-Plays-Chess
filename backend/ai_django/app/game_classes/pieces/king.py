from .piece import Piece
from ..constants import KINGS
from ..constants import SHORT_CASTLE, LONG_CASTLE
from ..utilities import in_bounds
from ..move import Move
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import ColourType, LocType, BoardType, MoveHisType


class King(Piece):
    def __init__(self, id: int, loc: 'LocType', colour: 'ColourType'):
        super().__init__(id, loc, colour)
        self.short_castle_rights: bool = True
        self.long_castle_rights: bool = True

    def get_type(self) -> str:
        return KINGS

    def get_name(self) -> str:
        return 'King'

    def __str__(self) -> str:
        return '♔' if self.colour == 'white' else '♚'

    def calculate_moves(self, board: 'BoardType', move_history: 'MoveHisType', board_str: str) -> None:
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

        # Regular Moves
        for loc in move_to_locs:
            if (
                    in_bounds(loc) and
                    (
                        board[loc[0]][loc[1]] is None or
                        board[loc[0]][loc[1]].colour != self.colour
                    )
            ):
                self.legal_moves.append(Move(self.loc, loc, board, board_str))

        # Castling
        two_left = (self.row, self.col - 2)
        three_left = (self.row, self.col - 3)
        two_right = (self.row, self.col + 2)
        if (
            self.short_castle_rights
            and board[right[0]][right[1]] is None
            and board[two_right[0]][two_right[1]] is None
        ):
            self.legal_moves.append(Move(self.loc, two_right, board, board_str, SHORT_CASTLE))
        if (
            self.long_castle_rights
            and board[left[0]][left[1]] is None
            and board[two_left[0]][two_left[1]] is None
            and board[three_left[0]][three_left[1]] is None
        ):
            self.legal_moves.append(Move(self.loc, two_left, board, board_str, LONG_CASTLE))
