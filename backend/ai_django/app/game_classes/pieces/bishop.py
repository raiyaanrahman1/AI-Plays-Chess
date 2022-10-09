from .piece import Piece
from ..utilities import in_bounds


class Bishop(Piece):
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
            moves.append((x, y))
            x, y = move_one_space(x, y)

        if in_bounds((x, y)) and board[x][y].colour != self.colour:
            moves.append((x, y))

        return moves

    def calculate_moves(self, board, move_history) -> None:
        self.legal_moves = []

        for x_direction in (1, -1):
            for y_direction in (1, -1):
                self.legal_moves += self.calculate_moves_in_direction(
                    x_direction, y_direction, board
                )
