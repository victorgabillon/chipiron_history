from bidict import bidict

from chipiron.players.move_selector.treevalue.nodes.tree_node import TreeNode
from chipiron.players.move_selector.treevalue.nodes.itree_node import ITreeNode
from chipiron.players.move_selector.treevalue.nodes.node_minmax_evaluation import NodeMinmaxEvaluation
from chipiron.players.boardevaluators.neural_networks.input_converters.board_representation import BoardRepresentation
from chipiron.players.move_selector.treevalue.node_indices.index_data import NodeExplorationData
from chipiron.environments.chess.board.board import BoardChi


class AlgorithmNode:
    """
    The generic Node used by the tree and value algorithm.
    It wraps tree nodes with values, minimax computation and exploration tools
    """

    # the reference to the tree node that is wrapped
    tree_node: TreeNode

    # the object computing the value
    minmax_evaluation: NodeMinmaxEvaluation

    # the object storing the information to help the algorithm decide the next nodes to explore
    exploration_index_data: NodeExplorationData

    # the board representation
    board_representation: BoardRepresentation

    def __init__(
            self,
            tree_node: TreeNode,
            minmax_evaluation: NodeMinmaxEvaluation,
            exploration_index_data: NodeExplorationData,
            board_representation: BoardRepresentation
    ) -> None:
        self.tree_node = tree_node
        self.minmax_evaluation = minmax_evaluation
        self.exploration_index_data = exploration_index_data
        self.board_representation = board_representation



    @property
    def player_to_move(self):
        return self.tree_node.player_to_move

    @property
    def id(self) -> int:
        return self.tree_node.id

    @property
    def half_move(self) -> int:
        return self.tree_node.half_move

    @property
    def fast_rep(self):
        return self.tree_node.fast_rep

    @property
    def moves_children(self) -> bidict:
        return self.tree_node.moves_children

    @property
    def parent_nodes(self) -> set[ITreeNode]:
        return self.tree_node.parent_nodes

    @property
    def board(self) -> BoardChi:
        return self.tree_node.board

    def is_over(self) -> bool:
        return self.minmax_evaluation.is_over()

    def add_parent(self, new_parent_node: ITreeNode):
        self.tree_node.add_parent(new_parent_node=new_parent_node)

    @property
    def all_legal_moves_generated(self):
        return self.tree_node.all_legal_moves_generated

    @property
    def non_opened_legal_moves(self):
        return self.tree_node.non_opened_legal_moves

    def dot_description(self):
        return self.tree_node.dot_description() + '\n' + self.minmax_evaluation.dot_description() + '\n' + self.exploration_manager.dot_description()
