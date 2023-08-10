from abc import abstractmethod
from typing import List

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import ColourType, LocType, BoardType, MoveHisType, MoveType


class Piece:
    def __init__(self, id: int, loc: 'LocType', colour: 'ColourType') -> None:
        self.id = id
        self.row, self.col = loc
        self.loc = loc
        self.colour: 'ColourType' = colour
        self.direction = 1 if self.colour == 'white' else -1
        self.legal_moves: List[MoveType] = []

    def set_loc(self, loc: 'LocType') -> None:
        self.row, self.col = loc
        self.loc = loc

    @abstractmethod
    def get_type(self) -> str:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def calculate_moves(self, board: 'BoardType', move_history: 'MoveHisType') -> None:
        pass
