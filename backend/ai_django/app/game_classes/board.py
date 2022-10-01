# import json
from .pieces.pawn import Pawn
from .pieces.knight import Knight
from .pieces.bishop import Bishop
from .pieces.rook import Rook
from .pieces.queen import Queen
from .pieces.king import King
from .constants import PIECE_TYPES
PAWNS, ROOKS, KNIGHTS, BISHOPS, QUEENS, KING = PIECE_TYPES


class Board:
    def __init__(self) -> None:
        self.board = []
        self.white_pieces = {'colour': 'white'}
        self.black_pieces = {'colour': 'black'}
        self.player_pieces = (self.white_pieces, self.black_pieces)
        self.setup_pieces()
        self.setup_board()

    def setup_pieces(self) -> None:
        for pieces in self.player_pieces:
            base_row = 0 if pieces['color'] == 'white' else 7
            pawn_row = base_row + (base_row == 0) - (base_row != 0)
            pieces[PAWNS] = [
                Pawn(x, (pawn_row, x), pieces['colour']) for x in range(8)
            ]
            pieces[ROOKS] = [
                Rook(0, (base_row, 0), pieces['colour']),
                Rook(1, (base_row, 7), pieces['colour'])
            ]
            pieces[KNIGHTS] = [
                Knight(0, (base_row, 1), pieces['colour']),
                Knight(1, (base_row, 6), pieces['colour'])
            ]
            pieces[BISHOPS] = [
                Bishop(0, (base_row, 2), pieces['colour']),
                Bishop(1, (base_row, 5), pieces['colour'])
            ]
            pieces[QUEENS] = [Queen(0, (base_row, 3), pieces['colour'])]
            pieces[KING] = King(0, (base_row, 4), pieces['colour'])

    def setup_board(self) -> None:
        self.board = [
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
        for pieces in self.player_pieces:
            for type in PIECE_TYPES:
                for piece in pieces[type]:
                    piece.calculate_moves(self.board)

    def make_move(self) -> None:
        pass

    # def __str__(self) -> str:
    #     return json.dumps(
    #             {
    #                 'board': self.board,
    #                 'white_pieces': self.white_pieces,
    #                 'black_pieces': self.black_pieces
    #             },
    #             indent=4
    #         )
