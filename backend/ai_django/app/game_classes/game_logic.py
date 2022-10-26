from copy import deepcopy
from .utilities import in_bounds
from .game_errors import (
    InvalidStartPosError,
    InvalidPlayerError,
    IllegalMoveError,
    InternalInvalidStartPosError,
    InternalInvalidPlayerError,
    InternalIllegalMoveError
)
from .constants import PIECE_TYPES
from .constants import KING
from .constants import SHORT_CASTLE, LONG_CASTLE
from .move import Move
PAWNS, KNIGHTS, BISHOPS, ROOKS, QUEENS = PIECE_TYPES


# TODO: make the order of parameters consistent for these methods
class Logic:
    @staticmethod
    def calculate_legal_moves(player, opponent, board, move_history, check_checks=True):
        in_check = Logic.in_check(board, player, opponent)

        def helper(piece):
            piece.calculate_moves(board, move_history)
            if not check_checks:
                return
            if in_check:
                piece.legal_moves = list(filter(
                    lambda move: (
                        move.special_move != SHORT_CASTLE  # Can't castle when in check
                        and move.special_move != LONG_CASTLE  # Can't castle when in check
                        and not Logic.in_check_after_move(
                            board, move_history, player, opponent, move
                        )
                    ),
                    piece.legal_moves
                ))
            else:
                Logic.validate_moves(board, move_history, piece, player, opponent)

        helper(player.pieces[KING])
        for piece_type in PIECE_TYPES:
            for piece in player.pieces[piece_type].values():
                helper(piece)

    @staticmethod
    # this method is in the Logic class instead of the Move class for flexibility
    # i.e. - you can pass in copied parameters and not have to worry about affecting
    # the originals. See in_check_after_move for an example
    def make_move(board, player, opponent, move_history, move, check_checks=True):
        # set variables
        from_loc = move.from_loc
        to_loc = move.to_loc
        piece = board[from_loc[0]][from_loc[1]]

        # error checking
        if piece is None:
            error = InvalidStartPosError if check_checks else InternalInvalidStartPosError
            raise error(from_loc)
        if piece.colour != player.colour:
            error = InvalidPlayerError if check_checks else InternalInvalidPlayerError
            raise error(piece.colour)
        if move not in piece.legal_moves:
            error = IllegalMoveError if check_checks else InternalIllegalMoveError
            raise error(
                piece.colour, piece.get_name(), move.from_loc, move.to_loc, move.special_move
            )

        # set castling rights
        if piece.get_type() == KING:
            piece.short_castle_rights = False
            piece.long_castle_rights = False

        if piece.get_type() == ROOKS:
            if piece.id == 0:
                player.pieces[KING].long_castle_rights = False
            elif piece.id == 1:
                player.pieces[KING].short_castle_rights = False

        if (move.special_move is None):
            # if capture, update opponents pieces
            if board[to_loc[0]][to_loc[1]] is not None:
                assert board[to_loc[0]][to_loc[1]].colour != player.colour
                captured_piece = board[to_loc[0]][to_loc[1]]
                del opponent.pieces[captured_piece.get_type()][captured_piece.id]

            # update piece location
            piece.set_loc(to_loc)

            # update board
            board[from_loc[0]][from_loc[1]] = None
            board[to_loc[0]][to_loc[1]] = piece

            # update move history
            move.move_num = len(move_history)
            move_history.append(move)
        else:
            pass  # TODO: implement

        # update legal moves
        Logic.calculate_legal_moves(player, opponent, board, move_history, check_checks)
        Logic.calculate_legal_moves(opponent, player, board, move_history, check_checks)

    # Might want to move this method into Piece to avoid an extra loop when filtering
    # Would have to pass in player
    @staticmethod
    def in_check_after_move(board, move_history, player, opponent, move) -> bool:
        # to avoid deep-copying the board, we can make the changes on the board itself
        # and then reverse the changes
        from_loc = move.from_loc
        to_loc = move.to_loc
        board_from = board[from_loc[0]][from_loc[1]]
        board_to = board[to_loc[0]][to_loc[1]]
        temp_player = deepcopy(player)
        temp_opponent = deepcopy(opponent)
        piece = temp_player.pieces[board_from.get_type()] if board_from.get_type() == KING \
            else temp_player.pieces[board_from.get_type()][board_from.id]
        board[from_loc[0]][from_loc[1]] = piece
        if board_to is not None and board_to.colour == player.colour:
            raise InternalIllegalMoveError(
                player.colour, board_from.get_name(), from_loc, to_loc, move.special_move
            )
        if board_to is not None:
            temp_opponent.pieces[board_to.get_type()].pop(board_to.id)

        Logic.make_move(
            board,
            temp_player,
            temp_opponent,
            move_history,
            Move(from_loc, to_loc, board, move.special_move),
            False
        )

        in_check = Logic.in_check(board, player, opponent)

        move_history.pop()
        board[from_loc[0]][from_loc[1]] = board_from
        board[to_loc[0]][to_loc[1]] = board_to

        return in_check

    # filters the pieces moves such that after the move is made, the player's king is not in check
    # pre-condition: the king is not currently in check
    @staticmethod
    def validate_moves(board, move_history, piece, player, opponent):
        if piece.get_type() == KING:
            legal_moves = []
            for move in piece.legal_moves:
                moves_to_check = []
                if move.special_move == SHORT_CASTLE:
                    moves_to_check.append(Move(piece.loc, (piece.loc[0], piece.loc[1] + 1), board))
                    moves_to_check.append(
                        Move(piece.loc, (piece.loc[0], piece.loc[1] + 2), board, SHORT_CASTLE)
                    )
                elif move.special_move == LONG_CASTLE:
                    moves_to_check.append(Move(piece.loc, (piece.loc[0], piece.loc[1] - 1), board))
                    moves_to_check.append(
                        Move(piece.loc, (piece.loc[0], piece.loc[1] - 2), board, LONG_CASTLE)
                    )
                else:
                    moves_to_check.append(move)
                i = 0
                moves_are_legal = True
                while (i < len(moves_to_check) and moves_are_legal):
                    moves_are_legal = not Logic.in_check_after_move(
                        board, move_history, player, opponent, moves_to_check[i]
                    )
                    i += 1
                if moves_are_legal:
                    legal_moves.append(move)

            player.pieces[KING].legal_moves = legal_moves
            return

        king_row, king_col = player.pieces[KING].loc

        def validate_in_dir(x_dir, y_dir):
            dist = 1
            found_piece = False
            while in_bounds((loc := (king_row + x_dir * dist, king_col + y_dir * dist))):
                board_loc = board[loc[1]][loc[0]]
                if not found_piece and board_loc is not None and board_loc.colour != player.colour:
                    return
                elif found_piece and board_loc is not None and board_loc.colour == player.colour:
                    return
                elif (
                    not found_piece
                    and board_loc is not None
                    and board_loc.colour == player.colour
                ):
                    found_piece = True
                    piece = board_loc
                    valid_moves = []
                elif found_piece and board_loc is None:
                    valid_moves.append(loc)
                elif found_piece and board_loc is not None and board_loc.colour != player.colour:
                    piece_type = board_loc.get_type()
                    if (
                        piece_type == QUEENS
                        or ((x_dir == 0 or y_dir == 0) and piece_type == ROOKS)
                        or (x_dir != 0 and y_dir != 0 and piece_type == BISHOPS)
                    ):
                        valid_moves.append(loc)
                        piece.legal_moves = list(filter(
                            lambda move_loc: move_loc in valid_moves,
                            piece.legal_moves
                        ))
                dist += 1

        for x_dir in (0, 1, -1):
            for y_dir in (0, 1, -1):
                if x_dir == 0 and y_dir == 0:
                    continue
                validate_in_dir(x_dir, y_dir)

    @staticmethod
    def in_check(board, player, opponent) -> bool:
        # Might want to reimplement by calculating lines from the king (and knight paths)
        # Why? Average branching-factor (i.e. number of legal moves in a position) is 35
        # Number of squares needed using lines is also 35 but that's in the worst case
        # so it could improve performance
        for piece_type in [KNIGHTS, BISHOPS, ROOKS, QUEENS]:
            for piece in opponent.pieces[piece_type].values():
                if Move(piece.loc, player.pieces[KING].loc, board) in piece.legal_moves:
                    return True

        # the other King can't actually put the player in check
        # this is simply to prevent the kings from being adjacent
        if (Move(opponent.pieces[KING].loc, player.pieces[KING].loc, board)
                in opponent.pieces[KING].legal_moves):
            return True

        left_diag = (player.pieces[KING].row + 1 * player.direction, player.pieces[KING].col - 1)
        right_diag = (player.pieces[KING].row + 1 * player.direction, player.pieces[KING].col + 1)

        for loc in (left_diag, right_diag):
            if not in_bounds(loc):
                continue
            board_at_loc = board[loc[0]][loc[1]]
            if (
                board_at_loc is not None
                and board_at_loc.colour != player.colour
                and board_at_loc.get_type == PAWNS
            ):
                return True

        return False
