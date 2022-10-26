from .utilities import loc_to_chess_notation
from .constants import SHORT_CASTLE, LONG_CASTLE, ENPASSANT_LEFT, ENPASSANT_RIGHT


class GameError(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)


class InvalidPlayerError(GameError):
    def __init__(self, player_colour, message_prefix='') -> None:
        message = f'Invalid Move: Not {player_colour}\'s turn'
        super().__init__(message_prefix + message)


class InternalInvalidPlayerError(InvalidPlayerError):
    def __init__(self, player_colour) -> None:
        message_prefix = 'Internal Error:\n'
        super().__init__(player_colour, message_prefix)


class InvalidStartPosError(GameError):
    def __init__(self, start_pos, message_prefix='') -> None:
        message = f'Invalid Move: No piece on {loc_to_chess_notation(start_pos)}'
        super().__init__(message_prefix + message)


class InternalInvalidStartPosError(InvalidStartPosError):
    def __init__(self, start_pos) -> None:
        message_prefix = 'Internal Error:\n'
        super().__init__(start_pos, message_prefix)


class IllegalMoveError(GameError):
    def __init__(
        self, player_colour, piece_name, start_pos, end_pos, special_move=None, message_prefix=''
    ) -> None:
        start_loc = loc_to_chess_notation(start_pos)
        end_loc = loc_to_chess_notation(end_pos)
        if special_move is None:
            message = (
                f'Invalid Move: It is illegal to move {player_colour}\'s ',
                f'{piece_name} from {start_loc} to {end_loc}'
            )
        elif special_move == SHORT_CASTLE:
            message = (
                f'Invalid Move: It is illegal for {player_colour}\'s ',
                'king to short castle'
            )
        elif special_move == LONG_CASTLE:
            message = (
                f'Invalid Move: It is illegal for {player_colour}\'s ',
                'king to long castle'
            )
        elif special_move == ENPASSANT_LEFT or special_move == ENPASSANT_RIGHT:
            message = (
                f'Invalid Move: It is illegal for {player_colour} ',
                f'to play en-passent with their pawn on {start_loc} to {end_loc}'
            )
        # TODO: Should I add promotion moves?? Even though it shouldn't be possible
        super().__init__(message_prefix + ''.join(message))


class InternalIllegalMoveError(IllegalMoveError):
    def __init__(
        self, player_colour, piece_name, start_pos, end_pos, special_move=None
    ) -> None:
        message_prefix = 'Internal Error:\n'
        super().__init__(
            player_colour, piece_name, start_pos, end_pos, special_move, message_prefix
        )
