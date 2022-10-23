from copy import deepcopy
from .utilities import in_bounds
from .constants import PIECE_TYPES
from .constants import KING
PAWNS, KNIGHTS, BISHOPS, ROOKS, QUEENS = PIECE_TYPES


class Logic:
    @staticmethod
    def calculate_legal_moves(player, opponent, board, move_history):
        in_check = Logic.in_check(board, player, opponent)

        def helper(piece):
            piece.calculate_moves(board, move_history)
            if in_check:
                piece.legal_moves = list(filter(
                    lambda move: not Logic.in_check_after_move(
                        board, opponent, piece.loc, move
                    ),
                    piece.legal_moves
                ))
            else:
                Logic.validate_moves(board, piece, player, opponent)

        helper(player.pieces[KING])
        for piece_type in PIECE_TYPES:
            for piece in player.pieces[piece_type]:
                helper(piece)

    @staticmethod
    def make_move(board, player, opponent, move_history, move):
        pass

    # Might want to move this method into Piece to avoid an extra loop when filtering
    # Would have to pass in player
    @staticmethod
    def in_check_after_move(board, move_history, player, opponent, from_loc, to_loc) -> bool:
        # to avoid deep-copying the board, we can make the changes on the board itself
        # and then reverse the changes
        board_from = board[from_loc[0]][from_loc[1]]
        board_to = board[to_loc[0]][to_loc[1]]
        temp_player = deepcopy(player)
        temp_opponent = deepcopy(opponent)
        copied_piece = temp_player.pieces[board_from.get_type()][board_from.id]
        if board_to is not None and board_to.colour == player.colour:
            raise TypeError('Cannot move to your own piece')
        if board_to is not None:
            temp_opponent.pieces[board_to.get_type()].pop(board_to.id)

        # TODO: move this block into a Player.make_move function
        copied_piece.row = to_loc[0]
        copied_piece.col = to_loc[1]
        board[from_loc[0]][from_loc[1]] = None
        board[to_loc[0]][to_loc[1]] = board_from
        # TODO: append move to move_history and adjust castling rights if needed
        Logic.calculate_legal_moves(temp_player, temp_opponent, board, move_history)
        Logic.calculate_legal_moves(temp_opponent, temp_player, board, move_history)

        in_check = Logic.in_check(board, player, opponent)

        # TODO: uncomment this line: move_history.pop()
        board[from_loc[0]][from_loc[1]] = board_from
        board[to_loc[0]][to_loc[1]] = board_to

        return in_check

    # filters the pieces moves such that after the move is made, the player's king is not in check
    # pre-condition: the king is not currently in check
    @staticmethod
    def validate_moves(board, piece, player, opponent):
        if piece.get_type() == KING:
            player.pieces[KING].legal_moves = list(filter(
                lambda move: not Logic.in_check_after_move(
                    board, player, opponent, piece.loc, move
                ),
                player.pieces[KING].legal_moves
            ))

            # TODO: implement special case for castling
            return

        king_row, king_col = player.pieces[KING].loc

        def validate_in_dir(x_dir, y_dir):
            dist = 1
            found_piece = False
            while in_bounds((loc := (king_row + x_dir * dist, king_col + y_dir * dist))):
                board_loc = board[loc[0]][loc[1]]
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
            for piece in opponent.pieces[piece_type]:
                if player.pieces[KING].loc in piece.legal_moves:
                    return True

        # the other King can't actually put the player in check
        # this is simply to prevent the kings from being adjacent
        if player.pieces[KING].loc in opponent.pieces[KING].legal_moves:
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
