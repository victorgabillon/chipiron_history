"""
This module defines the AlgorithmNode class, which is a generic node used by the tree and value algorithm.
It wraps tree nodes with values, minimax computation, and exploration tools.
"""

import chess

from chipiron.environments.chess.board.board import BoardChi
from chipiron.players.boardevaluators.neural_networks.input_converters.board_representation import BoardRepresentation
from chipiron.players.move_selector.treevalue.indices.node_indices import NodeExplorationData
from chipiron.players.move_selector.treevalue.nodes.algorithm_node.node_minmax_evaluation import NodeMinmaxEvaluation
from chipiron.players.move_selector.treevalue.nodes.itree_node import ITreeNode
from chipiron.players.move_selector.treevalue.nodes.tree_node import TreeNode


class AlgorithmNode:
    """
    The generic Node used by the tree and value algorithm.
    It wraps tree nodes with values, minimax computation and exploration tools
    """

    tree_node: TreeNode  # the reference to the tree node that is wrapped
    minmax_evaluation: NodeMinmaxEvaluation  # the object computing the value
    exploration_index_data: NodeExplorationData | None  # the object storing the information to help the algorithm decide the next nodes to explore
    board_representation: BoardRepresentation | None  # the board representation

    def __init__(
            self,
            tree_node: TreeNode,
            minmax_evaluation: NodeMinmaxEvaluation,
            exploration_index_data: NodeExplorationData | None,
            board_representation: BoardRepresentation | None
    ) -> None:
        """
        Initializes an AlgorithmNode object.

        Args:
            tree_node (TreeNode): The tree node that is wrapped.
            minmax_evaluation (NodeMinmaxEvaluation): The object computing the value.
            exploration_index_data (NodeExplorationData | None): The object storing the information to help the algorithm decide the next nodes to explore.
            board_representation (BoardRepresentation | None): The board representation.
        """
        self.tree_node = tree_node
        self.minmax_evaluation = minmax_evaluation
        self.exploration_index_data = exploration_index_data
        self.board_representation = board_representation

    @property
    def player_to_move(self) -> chess.Color:
        """
        Returns the color of the player to move.

        Returns:
            chess.Color: The color of the player to move.
        """
        return self.tree_node.player_to_move

    @property
    def id(self) -> int:
        """
        Returns the ID of the node.

        Returns:
            int: The ID of the node.
        """
        return self.tree_node.id

    @property
    def half_move(self) -> int:
        """
        Returns the half move count.

        Returns:
            int: The half move count.
        """
        return self.tree_node.half_move

    @property
    def fast_rep(self) -> str:
        """
        Returns the fast representation of the node.

        Returns:
            str: The fast representation of the node.
        """
        return self.tree_node.fast_rep

    @property
    def moves_children(self) -> dict[chess.Move, ITreeNode | None]:
        """
        Returns the bidirectional dictionary of moves and their corresponding child nodes.

        Returns:
            dict[chess.Move, ITreeNode | None]: The bidirectional dictionary of moves and their corresponding child nodes.
        """
        return self.tree_node.moves_children

    @property
    def parent_nodes(self) -> dict[ITreeNode, chess.Move]:
        """
        Returns the dictionary of parent nodes of the current tree node with associated move.

        :return: A dictionary of parent nodes of the current tree node with associated move.
        """
        return self.tree_node.parent_nodes

    @property
    def board(self) -> BoardChi:
        """
        Returns the board.

        Returns:
            BoardChi: The board.
        """
        return self.tree_node.board

    def is_over(self) -> bool:
        """
        Checks if the game is over.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return self.minmax_evaluation.is_over()

    def add_parent(
            self,
            move: chess.Move,
            new_parent_node: ITreeNode
    ) -> None:
        """
        Adds a parent node.

        Args:
            move (chess.Move): the move that led to the node from the new_parent_node
            new_parent_node (ITreeNode): The new parent node to add.
        """
        self.tree_node.add_parent(
            move=move,
            new_parent_node=new_parent_node
        )

    @property
    def legal_moves(self) -> chess.LegalMoveGenerator:
        """
        Returns the legal move generator.

        Returns:
            chess.LegalMoveGenerator: The legal move generator.
        """
        return self.tree_node.board_.legal_moves

    @property
    def all_legal_moves_generated(self) -> bool:
        """
        Returns True if all legal moves have been generated, False otherwise.

        Returns:
            bool: True if all legal moves have been generated, False otherwise.
        """
        return self.tree_node.all_legal_moves_generated

    @all_legal_moves_generated.setter
    def all_legal_moves_generated(self, value: bool) -> None:
        """
        Sets the flag indicating if all legal moves have been generated.

        Args:
            value (bool): The value to set.
        """
        self.tree_node.all_legal_moves_generated = value

    @property
    def non_opened_legal_moves(self) -> set[chess.Move]:
        """
        Returns the set of non-opened legal moves.

        Returns:
            set[chess.Move]: The set of non-opened legal moves.
        """
        return self.tree_node.non_opened_legal_moves

    def dot_description(self) -> str:
        """
        Returns the dot description of the node.

        Returns:
            str: The dot description of the node.
        """
        exploration_description: str = self.exploration_index_data.dot_description() \
            if self.exploration_index_data is not None else ''

        return f'{self.tree_node.dot_description()}\n{self.minmax_evaluation.dot_description()}\n{exploration_description}'
