from copy import deepcopy
from .utilities import (
    in_bounds, colour_of_square, get_board_string
)
from .game_errors import (
    InvalidStartPosError,
    InvalidPlayerError,
    IllegalMoveError,
    InternalInvalidStartPosError,
    InternalInvalidPlayerError,
    InternalIllegalMoveError
)
from typing import List
from . import settings
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
    def calculate_moves_for_both_players(
        player, opponent, board, move_history, material, check_checks=True
    ):
        player.pieces[KING].calculate_moves(board, move_history)
        opponent.pieces[KING].calculate_moves(board, move_history)
        for piece_type in PIECE_TYPES:
            for piece in player.pieces[piece_type].values():
                piece.calculate_moves(board, move_history)
            for piece in opponent.pieces[piece_type].values():
                piece.calculate_moves(board, move_history)

        player_in_check = Logic.calculate_legal_moves(
            player, opponent, board, move_history, material, check_checks
        )
        opponent_in_check = Logic.calculate_legal_moves(
            opponent, player, board, move_history, material, check_checks
        )

        result = (player_in_check, opponent_in_check)

        if not settings.debug:
            return result

        def set_move_names(moves: List[Move], player_pieces):
            for move in moves:
                move.move_name = move.get_basic_move_name(player_pieces)

        set_move_names(player.pieces[KING].legal_moves, player.pieces)
        set_move_names(opponent.pieces[KING].legal_moves, opponent.pieces)

        for piece_type in PIECE_TYPES:
            for piece in player.pieces[piece_type].values():
                set_move_names(piece.legal_moves, player.pieces)
            for piece in opponent.pieces[piece_type].values():
                set_move_names(piece.legal_moves, opponent.pieces)

        return result

    @staticmethod
    def calculate_legal_moves(player, opponent, board, move_history, material, check_checks=True):
        in_check = Logic.in_check(board, player, opponent)
        player.num_legal_moves = 0

        def helper(piece):
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
        captured_piece = move.get_captured_piece(board)
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

        if captured_piece is not None:
            assert captured_piece.colour != player.colour
            del opponent.pieces[captured_piece.get_type()][captured_piece.id]

            if move.special_move in (ENPASSANT_LEFT, ENPASSANT_RIGHT):
                board[captured_piece.row][captured_piece.col] = None

        # update piece location
        piece.set_loc(to_loc)

        # update board
        board[from_loc[0]][from_loc[1]] = None
        board[to_loc[0]][to_loc[1]] = piece

        if move.special_move is not None and move.special_move.startswith('promote'):
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
            board[to_loc[0]][to_loc[1]] = new_piece

        elif move.special_move == SHORT_CASTLE:
            player.pieces[ROOKS][1].set_loc((to_loc[0], to_loc[1] - 1))

            board[to_loc[0]][to_loc[1] + 1] = None
            board[to_loc[0]][to_loc[1] - 1] = player.pieces[ROOKS][1]

        elif move.special_move == LONG_CASTLE:
            player.pieces[ROOKS][0].set_loc((to_loc[0], to_loc[1] + 1))

            board[to_loc[0]][to_loc[1] - 2] = None
            board[to_loc[0]][to_loc[1] + 1] = player.pieces[ROOKS][0]

        if captured_piece is not None and captured_piece.get_type() == ROOKS:
            if captured_piece.id == 0:
                opponent.pieces[KING].long_castle_rights = False
            elif captured_piece.id == 1:
                opponent.pieces[KING].short_castle_rights = False

        # update move history
        move.move_num = len(move_history)
        move_history.append(move)

        # update material
        is_capture = captured_piece is not None
        if is_capture and captured_piece.get_type() != KING:
            material[player.colour][captured_piece.get_type()] += 1
        if promotion_piece is not None:
            material[player.colour][new_piece.get_type()] += 1
            material[opponent.colour][PAWNS] += 1

        # TODO: get_basic_move_name is already called in calculate_moves_for_both_players when debug is on
        move_name = move.get_basic_move_name(player.pieces)

        # update legal moves
        player_in_check, opponent_in_check = Logic.calculate_moves_for_both_players(
            player, opponent, board, move_history, material, check_checks
        )

        game_status = {
            'game_finished': False,
            f'{player.colour}_in_check': player_in_check,
            f'{opponent.colour}_in_check': opponent_in_check,
            'last_move_was_capture': is_capture,
        }

        move_name_suffix = '+' if opponent_in_check else ''
        # check for checkmate
        if opponent_in_check and opponent.num_legal_moves == 0:
            game_status['game_finished'] = True
            game_status['game_result'] = 'checkmate'
            game_status['winner'] = player.colour
            game_status['game_result_message'] = f'{player.colour} won by checkmate'
            move_name_suffix = '#'

        move.move_name = move_name + move_name_suffix

        # check for draw
        is_draw, draw_by = Logic.is_draw(board, player, opponent, move_history, opponent_in_check)
        if is_draw:
            game_status['game_finished'] = True
            game_status['game_result'] = 'draw'
            game_status['draw_by'] = draw_by
            game_status['game_result_message'] = f'game drawn by {draw_by}'

        return game_status

    # checks 3-fold repetition, 50 move rule, insufficient mating material
    # should not be called before a move is made
    @staticmethod
    def is_draw(board, player, opponent, move_history, opponent_in_check):
        if not opponent_in_check and opponent.num_legal_moves == 0:
            return (True, 'stalemate')

        insuff_material = Logic.insufficient_mating_material([player, opponent])
        if insuff_material:
            return (True, 'insufficient material')

        boards = {get_board_string(board): 1}

        iterations = 0
        for i in range(len(move_history) - 1, max(-1, len(move_history) - 100), -1):
            if move_history[i].board_str_before_move in boards:
                boards[move_history[i].board_str_before_move] += 1
                if boards[move_history[i].board_str_before_move] >= 3:
                    return (True, '3-fold repetition')
            else:
                boards[move_history[i].board_str_before_move] = 1

            assert move_history[i].is_capture is not None
            if move_history[i].piece_type == PAWNS or move_history[i].is_capture:
                return (False, None)
            iterations += 1

        return (True, '50-move rule') if iterations >= 50 else (False, None)

    # using lichess / FIDE rules, i.e. it's only a draw if there's absolutely no mate possible
    # (it's not a draw if there is a possible mate even if there is no forced mate)
    @staticmethod
    def insufficient_mating_material(players):
        for i, player in enumerate(players):
            if (
                len(player.pieces[PAWNS]) > 0
                or len(player.pieces[KNIGHTS]) >= 2
                or len(player.pieces[ROOKS]) > 0
                or len(player.pieces[QUEENS]) > 0
            ):
                return False
            if (
                len(player.pieces[KNIGHTS]) >= 1
                and len(player.pieces[BISHOPS]) >= 1
            ):
                return False
            if len(player.pieces[KNIGHTS]) >= 1 and (
                len(players[1-i].pieces[KNIGHTS]) >= 1
                or len(players[1-i].pieces[BISHOPS]) >= 1
            ):
                return False
            if len(player.pieces[BISHOPS]) >= 2 and (
                any(
                    colour_of_square(bishop.loc) != colour_of_square(player.pieces[BISHOPS][0].loc)
                    for bishop in player.pieces[BISHOPS]
                )
            ):
                return False
            if (
                len(player.pieces[BISHOPS]) >= 1
                and len(players[1-i].pieces[BISHOPS]) >= 1
                and any(
                    colour_of_square(bishop.loc) != colour_of_square(player.pieces[BISHOPS][0].loc)
                    for bishop in (player.pieces[BISHOPS] + players[1-i].pieces[BISHOPS])
                )
            ):
                return False

        return True

    @staticmethod
    def get_board_from_pieces(player_pieces, opponent_pieces):
        board = [[None for _ in range(8)] for _ in range(8)]

        def set_piece_on_board(piece):
            board[piece.row][piece.col] = piece

        for pieces in (player_pieces, opponent_pieces):
            for piece_type in (KNIGHTS, BISHOPS, ROOKS, QUEENS, PAWNS):
                for piece in pieces[piece_type].values():
                    set_piece_on_board(piece)
            set_piece_on_board(pieces[KING])

        return board

    @staticmethod
    def in_check_after_move(board, move_history, material, player, opponent, move) -> bool:
        from_loc = move.from_loc
        to_loc = move.to_loc

        temp_player = deepcopy(player)
        temp_opponent = deepcopy(opponent)
        temp_board = Logic.get_board_from_pieces(temp_player.pieces, temp_opponent.pieces)

        Logic.make_move(
            temp_board,
            temp_player,
            temp_opponent,
            move_history,
            deepcopy(material),
            Move(from_loc, to_loc, temp_board, move.special_move),
            False
        )

        in_check = Logic.in_check(temp_board, temp_player, temp_opponent)

        move_history.pop()

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
            def check_for_enpassent(piece, loc, player, board):
                if (
                    piece.get_type() == PAWNS
                    and loc[0] == piece.loc[0] + 1 * player.direction
                    and loc[1] == piece.loc[1] - 1
                ):
                    return Move(piece.loc, loc, board, ENPASSANT_LEFT)
                elif (
                    piece.get_type() == PAWNS
                    and loc[0] == piece.loc[0] + 1 * player.direction
                    and loc[1] == piece.loc[1] + 1
                ):
                    return Move(piece.loc, loc, board, ENPASSANT_RIGHT)
                return None

            dist = 1
            found_piece = False
            empty_squares_between_king_and_piece = []
            while in_bounds((loc := (king_row + y_dir * dist, king_col + x_dir * dist))):
                board_loc = board[loc[0]][loc[1]]

                if not found_piece and board_loc is not None and board_loc.colour != player.colour:
                    return

                elif found_piece and board_loc is not None and board_loc.colour == player.colour:
                    return

                elif not found_piece and board_loc is None:
                    empty_squares_between_king_and_piece.append((loc[0], loc[1]))
                elif (
                    not found_piece
                    and board_loc is not None
                    and board_loc.colour == player.colour
                ):
                    found_piece = True
                    piece = board_loc
                    valid_moves = []
                    for empty_loc in empty_squares_between_king_and_piece:
                        valid_moves.append(Move(piece.loc, empty_loc, board))
                        enpassent = check_for_enpassent(piece, empty_loc, player, board)
                        if enpassent:
                            valid_moves.append(enpassent)
                    valid_moves = [
                        Move(piece.loc, empty_loc, board) for empty_loc in empty_squares_between_king_and_piece
                    ]

                elif found_piece and board_loc is None:
                    valid_moves.append(Move(piece.loc, loc, board))
                    enpassent = check_for_enpassent(piece, loc, player, board)
                    if enpassent:
                        valid_moves.append(enpassent)

                elif found_piece and board_loc is not None and board_loc.colour != player.colour:
                    piece_type = board_loc.get_type()
                    if (
                        piece_type == QUEENS
                        or ((x_dir == 0 or y_dir == 0) and piece_type == ROOKS)
                        or (x_dir != 0 and y_dir != 0 and piece_type == BISHOPS)
                    ):
                        valid_moves.append(Move(piece.loc, loc, board))
                        piece.legal_moves = list(filter(
                            lambda move: move in valid_moves,
                            piece.legal_moves
                        ))
                    else:
                        return
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
                and board_at_loc.get_type() == PAWNS
            ):
                return True

        return False
