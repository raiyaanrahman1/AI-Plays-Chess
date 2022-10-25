from .utilities import loc_to_chess_notation


class Move:
    def __init__(self, from_loc, to_loc, board_before_move, special_move=None):
        self.from_loc = from_loc
        self.to_loc = to_loc
        self.special_move = special_move
        self.move_num = -1  # index of move history - set in Logic.make_move()

        if board_before_move[from_loc[0]][from_loc[1]] is None:
            self.piece_type = None
            self.piece_id = None
            self.colour = None
            return

        self.piece_type = board_before_move[from_loc[0]][from_loc[1]].get_type()
        self.piece_id = board_before_move[from_loc[0]][from_loc[1]].id
        self.colour = board_before_move[from_loc[0]][from_loc[1]].colour

    def __str__(self) -> str:
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
