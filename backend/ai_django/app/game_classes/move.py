from .utilities import loc_to_chess_notation, get_board_string, index_to_letter
from .constants import (
    SHORT_CASTLE,
    LONG_CASTLE,
    ENPASSANT_LEFT,
    ENPASSANT_RIGHT,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import (
        BoardType,
        MoveType,
        PieceCollectionType,
        LocType
    )
from .constants import PIECE_TYPES
PAWNS, KNIGHTS, BISHOPS, ROOKS, QUEENS, KINGS = PIECE_TYPES


class Move:
    def __init__(
            self,
            from_loc: 'LocType',
            to_loc: 'LocType',
            board_before_move: 'BoardType',
            board_str_before_move: str,
            special_move: 'None | str' = None
    ):
        self.from_loc = from_loc
        self.to_loc = to_loc
        self.special_move = special_move
        self.move_name: 'None | str' = None
        self.board_str_before_move = board_str_before_move
        self.move_num = -1  # index of move history - set in Logic.make_move()

        if board_before_move[from_loc[0]][from_loc[1]] is None:
            self.piece_type = None
            self.piece_id = None
            self.colour = None
            return

        self.piece_type = board_before_move[from_loc[0]][from_loc[1]].get_type()
        self.piece_id = board_before_move[from_loc[0]][from_loc[1]].id
        self.colour = board_before_move[from_loc[0]][from_loc[1]].colour

        captured_piece = self.get_captured_piece(board_before_move)
        self.is_capture = captured_piece is not None

        self.promotion_piece = None
        if special_move is not None and special_move.startswith('promote'):
            self.promotion_piece = special_move.split(':')[1]

    def __str__(self) -> str:
        if self.move_name is not None:
            return self.move_name
        if self.special_move is not None:
            return self.special_move
        from_loc_chess_not = loc_to_chess_notation(self.from_loc)
        to_loc_chess_not = loc_to_chess_notation(self.to_loc)
        return f'from: {from_loc_chess_not}, to: {to_loc_chess_not}'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other: 'MoveType'):
        # NOTE: This means that moves can be played at different times and be considered
        # equal (since move_num is not checked). It doesn't even have to be the exact same piece_id
        return (
            isinstance(other, Move)
            and self.colour == other.colour
            and self.piece_type == other.piece_type
            and self.from_loc == other.from_loc
            and self.to_loc == other.to_loc
            and self.special_move == other.special_move
        )

    def get_captured_piece(self, board: 'BoardType'):
        from_loc = self.from_loc
        to_loc = self.to_loc

        if self.special_move is None or self.special_move.startswith('promote'):
            # if capture, update opponents pieces
            if board[to_loc[0]][to_loc[1]] is not None:
                return board[to_loc[0]][to_loc[1]]

        elif self.special_move == ENPASSANT_LEFT:
            return board[from_loc[0]][from_loc[1] - 1]

        elif self.special_move == ENPASSANT_RIGHT:
            return board[from_loc[0]][from_loc[1] + 1]

        return None

    # returns the move name without any suffixes like + or #
    def get_basic_move_name(self, player_pieces: 'PieceCollectionType') -> str:
        if self.special_move in (SHORT_CASTLE, LONG_CASTLE):
            return self.special_move

        piece_type = self.piece_type

        extra_potential_from_locs = []
        if piece_type in (KNIGHTS, BISHOPS, ROOKS, QUEENS):
            for piece in player_pieces[piece_type]:
                if (
                    piece.id != self.piece_id
                    and any(other_move.to_loc == self.to_loc for other_move in piece.legal_moves)
                ):
                    extra_potential_from_locs.append(piece.loc)
        same_file_exists = False
        same_rank_exists = False
        for loc in extra_potential_from_locs:
            if loc[0] == self.from_loc[0]:
                same_rank_exists = True
            if loc[1] == self.from_loc[1]:
                same_file_exists = True

        include_from_loc = ''
        if len(extra_potential_from_locs) > 0 and not same_file_exists and not same_rank_exists:
            include_from_loc += index_to_letter(self.from_loc[1])
        if same_rank_exists:
            include_from_loc += index_to_letter(self.from_loc[1])
        if same_file_exists:
            include_from_loc += str(self.from_loc[0] + 1)

        if include_from_loc == '' and piece_type == PAWNS and self.is_capture:
            include_from_loc = index_to_letter(self.from_loc[1])

        include_piece = '' if piece_type == PAWNS else piece_type
        include_capture = 'x' if self.is_capture else ''
        include_promotion = f'={self.promotion_piece}' if self.promotion_piece is not None else ''
        to_loc_chess_not = loc_to_chess_notation(self.to_loc)
        return '{}{}{}{}{}'.format(
            include_piece,
            include_from_loc,
            include_capture,
            to_loc_chess_not,
            include_promotion
        )
