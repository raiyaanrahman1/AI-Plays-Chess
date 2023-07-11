from .utilities import loc_to_chess_notation, get_board_string
from .constants import (
    ENPASSANT_LEFT,
    ENPASSANT_RIGHT,
)


class Move:
    def __init__(self, from_loc, to_loc, board_before_move, special_move=None):
        self.from_loc = from_loc
        self.to_loc = to_loc
        self.special_move = special_move
        self.move_name = None
        self.board_str_before_move = get_board_string(board_before_move)
        self.move_num = -1  # index of move history - set in Logic.make_move()

        if board_before_move[from_loc[0]][from_loc[1]] is None:
            self.piece_type = None
            self.piece_id = None
            self.colour = None
            return

        self.piece_type = board_before_move[from_loc[0]][from_loc[1]].get_type()
        self.piece_id = board_before_move[from_loc[0]][from_loc[1]].id
        self.colour = board_before_move[from_loc[0]][from_loc[1]].colour

        captured_piece = self.get_captured_piece(board_before_move)
        self.is_capture = captured_piece is not None
        # self.temporary_move_name = Logic.get_move_name(self, self.is_capture, )

    def __str__(self) -> str:
        if self.move_name is not None:
            return self.move_name
        if self.special_move is not None:
            return self.special_move
        from_loc_chess_not = loc_to_chess_notation(self.from_loc)
        to_loc_chess_not = loc_to_chess_notation(self.to_loc)
        return f'from: {from_loc_chess_not}, to: {to_loc_chess_not}'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        # NOTE: This means that moves can be played at different times and be considered
        # equal (since move_num is not checked). It doesn't even have to be the exact same piece_id
        return (
            isinstance(other, Move)
            and self.colour == other.colour
            and self.piece_type == other.piece_type
            and self.from_loc == other.from_loc
            and self.to_loc == other.to_loc
            and self.special_move == other.special_move
        )

    def get_captured_piece(self, board):
        from_loc = self.from_loc
        to_loc = self.to_loc

        if self.special_move is None or self.special_move.startswith('promote'):
            # if capture, update opponents pieces
            if board[to_loc[0]][to_loc[1]] is not None:
                return board[to_loc[0]][to_loc[1]]

        elif self.special_move == ENPASSANT_LEFT:
            return board[from_loc[0]][from_loc[1] - 1]

        elif self.special_move == ENPASSANT_RIGHT:
            return board[from_loc[0]][from_loc[1] + 1]

        return None
