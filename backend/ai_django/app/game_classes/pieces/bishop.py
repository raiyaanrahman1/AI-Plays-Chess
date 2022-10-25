from .piece import Piece
from ..constants import BISHOPS
from ..utilities import in_bounds
from ..move import Move


class Bishop(Piece):
    def get_type(self):
        return BISHOPS

    def get_name(self) -> str:
        return 'Bishop'

    def __str__(self) -> str:
        return '♗' if self.colour == 'white' else '♝'

    def calculate_moves_in_direction(self, x_direction, y_direction, board):
        x = self.row
        y = self.col
        moves = []

        def move_one_space(x, y):
            return (
                x + 1 * x_direction,
                y + 1 * y_direction
            )

        x, y = move_one_space(x, y)
        while in_bounds((x, y)) and board[x][y] is None:
            moves.append(Move(self.loc, (x, y), board))
            x, y = move_one_space(x, y)

        if in_bounds((x, y)) and board[x][y].colour != self.colour:
            moves.append(Move(self.loc, (x, y), board))

        return moves

    def calculate_moves(self, board, move_history) -> None:
        self.legal_moves = []

        for x_direction in (1, -1):
            for y_direction in (1, -1):
                self.legal_moves += self.calculate_moves_in_direction(
                    x_direction, y_direction, board
                )
