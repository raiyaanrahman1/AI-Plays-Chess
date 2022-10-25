def in_bounds(loc):
    return 0 <= loc[0] <= 7 and 0 <= loc[1] <= 7


def loc_to_chess_notation(loc):
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
    return f'{INDEX_TO_LETTER_MAP[loc[1]]}{loc[0] + 1}'
