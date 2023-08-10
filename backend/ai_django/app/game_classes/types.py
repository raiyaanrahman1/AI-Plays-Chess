from typing import List, Dict, Tuple, Literal
from .pieces.piece import Piece
from .pieces.pawn import Pawn
from .pieces.bishop import Bishop
from .pieces.knight import Knight
from .pieces.rook import Rook
from .pieces.queen import Queen
from .pieces.king import King
from .player import Player
from .move import Move
from typing import TypedDict


BoardType = List[List[Piece | None]]
PieceType = Piece
MoveHisType = List[Move]
MaterialType = Dict[str, Dict[str, int]]
LocType = Tuple[int, int]
PlayerType = Player
ColourType = Literal['white', 'black']
NonZeroDirectionType = Literal[1, -1]
DirectionType = Literal[-1, 0, 1]
MoveType = Move


class PieceCollection(TypedDict):
    P: List[Pawn]
    N: List[Knight]
    B: List[Bishop]
    R: List[Rook]
    Q: List[Queen]
    K: King


PieceCollectionType = PieceCollection
