from .piece import Piece
from ..constants import ROOKS
from ..utilities import in_bounds
from ..move import Move


class Rook(Piece):
    def get_type(self):
        return ROOKS

    def __str__(self) -> str:
        return '♖' if self.colour == 'white' else '♜'

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
            moves.append(Move(self.loc, (x, y), board))
            x, y = move_one_space(x, y)

        if in_bounds((x, y)) and board[x][y].colour != self.colour:
            moves.append(Move(self.loc, (x, y), board))

        return moves

    def calculate_moves(self, board, move_history) -> None:
        self.legal_moves = []

        for direction in ('x', 'y'):
            for sign in (1, -1):
                self.legal_moves += self.calculate_moves_in_direction(direction, sign, board)
