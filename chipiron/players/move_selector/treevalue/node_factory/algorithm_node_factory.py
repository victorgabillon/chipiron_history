""""
AlgorithmNodeFactory
"""
from chipiron.players.move_selector.treevalue.nodes.node_minmax_evaluation import NodeMinmaxEvaluation
from chipiron.players.move_selector.treevalue.node_indices.factory import NodeExplorationData, \
    create_exploration_index_data
import chipiron.players.move_selector.treevalue.node_factory as node_fac
import chipiron.players.move_selector.treevalue.nodes as node
import chipiron.environments.chess.board as board_mod
from chipiron.players.boardevaluators.neural_networks.input_converters.board_representation import BoardRepresentation
from chipiron.players.boardevaluators.neural_networks.input_converters.factory import Representation364Factory
from dataclasses import dataclass
from typing import Any


@dataclass
class AlgorithmNodeFactory:
    """
    The classe creating Algorithm Nodes
    """
    tree_node_factory: node_fac.Base
    board_representation_factory: Representation364Factory | None
    index_computation: Any = None

    def create(self,
               board,
               half_move: int,
               count: int,
               parent_node: node.AlgorithmNode | None,
               board_depth: int,
               modifications: board_mod.BoardModification
               ) -> node.AlgorithmNode:
        tree_node: node.TreeNode = self.tree_node_factory.create(
            board=board,
            half_move=half_move,
            count=count,
            parent_node=parent_node,
        )
        minmax_evaluation: NodeMinmaxEvaluation = NodeMinmaxEvaluation(tree_node=tree_node)
        exploration_index_data: NodeExplorationData = create_exploration_index_data(
            tree_node=tree_node,
            index_computation=self.index_computation
        )
        board_representation: BoardRepresentation | None = None
        if self.board_representation_factory is not None:
            board_representation: BoardRepresentation = self.board_representation_factory.create_from_transition(
                tree_node=tree_node,
                parent_node=parent_node,
                modifications=modifications
            )

        return node.AlgorithmNode(
            tree_node=tree_node,
            minmax_evaluation=minmax_evaluation,
            exploration_index_data=exploration_index_data,
            board_representation=board_representation
        )
