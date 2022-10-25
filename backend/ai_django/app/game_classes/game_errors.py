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
        message = f'Invalid Move: No piece on {start_pos}'
        super().__init__(message)


class IllegalMove(GameError):
    def __init__(self, player_colour, piece, start_pos, end_pos) -> None:
        message = (
            f'Invalid Move: It is illegal to move {player_colour}\'s',
            f'{piece} from {start_pos} to {end_pos}'
        )
        super().__init__(message)
