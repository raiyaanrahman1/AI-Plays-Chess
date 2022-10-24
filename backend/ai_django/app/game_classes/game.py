from pprint import pformat
from .player import Player
from .game_logic import Logic
from .move import Move
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
        self.move_history = []
        self.board = self.setup_board()

    def setup_board(self) -> None:
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
        Logic.calculate_legal_moves(
            self.white_player, self.black_player, self.board, self.move_history
        )
        Logic.calculate_legal_moves(
            self.black_player, self.white_player, self.board, self.move_history
        )

    def make_move(self, from_loc, to_loc):
        player_index = len(self.move_history) % 2
        Logic.make_move(
            self.board,
            self.players[player_index],
            self.players[1-player_index],
            self.move_history,
            Move(from_loc, to_loc, self.board)
        )

    def get_all_legal_moves(self):
        legal_moves = {'white': {}, 'black': {}}
        for player in self.players:
            for piece_type in PIECE_TYPES:
                legal_moves[player.colour][piece_type] = []
                for piece in player.pieces[piece_type].values():
                    legal_moves[player.colour][piece_type].append(piece.legal_moves)
            legal_moves[player.colour][KING] = player.pieces[KING].legal_moves

        return legal_moves

    def __str__(self) -> str:
        result = ''
        for i in range(len(self.board)):
            for piece in self.board[len(self.board) - i - 1]:
                result += '|' + (str(piece) if piece is not None else ' ')
            result += '|\n'

        return result

    def info(self) -> str:
        return 'legal moves:\n' + pformat(self.get_all_legal_moves())
