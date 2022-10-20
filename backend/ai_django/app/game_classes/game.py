from .player import Player
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
        for player in self.players:
            player.calculate_legal_moves(self.board, self.move_history)

    def make_move(self, from_loc, to_loc):
        try:
            self.board.make_move(from_loc, to_loc)
        except Exception as err:
            print(str(err))
