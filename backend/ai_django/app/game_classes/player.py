from copy import deepcopy
from .utilities import in_bounds
from .pieces.pawn import Pawn
from .pieces.knight import Knight
from .pieces.bishop import Bishop
from .pieces.rook import Rook
from .pieces.queen import Queen
from .pieces.king import King
from .constants import PIECE_TYPES
from .constants import KING
PAWNS, KNIGHTS, BISHOPS, ROOKS, QUEENS = PIECE_TYPES


class Player:
    def __init__(self, colour) -> None:
        self.colour = colour
        self.direction = 1 if self.colour == 'white' else -1
        self.pieces = self.setup_pieces()

    def setup_pieces(self) -> None:
        pieces = {}
        base_row = 0 if self.colour == 'white' else 7
        pawn_row = base_row + (base_row == 0) - (base_row != 0)
        pieces[PAWNS] = [
            Pawn(x, (pawn_row, x), self.colour) for x in range(8)
        ]
        pieces[ROOKS] = [
            Rook(0, (base_row, 0), self.colour),
            Rook(1, (base_row, 7), self.colour)
        ]
        pieces[KNIGHTS] = [
            Knight(0, (base_row, 1), self.colour),
            Knight(1, (base_row, 6), self.colour)
        ]
        pieces[BISHOPS] = [
            Bishop(0, (base_row, 2), self.colour),
            Bishop(1, (base_row, 5), self.colour)
        ]
        pieces[QUEENS] = [Queen(0, (base_row, 3), self.colour)]
        pieces[KING] = King(0, (base_row, 4), self.colour)
        return pieces

    def calculate_legal_moves(self, other_player, board, move_history):
        in_check = self.in_check(board, other_player)

        def helper(piece):
            piece.calculate_moves(board, move_history)
            if in_check:
                piece.legal_moves = filter(
                    lambda move: not self.in_check_after_move(
                        board, other_player, piece.loc, move
                    ),
                    piece.legal_moves
                )
            else:
                self.validate_moves(board, piece, other_player)

        helper(self.pieces[KING])
        for piece_type in PIECE_TYPES:
            for piece in self.pieces[piece_type]:
                helper(piece)

    # Might want to move this method into Piece to avoid an extra loop when filtering
    # Would have to pass in player
    def in_check_after_move(self, board, move_history, other_player, from_loc, to_loc) -> bool:
        # to avoid deep-copying the board, we can make the changes on the board itself
        # and then reverse the changes
        board_from = board[from_loc[0]][from_loc[1]]
        board_to = board[to_loc[0]][to_loc[1]]
        temp_self = deepcopy(self)
        temp_opponent = deepcopy(other_player)
        copied_from = temp_self.pieces[board_from.get_type()][board_from.id]
        # copied_to = temp_opponent.pieces[board_to.get_type()][board_to.id]
        if board_to is not None and board_to.colour == self.colour:
            raise TypeError('Cannot move to your own piece')
        if board_to is not None:
            temp_opponent.pieces[board_to.get_type()].pop(board_to.id)

        copied_from.row = to_loc[0]
        copied_from.col = to_loc[1]
        board[from_loc[0]][from_loc[1]] = None
        board[to_loc[0]][to_loc[1]] = board_from
        # TODO: append move to move_history

        temp_self.calculate_legal_moves(temp_opponent, board, move_history)
        temp_opponent.calculate_legal_moves(temp_self, board, move_history)

        in_check = self.in_check(board, other_player)

        # TODO: uncomment this line: move_history.pop()
        board[from_loc[0]][from_loc[1]] = board_from
        board[to_loc[0]][to_loc[1]] = board_to

        return in_check

    # filters the pieces moves such that after the move is made, the player's king is not in check
    # pre-condition: the king is not currently in check
    def validate_moves(self, board, piece, other_player):
        if piece.get_type() == KING:
            self.pieces[KING].legal_moves = filter(
                lambda move: not self.in_check_after_move(board, other_player, piece.loc, move),
                self.pieces[KING].legal_moves
            )

            # TODO: implement special case for castling
            return

        king_row, king_col = self.pieces[KING].loc

        def validate_in_dir(x_dir, y_dir):
            dist = 1
            found_piece = False
            while in_bounds((loc := (king_row + x_dir * dist, king_col + y_dir * dist))):
                board_loc = board[loc[0]][loc[1]]
                if not found_piece and board_loc is not None and board_loc.colour != self.colour:
                    return
                elif found_piece and board_loc is not None and board_loc.colour == self.colour:
                    return
                elif not found_piece and board_loc is not None and board_loc.colour == self.colour:
                    found_piece = True
                    piece = board_loc
                    valid_moves = []
                elif found_piece and board_loc is None:
                    valid_moves.append(loc)
                elif found_piece and board_loc is not None and board_loc.colour != self.colour:
                    valid_moves.append(loc)
                    piece.legal_moves = filter(
                        lambda move_loc: move_loc in valid_moves,
                        piece.legal_moves
                    )
                dist += 1

        for x_dir in (0, 1, -1):
            for y_dir in (0, 1, -1):
                if x_dir == 0 and y_dir == 0:
                    continue
                validate_in_dir(x_dir, y_dir)

    def in_check(self, board, other_player) -> bool:
        # Might want to reimplement by calculating lines from the king (and knight paths)
        # Why? Average branching-factor (i.e. number of legal moves in a position) is 35
        # Number of squares needed using lines is also 35 but that's in the worst case
        # so it could improve performance
        for piece_type in [KNIGHTS, BISHOPS, ROOKS, QUEENS]:
            for piece in other_player[piece_type]:
                if self.pieces[KING].loc in other_player[piece_type][piece].legal_moves:
                    return True

        # the other King can't actually put the player in check
        # this is simply to prevent the kings from being adjacent
        if self.pieces[KING].loc in other_player[KING].legal_moves:
            return True

        left_diag = (self.row + 1 * self.direction, self.col - 1)
        right_diag = (self.row + 1 * self.direction, self.col + 1)

        for loc in (left_diag, right_diag):
            if not in_bounds(loc):
                continue
            board_at_loc = board[loc[0]][loc[1]]
            if (
                board_at_loc is not None
                and board_at_loc.colour != self.colour
                and board_at_loc.get_type == PAWNS
            ):
                return True

        return False
