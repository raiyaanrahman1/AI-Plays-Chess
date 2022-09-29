# import json
from .pieces.pawn import Pawn
from .pieces.knight import Knight
from .pieces.bishop import Bishop
from .pieces.rook import Rook
from .pieces.queen import Queen
from .pieces.king import King
from .constants import PAWNS, ROOKS, KNIGHTS, BISHOPS, QUEENS, KING


class Board:
    def __init__(self) -> None:
        self.board = []
        self.white_pieces = {}
        self.black_pieces = {}
        self.setup_pieces()
        self.setup_board()

    def setup_pieces(self) -> None:
        pieces = [self.white_pieces, self.black_pieces]
        for i in range(2):
            base_row = 0 if i == 0 else 7
            pawn_row = base_row + (base_row == 0) - (base_row != 0)
            pieces[i][PAWNS] = [Pawn(x, [pawn_row, x]) for x in range(8)]
            pieces[i][ROOKS] = [
                Rook(0, [base_row, 0]),
                Rook(1, [base_row, 7])
            ]
            pieces[i][KNIGHTS] = [
                Knight(0, [base_row, 1]), Knight(1, [base_row, 6])
            ]
            pieces[i][BISHOPS] = [
                Bishop(0, [base_row, 2]), Bishop(1, [base_row, 5])
            ]
            pieces[i][QUEENS] = [Queen(0, [base_row, 3])]
            pieces[i][KING] = King(0, [base_row, 4])

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
