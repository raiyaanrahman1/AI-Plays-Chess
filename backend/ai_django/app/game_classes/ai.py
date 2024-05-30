from .utilities import (
    in_bounds, colour_of_square, get_board_string
)
from .game_errors import (
    InvalidStartPosError,
    InvalidPlayerError,
    IllegalMoveError,
    InternalInvalidStartPosError,
    InternalInvalidPlayerError,
    InternalIllegalMoveError
)
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .types import (
        BoardType,
        MoveHisType,
        MaterialType,
        PlayerType,
        MoveType,
        PieceCollectionType,
        PieceType,
        DirectionType,
        LocType
    )

from . import settings
import math
import heapq
from .game_logic import Logic
from .pieces.knight import Knight
from .pieces.bishop import Bishop
from .pieces.rook import Rook
from .pieces.queen import Queen
from .pieces.pawn import Pawn
from .pieces.king import King
from .constants import PIECE_TYPES
from .constants import (
    SHORT_CASTLE,
    LONG_CASTLE,
    ENPASSANT_LEFT,
    ENPASSANT_RIGHT,
)
from .move import Move
from .player import Player
PAWNS, KNIGHTS, BISHOPS, ROOKS, QUEENS, KINGS = PIECE_TYPES


class ChessAI:
    @staticmethod
    @staticmethod
    def calculate_deep_moves(
        board: 'BoardType',
        move_history: 'MoveHisType',
        material: 'MaterialType',
        player: 'PlayerType',
        opponent: 'PlayerType',
        game_status,
        depth: int,
        currentTree=None,
        alpha: float = -math.inf,
        beta: float = math.inf,
    ):
        curr_state = {
            'move_before_current_state': move_history[-1] if len(move_history) > 0 else None,
            'game_state_after_move': {
                'board': board,
                'player': player,
                'opponent': opponent,
                'move_history': move_history,
                'material': material,
                'game_status': game_status,
                'move_history_str': str(move_history),
            },
            'children': {},
            'best_move': None,
            'best_move_node': None,
        }

        if currentTree is None:
            currentTree = curr_state

        def evaluate_position(player: 'PlayerType', opponent: 'PlayerType', material: 'MaterialType', game_status):
            if game_status['winner'] is not None:
                return (-1) ** (game_status['winner'] == 'black') * math.inf

            if game_status['game_result'] == 'draw':
                return 0

            num_legal_moves = [player.num_legal_moves, opponent.num_legal_moves]
            mat = [0, 0]
            for i, p in enumerate((player, opponent)):
                mat[i] += (
                    material[p.colour][PAWNS]
                    + material[p.colour][KNIGHTS] * 3
                    + material[p.colour][BISHOPS] * 3
                    + material[p.colour][ROOKS] * 5
                    + material[p.colour][QUEENS] * 9
                )

            white_player = 1 - int(player.colour == 'white')
            black_player = 1 - white_player
            return mat[white_player] - mat[black_player] + (num_legal_moves[white_player] - num_legal_moves[black_player]) / 50

        if depth == 0:
            currentTree['eval'] = evaluate_position(player, opponent, material, game_status)
            return currentTree

        curr_eval = (-1) ** (player.colour == 'white') * math.inf

        legal_moves = []
        for piece_type in player.pieces:
            for piece in player.pieces[piece_type]:
                for move in piece.legal_moves:
                    from_loc = move.from_loc
                    to_loc = move.to_loc

                    temp_player = Logic.copy_player(player)
                    temp_opponent = Logic.copy_player(opponent)
                    temp_board = Logic.get_board_from_pieces(temp_player.pieces, temp_opponent.pieces)
                    temp_board_str = get_board_string(temp_board)
                    temp_material = Logic.copy_material(material)
                    temp_move_history = Logic.copy_move_history(move_history)

                    game_status = Logic.make_move(
                        temp_board,
                        temp_player,
                        temp_opponent,
                        temp_move_history,
                        temp_material,
                        Move(from_loc, to_loc, temp_board, temp_board_str, move.special_move),
                        temp_board_str
                    )
                    legal_moves.append({
                        'move_before_current_state': move,
                        'game_state_after_move': {
                            'board': temp_board,
                            'player': temp_opponent,
                            'opponent': temp_player,
                            'move_history': temp_move_history,
                            'material': temp_material,
                            'game_status': game_status,
                            'move_history_str': str(temp_move_history),
                        },
                        'children': {},
                        'best_move': None,
                        'best_move_node': None,
                        'eval': evaluate_position(temp_player, temp_opponent, temp_material, game_status)
                    })
        legal_moves.sort(key=lambda state: state['eval'], reverse=player.colour == 'white')
        max_or_min = max if player.colour == 'white' else min

        for game_info in legal_moves:
            move = game_info['move_before_current_state']
            if depth > 0 and beta > alpha:
                move_id = move.id
                child_move_in_currentTree = currentTree is not None and move_id in currentTree['children']
                
                prev_state = currentTree['children'][move_id] if child_move_in_currentTree else game_info

                child_state = ChessAI.calculate_deep_moves(
                    prev_state['game_state_after_move']['board'],
                    prev_state['game_state_after_move']['move_history'],
                    prev_state['game_state_after_move']['material'],
                    prev_state['game_state_after_move']['player'],
                    prev_state['game_state_after_move']['opponent'],
                    prev_state['game_state_after_move']['game_status'],
                    depth - 1,
                    prev_state,
                    alpha,
                    beta
                )
                eval = child_state['eval']

                curr_eval = max_or_min(curr_eval, eval)
                if curr_eval == eval:
                    currentTree['best_move'] = move
                    currentTree['best_move_node'] = child_state

                alpha_or_beta = alpha if player.colour == 'white' else beta
                alpha_or_beta = max_or_min(alpha_or_beta, curr_eval)

                if not child_move_in_currentTree:
                    currentTree['children'][move_id] = child_state

        currentTree['eval'] = curr_eval
        return currentTree