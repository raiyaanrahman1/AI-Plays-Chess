from .utilities import get_board_string
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .types import (
        BoardType,
        MoveHisType,
        MaterialType,
        PlayerType,
        MoveType,
        TreeNodeType,
        GameStateType,
        GameStatusType
    )

import math
import random
import heapq
from .game_logic import Logic
from .copy_game_objects import CopyGameObjects
from .constants import PIECE_TYPES
from .move import Move
PAWNS, KNIGHTS, BISHOPS, ROOKS, QUEENS, KINGS = PIECE_TYPES


class GameState:
    def __init__(
        self,
        board: 'BoardType',
        move_history: 'MoveHisType',
        material: 'MaterialType',
        player: 'PlayerType',
        opponent: 'PlayerType',
        game_status: 'GameStatusType'
    ) -> None:
        self.board = board
        self.move_history = move_history
        self.material = material
        self.player = player
        self.opponent = opponent
        self.game_status = game_status
        self.move_history_str = str(move_history)
        


class TreeNode:
    def __init__(
        self: 'TreeNodeType',
        game_state_after_move: 'GameStateType'
    ) -> None:
        move_history = game_state_after_move.move_history
        self.move_before_current_state = move_history[-1] if len(move_history) > 0 else None
        self.game_state_after_move = game_state_after_move
        self.children: 'Dict[str, TreeNodeType]' = {}
        self.best_move: 'None | MoveType ' = None
        self.best_move_node: 'None | TreeNodeType' = None
        self.eval: 'None | float' = None


# for beam_search
class HeapNode:
    def __init__(self, tree_node: TreeNode, eval: float) -> None:
        self.node = tree_node
        self.eval = eval

    def __lt__(self, other):
        return self.eval < other.eval

