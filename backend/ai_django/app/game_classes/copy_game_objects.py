from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .types import (
        MoveHisType,
        MaterialType,
        PlayerType,
        PieceType,
    )

from .constants import PIECE_TYPES
from .player import Player
PAWNS, KNIGHTS, BISHOPS, ROOKS, QUEENS, KINGS = PIECE_TYPES

from .pieces.knight import Knight
from .pieces.bishop import Bishop
from .pieces.rook import Rook
from .pieces.queen import Queen
from .pieces.pawn import Pawn
from .pieces.king import King

class CopyGameObjects:
    @staticmethod
    def copy_player(player: 'PlayerType') -> 'PlayerType':
        new_player: 'PlayerType' = Player(player.colour)
        new_player.pieces = {
            PAWNS: [],
            KNIGHTS: [],
            BISHOPS: [],
            ROOKS: [],
            KINGS: [],
            QUEENS: []
        }
        for piece_type in PIECE_TYPES:
            for piece in player.pieces[piece_type]:
                new_player.pieces[piece_type].append(CopyGameObjects.copy_piece(piece))

        return new_player
    
    @staticmethod
    def copy_piece(piece: 'PieceType') -> 'PieceType':
        piece_type_to_class = {
            PAWNS: Pawn,
            KNIGHTS: Knight,
            BISHOPS: Bishop,
            ROOKS: Rook,
            QUEENS: Queen,
            KINGS: King,
        }
        new_piece: PieceType = piece_type_to_class[piece.get_type()](piece.id, piece.loc, piece.colour)
        new_piece.legal_moves = piece.legal_moves  # TODO: This might mess up stuff, but should be fine for now since
                                                    # we always recalculate legal moves by reassigning it to an empty array and
                                                    # filling it
        if piece.get_type() == KINGS:
            new_piece.short_castle_rights = piece.short_castle_rights
            new_piece.long_castle_rights = piece.long_castle_rights
        return new_piece
    
    @staticmethod
    def copy_move_history(move_history: 'MoveHisType') -> 'MoveHisType':
        return [move for move in move_history]

    @staticmethod
    def copy_material(material: 'MaterialType') -> 'MaterialType':
        return {colour: {piece_type: material[colour][piece_type] for piece_type in material[colour]} for colour in material}
