import json


class Board:
    def __init__(self) -> None:
        self.board = []
        self.white_pieces = {}
        self.black_pieces = {}
        self.setup_board()
        self.setup_pieces()

    def setup_board(self) -> None:
        self.board = [
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
        ]

    def setup_pieces(self) -> None:
        pieces = [self.white_pieces, self.black_pieces]
        for i in range(2):
            base_row = 0 if i == 0 else 7
            pawn_row = base_row + (base_row == 0) - (base_row != 0)
            pieces[i]['pawns'] = [[pawn_row, x] for x in range(8)]
            pieces[i]['rooks'] = [[base_row, 0], [base_row, 7]]
            pieces[i]['knights'] = [[base_row, 1], [base_row, 6]]
            pieces[i]['bishops'] = [[base_row, 2], [base_row, 5]]
            pieces[i]['queens'] = [[base_row, 3]]
            pieces[i]['king'] = [base_row, 4]

    def make_move(self) -> None:
        pass

    def __str__(self) -> str:
        return json.dumps(
                {
                    'board': self.board,
                    'white_pieces': self.white_pieces,
                    'black_pieces': self.black_pieces
                },
                indent=4
            )
