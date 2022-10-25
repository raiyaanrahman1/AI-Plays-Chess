from .utilities import loc_to_chess_notation


class GameError(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)


class InvalidPlayerError(GameError):
    def __init__(self, player_colour) -> None:
        message = f'Invalid Move: Not {player_colour}\'s turn'
        super().__init__(message)


class InvalidStartPosError(GameError):
    def __init__(self, start_pos) -> None:
        message = f'Invalid Move: No piece on {loc_to_chess_notation(start_pos)}'
        super().__init__(message)


class IllegalMoveError(GameError):
    def __init__(self, player_colour, piece_name, start_pos, end_pos, special_move=None) -> None:
        start_loc = loc_to_chess_notation(start_pos)
        end_loc = loc_to_chess_notation(end_pos)
        if special_move is None:
            message = (
                f'Invalid Move: It is illegal to move {player_colour}\'s ',
                f'{piece_name} from {start_loc} to {end_loc}'
            )
        elif special_move == 'O-O':
            message = (
                f'Invalid Move: It is illegal for {player_colour}\'s ',
                'king to short castle'
            )
        elif special_move == 'O-O-O':
            message = (
                f'Invalid Move: It is illegal for {player_colour}\'s ',
                'king to long castle'
            )
        elif special_move == '<-x' or special_move == 'x->':
            message = (
                f'Invalid Move: It is illegal for {player_colour} ',
                f'to play en-passent with their pawn on {start_loc} to {end_loc}'
            )
        super().__init__(message)
