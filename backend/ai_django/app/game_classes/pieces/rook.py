from .piece import Piece
from ..utilities import in_bounds


class Rook(Piece):
    def calculate_moves_in_direction(self, direction, sign, board):
        x = self.row
        y = self.col
        moves = []

        def move_one_space(x, y):
            return (
                x + int(direction == 'x') * sign,
                y + int(direction == 'y') * sign
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

        for direction in ('x', 'y'):
            for sign in (1, -1):
                self.legal_moves += self.calculate_moves_in_direction(direction, sign, board)
