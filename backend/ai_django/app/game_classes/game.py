from pprint import pformat
from .player import Player
from .game_logic import Logic
from .utilities import get_board_string, get_board_representation
from .move import Move
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import (
        BoardType,
        MoveType,
        LocType,
        MaterialType,
        MoveHisType
    )
from .constants import PIECE_TYPES
from .constants import KING
PAWNS, KNIGHTS, BISHOPS, ROOKS, QUEENS = PIECE_TYPES


class Game:
    def __init__(self) -> None:
        self.white_player = Player('white')
        self.white_pieces = self.white_player.pieces
        self.black_player = Player('black')
        self.black_pieces = self.black_player.pieces
        self.players = (self.white_player, self.black_player)
        self.player_pieces = (self.white_player.pieces, self.black_player.pieces)
        self.move_history: 'MoveHisType' = []
        self.material: 'MaterialType' = {
            'white': {PAWNS: 0, KNIGHTS: 0, BISHOPS: 0, ROOKS: 0, QUEENS: 0},
            'black': {PAWNS: 0, KNIGHTS: 0, BISHOPS: 0, ROOKS: 0, QUEENS: 0},
        }
        self.board = self.setup_board()
        self.game_status = {
            'game_finished': False,
            'white_in_check': False,
            'black_in_check': False,
            'last_move_was_capture': False
        }

    def setup_board(self) -> 'BoardType':
        return [
            [
                self.white_pieces[ROOKS][0],
                self.white_pieces[KNIGHTS][0],
                self.white_pieces[BISHOPS][0],
                self.white_pieces[QUEENS][0],
                self.white_pieces[KING],
                self.white_pieces[BISHOPS][1],
                self.white_pieces[KNIGHTS][1],
                self.white_pieces[ROOKS][1],
            ],
            [self.white_pieces[PAWNS][i] for i in range(8)],
            [None for _ in range(8)],
            [None for _ in range(8)],
            [None for _ in range(8)],
            [None for _ in range(8)],
            [self.black_pieces[PAWNS][i] for i in range(8)],
            [
                self.black_pieces[ROOKS][0],
                self.black_pieces[KNIGHTS][0],
                self.black_pieces[BISHOPS][0],
                self.black_pieces[QUEENS][0],
                self.black_pieces[KING],
                self.black_pieces[BISHOPS][1],
                self.black_pieces[KNIGHTS][1],
                self.black_pieces[ROOKS][1],
            ],
        ]

    def calculate_legal_moves(self) -> None:
        Logic.calculate_moves_for_both_players(
            self.white_player, self.black_player, self.board, self.move_history, self.material
        )

    def make_move(self, from_loc: 'LocType', to_loc: 'LocType', special_move: str | None = None):
        player_index = len(self.move_history) % 2
        self.game_status = Logic.make_move(
            self.board,
            self.players[player_index],
            self.players[1-player_index],
            self.move_history,
            self.material,
            Move(from_loc, to_loc, self.board, special_move)
        )

    def get_all_legal_moves(self):

        def get_move_info(move: 'MoveType'):
            return {
                'from_loc': move.from_loc,
                'to_loc': move.to_loc,
                'special_move': move.special_move,
                'move_str': str(move)
            }

        legal_moves = {
            'white': {},
            'black': {},
            'white_num_legal_moves': self.white_player.num_legal_moves,
            'black_num_legal_moves': self.black_player.num_legal_moves
        }
        for player in self.players:
            for piece_type in PIECE_TYPES:
                legal_moves[player.colour][piece_type] = []
                for piece in player.pieces[piece_type].values():
                    legal_moves[player.colour][piece_type].append(
                        [get_move_info(move) for move in piece.legal_moves]
                    )
            legal_moves[player.colour][KING] = [
                get_move_info(move) for move in player.pieces[KING].legal_moves
            ]

        return legal_moves

    def __str__(self) -> str:
        return get_board_string(self.board)

    def get_board_repr(self):
        return get_board_representation(self.board)

    def info(self) -> str:
        return 'legal moves:\n' + pformat(self.get_all_legal_moves()) \
            + '\nmove history:\n' + pformat(self.move_history) \
            + '\nmaterial:\n' + pformat(self.material) \
            + '\ngame status: ' + pformat(self.game_status)
