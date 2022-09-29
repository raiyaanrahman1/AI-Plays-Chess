class InvalidPlayerError(Exception):
    def __init__(self, player) -> None:
        self.message = f'Invalid Move: Not {player}\'s turn'
        super().__init__(self.message)


class InvalidStartPosError(Exception):
    def __init__(self, start_pos) -> None:
        self.message = f'Invalid Move: No piece on {start_pos}'
        super().__init__(self.message)


class IllegalMove(Exception):
    def __init__(self, player, piece, start_pos, end_pos) -> None:
        self.message = (
                f'Invalid Move: It is illegal to move {player}\'s',
                f'{piece} from {start_pos} to {end_pos}'
            )
        super().__init__(self.message)
