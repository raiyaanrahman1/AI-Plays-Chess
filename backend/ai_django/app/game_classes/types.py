from typing import List, Dict, Tuple, Literal
from .pieces.piece import Piece
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


class PlayerPieces(TypedDict):
    P: Dict[int, Piece]
    N: Dict[int, Piece]
    B: Dict[int, Piece]
    R: Dict[int, Piece]
    Q: Dict[int, Piece]
    K: King


PlayerPiecesType = PlayerPieces