class ChessAI:
    @staticmethod
    def get_child_game_state(
        move_to_make: 'MoveType',
        player: 'PlayerType',
        opponent: 'PlayerType',
        material: 'MaterialType',
        move_history: 'MoveHisType'
    ):
        move = move_to_make
        from_loc = move.from_loc
        to_loc = move.to_loc

        temp_player = CopyGameObjects.copy_player(player)
        temp_opponent = CopyGameObjects.copy_player(opponent)
        temp_board = Logic.get_board_from_pieces(temp_player.pieces, temp_opponent.pieces)
        temp_board_str = get_board_string(temp_board)
        temp_material = CopyGameObjects.copy_material(material)
        temp_move_history = CopyGameObjects.copy_move_history(move_history)

        game_status = Logic.make_move(
            temp_board,
            temp_player,
            temp_opponent,
            temp_move_history,
            temp_material,
            Move(from_loc, to_loc, temp_board, temp_board_str, move.special_move),
            temp_board_str
        )
        child_game_state = GameState(
            temp_board,
            temp_move_history,
            temp_material,
            temp_opponent,
            temp_player,
            game_status
        )
        return child_game_state
    
    @staticmethod
    def add_child_nodes(currentTree: 'TreeNodeType'):
        player, opponent, material, move_history = (
            currentTree.game_state_after_move.player,
            currentTree.game_state_after_move.opponent,
            currentTree.game_state_after_move.material,
            currentTree.game_state_after_move.move_history
        )
        child_tree_nodes: 'List[TreeNode]' = []
        for piece_type in player.pieces:
            for piece in player.pieces[piece_type]:
                for move in piece.legal_moves:
                    child_game_state = ChessAI.get_child_game_state(
                        move,
                        player,
                        opponent,
                        material,
                        move_history
                    )
                    child_tree_node = TreeNode(child_game_state)
                    child_tree_node.eval = ChessAI.evaluate_position(child_game_state)
                    child_tree_nodes.append(child_tree_node)
        child_tree_nodes.sort(key=lambda state: state.eval, reverse=player.colour == 'white')
        currentTree.children = {child_node.move_before_current_state.id: child_node for child_node in child_tree_nodes}

    @staticmethod
    def evaluate_position(game_state: 'GameStateType') -> float:
        player, opponent, material, game_status = (
            game_state.player,
            game_state.opponent,
            game_state.material,
            game_state.game_status
        )

        if game_status.winner is not None:
            return (-1) ** (game_status.winner == 'black') * math.inf

        if game_status.game_result == 'draw':
            return 0

        num_legal_moves = [player.num_legal_moves, opponent.num_legal_moves]
        mat = [0, 0]
        for i, p in enumerate((player, opponent)):
            mat[i] += (
                material[p.colour][PAWNS]
                + material[p.colour][KNIGHTS] * 3
                + material[p.colour][BISHOPS] * 3
                + material[p.colour][ROOKS] * 5
                + material[p.colour][QUEENS] * 9
            )

        white_player = 1 - int(player.colour == 'white')
        black_player = 1 - white_player
        return mat[white_player] - mat[black_player] + (num_legal_moves[white_player] - num_legal_moves[black_player]) / 50

    @staticmethod
    def calculate_deep_moves(
        currentTree: 'TreeNode',
        depth: int,
        alpha: float = -math.inf,
        beta: float = math.inf,
    ):
        player = currentTree.game_state_after_move.player

        if depth == 0:
            currentTree.eval = ChessAI.evaluate_position(currentTree.game_state_after_move)
            return currentTree

        curr_eval = (-1) ** (player.colour == 'white') * math.inf

        if len(currentTree.children) == 0:
            ChessAI.add_child_nodes(currentTree)

        max_or_min = max if player.colour == 'white' else min

        for child_node in currentTree.children.values():
            move = child_node.move_before_current_state
            if depth > 0 and beta > alpha:
                child_node = ChessAI.calculate_deep_moves(
                    child_node,
                    depth - 1,
                    alpha,
                    beta
                )
                eval = child_node.eval

                curr_eval = max_or_min(curr_eval, eval)
                if curr_eval == eval:
                    currentTree.best_move = move
                    currentTree.best_move_node = child_node

                alpha_or_beta = alpha if player.colour == 'white' else beta
                alpha_or_beta = max_or_min(alpha_or_beta, curr_eval)

        currentTree.eval = curr_eval
        return currentTree
    
    @staticmethod
    def select_children_for_beam(
        player: 'PlayerType',
        parent_nodes: 'List[TreeNode]',
        k: int
    ) -> 'List[TreeNode]':
        heap: List[HeapNode] = []

        if len(parent_nodes) == 1:
            return list(parent_nodes[0].children.values())

        # select k best children
        for parent in parent_nodes:
            # best_child = max(parent.children.values(), key = lambda child: child.eval * player.direction)
            for child in parent.children.values():
                if len(heap) < k:
                    heapq.heappush(heap, HeapNode(child, child.eval))

                elif child.eval * player.direction > min(heap).eval:
                    heapq.heapreplace(heap, HeapNode(child, child.eval))

        selected_children = [heap_node.node for heap_node in heap]
        children_lst = [child for parent in parent_nodes for child in parent.children.values() if child not in selected_children]

        # select k other random children
        for _ in range(k):
            if len(children_lst) == 0:
                break
            node = random.choice(children_lst)
            selected_children.append(node)
            children_lst.remove(node)

        return selected_children

    @staticmethod
    def recompute_evals(
        currentTree: 'TreeNode'
    ):
        if len(currentTree.children) == 0:
            return
        
        for child in currentTree.children.values():
            ChessAI.recompute_evals(child)

        player = currentTree.game_state_after_move.player
        currentTree.best_move_node = max(currentTree.children.values(), key = lambda node: node.eval * player.direction)
        currentTree.best_move = currentTree.best_move_node.move_before_current_state
        currentTree.eval = currentTree.best_move_node.eval
        return
        
    @staticmethod
    def update_tree_for_beam_search(
        currentTree: 'TreeNode',
        selected_leaves: 'List[TreeNode]'
    ):
        leaf_depth = len(selected_leaves[0].game_state_after_move.move_history)
        tree_depth = len(currentTree.game_state_after_move.move_history)

        if leaf_depth - tree_depth > 1:
            for child in currentTree.children.values():
                ChessAI.update_tree_for_beam_search(
                    child,
                    selected_leaves
                )
        
        move_ids = list(currentTree.children.keys())
        for move_id in move_ids:
            child = currentTree.children[move_id]
            child_move_his = child.game_state_after_move.move_history
            
            found_leaf = False
            for leaf in selected_leaves:
                if child_move_his == leaf.game_state_after_move.move_history[:tree_depth + 1]:
                    found_leaf = True
                    break

            if not found_leaf:
                del currentTree.children[move_id]
    
    @staticmethod
    def beam_search(
        currentTree: 'TreeNode',
        minimax_depth: int,
        k: int,
        beam_depth: int
    ):
        currentTree = ChessAI.calculate_deep_moves(currentTree, minimax_depth)
        player, opponent = currentTree.game_state_after_move.player, currentTree.game_state_after_move.opponent
        current_player, current_opponent = player, opponent
        nodes_at_depth: 'List[TreeNode]' = ChessAI.select_children_for_beam(player, [currentTree], k)

        while len(nodes_at_depth[0].children) > 0:
            nodes_at_depth = [child.best_move_node for child in nodes_at_depth]

        for i in range(beam_depth):
            for node in nodes_at_depth:
                ChessAI.add_child_nodes(node)

            nodes_at_depth = ChessAI.select_children_for_beam(current_player, nodes_at_depth, k)

            current_player, current_opponent = current_opponent, current_player
            # k += k
        
        # ChessAI.update_tree_for_beam_search(currentTree, nodes_at_depth)
        ChessAI.recompute_evals(currentTree)
    
    # @staticmethod
    # def beam_search_helper(
    #     currentTree: 'TreeNode',
    #     minimax_depth: int,
    #     k: int,
    #     beam_depth: int
    # ) -> 'TreeNode':
    #     player = currentTree.game_state_after_move.player
    #     game_status = currentTree.game_state_after_move.game_status

    #     if beam_depth == 0 or game_status.game_finished:
    #         currentTree.eval = ChessAI.evaluate_position(currentTree.game_state_after_move)
    #         return currentTree
        
    #     if len(currentTree.children) == 0:
    #         ChessAI.add_child_nodes(currentTree)

    #     children_for_beam = ChessAI.select_children_for_beam(currentTree, k)

    #     for child in children_for_beam:
    #         node_to_beam = child
    #         new_depth = beam_depth - (currentTree.best_move is None)
    #         node_to_beam = ChessAI.beam_search_helper(node_to_beam, minimax_depth, k, new_depth)

    #     best_eval = -math.inf
    #     best_child = None
    #     for child in currentTree.children.values():
    #         assert child.eval is not None
    #         if child.eval * player.direction > best_eval:
    #             best_eval = child.eval
    #             best_child = child

    #     currentTree.eval = best_eval * player.direction
    #     currentTree.best_move_node = best_child
    #     assert best_child is not None
    #     currentTree.best_move = best_child.move_before_current_state
    #     return currentTree
    
    # @staticmethod
    # def beam_search(
    #     currentTree: 'TreeNode',
    #     minimax_depth: int,
    #     k: int,
    #     beam_depth: int
    # ):
    #     currentTree = ChessAI.calculate_deep_moves(currentTree, minimax_depth)
    #     return ChessAI.beam_search_helper(currentTree, minimax_depth, k, beam_depth)
        