"""
Basic class for Creating Tree nodes
"""
from typing import TypeVar, Generic, Any

import chess

import chipiron.environments.chess.board as board_mod
import chipiron.environments.chess.board as boards
from chipiron.environments.chess.move import IMove
from chipiron.players.move_selector.treevalue.node_factory.node_factory import TreeNodeFactory
from chipiron.players.move_selector.treevalue.nodes.itree_node import ITreeNode
from chipiron.players.move_selector.treevalue.nodes.tree_node import TreeNode

T = TypeVar('T', bound=ITreeNode[Any])


class Base(Generic[T], TreeNodeFactory[T]):
    """
    Basic class for Creating Tree nodes
    """

    def create(
            self,
            board: boards.IBoard[Any],
            half_move: int,
            count: int,
            parent_node: ITreeNode[Any] | None,
            move_from_parent: IMove | None,
            modifications: board_mod.BoardModification | None
    ) -> TreeNode[T]:
        """
        Creates a new TreeNode object.

        Args:
            board (boards.BoardChi): The current board state.
            half_move (int): The half-move count.
            count (int): The ID of the new node.
            parent_node (ITreeNode | None): The parent node of the new node.
            move_from_parent (chess.Move | None): The move that leads to the new node.
            modifications (board_mod.BoardModification | None): The modifications applied to the board.

        Returns:
            TreeNode: The newly created TreeNode object.
        """

        parent_nodes: dict[ITreeNode[Any], IMove]
        if parent_node is None:
            parent_nodes = {}
        else:
            assert move_from_parent is not None
            parent_nodes = {parent_node: move_from_parent}

        tree_node: TreeNode[T] = TreeNode[T](
            board_=board,
            half_move_=half_move,
            id_=count,
            parent_nodes_=parent_nodes,
        )
        return tree_node
