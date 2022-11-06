from copy import deepcopy
from .utilities import in_bounds, index_to_letter, loc_to_chess_notation
from .game_errors import (
    InvalidStartPosError,
    InvalidPlayerError,
    IllegalMoveError,
    InternalInvalidStartPosError,
    InternalInvalidPlayerError,
    InternalIllegalMoveError
)
from .pieces.knight import Knight
from .pieces.bishop import Bishop
from .pieces.rook import Rook
from .pieces.queen import Queen
from .constants import PIECE_TYPES
from .constants import KING
from .constants import (
    SHORT_CASTLE,
    LONG_CASTLE,
    ENPASSANT_LEFT,
    ENPASSANT_RIGHT,
)
from .move import Move
PAWNS, KNIGHTS, BISHOPS, ROOKS, QUEENS = PIECE_TYPES


# TODO: make the order of parameters consistent for these methods
class Logic:
    @staticmethod
    def calculate_legal_moves(player, opponent, board, move_history, material, check_checks=True):
        in_check = Logic.in_check(board, player, opponent)
        player.num_legal_moves = 0

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
                            board, move_history, material, player, opponent, move
                        )
                    ),
                    piece.legal_moves
                ))
            else:
                Logic.validate_moves(board, move_history, material, piece, player, opponent)
            player.num_legal_moves += len(piece.legal_moves)

        helper(player.pieces[KING])
        for piece_type in PIECE_TYPES:
            for piece in player.pieces[piece_type].values():
                helper(piece)

        return in_check

    @staticmethod
    # this method is in the Logic class instead of the Move class for flexibility
    # i.e. - you can pass in copied parameters and not have to worry about affecting
    # the originals. See in_check_after_move for an example
    def make_move(board, player, opponent, move_history, material, move, check_checks=True):
        # set variables
        from_loc = move.from_loc
        to_loc = move.to_loc
        piece = board[from_loc[0]][from_loc[1]]
        captured_piece = None
        promotion_piece = None

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

        if move.special_move is None:
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

        elif move.special_move == SHORT_CASTLE:
            piece.set_loc(to_loc)
            player.pieces[ROOKS][1].set_loc((to_loc[0], to_loc[1] - 1))

            board[from_loc[0]][from_loc[1]] = None
            board[to_loc[0]][to_loc[1] + 1] = None
            board[to_loc[0]][to_loc[1]] = piece
            board[to_loc[0]][to_loc[1] - 1] = player.pieces[ROOKS][1]

        elif move.special_move == LONG_CASTLE:
            piece.set_loc(to_loc)
            player.pieces[ROOKS][0].set_loc((to_loc[0], to_loc[1] + 1))

            board[from_loc[0]][from_loc[1]] = None
            board[to_loc[0]][to_loc[1] - 2] = None
            board[to_loc[0]][to_loc[1]] = piece
            board[to_loc[0]][to_loc[1] + 1] = player.pieces[ROOKS][0]

        elif move.special_move == ENPASSANT_LEFT:
            captured_piece = board[from_loc[0]][from_loc[1] - 1]
            del opponent.pieces[PAWNS][captured_piece.id]

            piece.set_loc(to_loc)

            # update board
            board[from_loc[0]][from_loc[1]] = None
            board[to_loc[0]][to_loc[1]] = piece

        elif move.special_move == ENPASSANT_RIGHT:
            captured_piece = board[from_loc[0]][from_loc[1] + 1]
            del opponent.pieces[PAWNS][captured_piece.id]

            piece.set_loc(to_loc)

            # update board
            board[from_loc[0]][from_loc[1]] = None
            board[to_loc[0]][to_loc[1]] = piece

        elif move.special_move.startswith('promote'):
            # if capture, update opponents pieces
            if board[to_loc[0]][to_loc[1]] is not None:
                assert board[to_loc[0]][to_loc[1]].colour != player.colour
                captured_piece = board[to_loc[0]][to_loc[1]]
                del opponent.pieces[captured_piece.get_type()][captured_piece.id]

            # delete pawn
            del player.pieces[PAWNS][piece.id]

            promotion_piece = move.special_move.split(':')[1]
            piece_type_to_class = {
                QUEENS: Queen,
                ROOKS: Rook,
                BISHOPS: Bishop,
                KNIGHTS: Knight
            }
            piece_class = piece_type_to_class[promotion_piece]
            piece_id = len(player.pieces[promotion_piece])
            new_piece = piece_class(piece_id, to_loc, player.colour)
            player.pieces[promotion_piece][piece_id] = new_piece

            # update board
            board[from_loc[0]][from_loc[1]] = None
            board[to_loc[0]][to_loc[1]] = new_piece

        # update move history
        move.move_num = len(move_history)
        move_history.append(move)

        # update material
        is_capture = captured_piece is not None
        if is_capture and captured_piece.get_type() != KING:
            material[player.colour][captured_piece.get_type()] += 1
        if promotion_piece is not None:
            material[player.colour][promotion_piece.get_type()] += 1
            material[opponent.colour][PAWNS] += 1

        # update legal moves
        Logic.calculate_legal_moves(player, opponent, board, move_history, material, check_checks)
        opponent_in_check = Logic.calculate_legal_moves(
            opponent, player, board, move_history, material, check_checks
        )

        game_status = {'game_finished': False}

        move_name_suffix = '+' if opponent_in_check else ''
        # check for checkmate
        if opponent_in_check and opponent.num_legal_moves == 0:
            game_status['game_finished'] = True
            game_status['game_result'] = 'checkmate'
            game_status['winner'] = player.colour
            game_status['game_result_message'] = f'{player.colour} won by checkmate'
            move_name_suffix = '#'

        # check for stalemate
        elif opponent.num_legal_moves == 0:
            game_status['game_finished'] = True
            game_status['game_result'] = 'draw'
            game_status['draw_by'] = 'stalemate'
            game_status['game_result_message'] = 'stalemate'

        elif Logic.is_draw():
            game_status['game_finished'] = True
            game_status['game_result'] = 'draw'
            # TODO: implement
            game_status['draw_by'] = 'not implemented'
            game_status['game_result_message'] = 'not implemented'

        move.move_name = Logic.get_move_name(move, is_capture, move_name_suffix, player.pieces)
        return game_status

    @staticmethod
    def get_move_name(move, is_capture, suffix, player_pieces) -> str:
        piece_type = move.piece_type

        extra_potential_from_locs = []
        if piece_type in (KNIGHTS, BISHOPS, ROOKS, QUEENS):
            for piece in player_pieces[piece_type]:
                if (
                    piece.id != move.piece_id
                    and any(other_move.to_loc == move.to_loc for other_move in piece.legal_moves)
                ):
                    extra_potential_from_locs.append(piece.loc)
        same_file_exists = False
        same_rank_exists = False
        for loc in extra_potential_from_locs:
            if loc[0] == move.from_loc[0]:
                same_rank_exists = True
            if loc[1] == move.from_loc[1]:
                same_file_exists = True

        include_from_loc = ''
        if len(extra_potential_from_locs) > 0 and not same_file_exists and not same_rank_exists:
            include_from_loc += index_to_letter(move.from_loc[1])
        if same_rank_exists:
            include_from_loc += index_to_letter(move.from_loc[1])
        if same_file_exists:
            include_from_loc += move.from_loc[0] + 1

        include_piece = '' if piece_type == PAWNS else piece_type
        include_capture = 'x' if is_capture else ''
        to_loc_chess_not = loc_to_chess_notation(move.to_loc)
        return f'{include_piece}{include_from_loc}{include_capture}{to_loc_chess_not}{suffix}'

    # TODO: need to check 3-fold repetition, 50 move rule, insufficient mating material
    @staticmethod
    def is_draw():
        return False

    # Might want to move this method into Piece to avoid an extra loop when filtering
    # Would have to pass in player
    @staticmethod
    def in_check_after_move(board, move_history, material, player, opponent, move) -> bool:
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
            material,
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
    def validate_moves(board, move_history, material, piece, player, opponent):
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
                        board, move_history, material, player, opponent, moves_to_check[i]
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
