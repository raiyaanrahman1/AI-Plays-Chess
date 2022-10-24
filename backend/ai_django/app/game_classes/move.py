class Move:
    def __init__(self, from_loc, to_loc, board_before_move, special_move=None):
        self.from_loc = from_loc
        self.to_loc = to_loc
        self.special_move = special_move
        self.piece_type = board_before_move[from_loc[0]][from_loc[1]].get_type()
        self.piece_id = board_before_move[from_loc[0]][from_loc[1]].id
        self.colour = board_before_move[from_loc[0]][from_loc[1]].colour
        self.move_num = -1  # index of move history - set in Logic.make_move()

    def __str__(self) -> str:
        return f'from: {self.from_loc}, to: {self.to_loc}'

    def __repr__(self):
        return self.__str__()
