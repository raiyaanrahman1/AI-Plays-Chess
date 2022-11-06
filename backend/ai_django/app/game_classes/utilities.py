def in_bounds(loc):
    return 0 <= loc[0] <= 7 and 0 <= loc[1] <= 7


def index_to_letter(index):
    INDEX_TO_LETTER_MAP = {
        0: 'a',
        1: 'b',
        2: 'c',
        3: 'd',
        4: 'e',
        5: 'f',
        6: 'g',
        7: 'h',
    }
    return INDEX_TO_LETTER_MAP[index]


def loc_to_chess_notation(loc):
    return f'{index_to_letter(loc[1])}{loc[0] + 1}'


def get_board_string(board) -> str:
    result = ''
    for i in range(len(board)):
        for piece in board[len(board) - i - 1]:
            result += '|' + (str(piece) if piece is not None else ' ')
        result += '|\n'

    return result


def colour_of_square(loc) -> str:
    return 'black' if loc[0] % 2 == loc[1] % 2 else 'white'
