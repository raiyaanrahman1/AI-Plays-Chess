from typing import Literal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import (
        ColourType
    )

class GameStatus:
    def __init__(
            self,
            game_finished: bool = False,
            white_in_check: bool = False,
            black_in_check: bool = False,
            last_move_was_capture: bool = False,
            game_result: Literal['checkmate', 'draw', ''] = '',
            winner: 'ColourType | None' = None,
            game_result_message: str = '',
            draw_by: str | None = None
        ) -> None:

        self.game_finished = game_finished
        self.white_in_check = white_in_check
        self.black_in_check = black_in_check
        self.last_move_was_capture = last_move_was_capture
        self.game_result = game_result
        self.winner = winner
        self.game_result_message = game_result_message
        self.draw_by = draw_by

    def set_player_in_check(self, colour: 'ColourType', in_check: bool):
        if colour == 'white':
            self.white_in_check = in_check
        else:
            self.black_in_check = in_check

    def __str__(self) -> str:
        return f'''game_finished: {self.game_finished}
        game_result: {self.game_result}
        game_result_message: {self.game_result_message}
        white_in_check: {self.white_in_check}
        black_in_check: {self.black_in_check}
        last_move_was_capture: {self.last_move_was_capture}
        winner: {self.winner}
        '''