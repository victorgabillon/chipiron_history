from .algorithm_node_tree_manager import AlgorithmNodeTreeManager, TreeManager
from chipiron.players.move_selector.treevalue import node_factory
import chipiron.players.move_selector.treevalue.updates as upda
from chipiron.players.move_selector.treevalue.node_evaluator import NodeEvaluator, EvaluationQueries
from chipiron.players.move_selector.treevalue.node_indices.factory import NodeExplorationIndexManager, \
    create_exploration_index_manager

from chipiron.players.move_selector.treevalue.node_indices.index_types import IndexComputationType


def create_algorithm_node_tree_manager(
        node_evaluator: NodeEvaluator,
        algorithm_node_factory: node_factory.AlgorithmNodeFactory,
        index_computation: IndexComputationType
) -> AlgorithmNodeTreeManager:
    tree_manager: TreeManager = TreeManager(
        node_factory=algorithm_node_factory
    )

    algorithm_node_updater: upda.AlgorithmNodeUpdater = upda.create_algorithm_node_updater()

    evaluation_queries: EvaluationQueries = EvaluationQueries()

    exploration_index_manager: NodeExplorationIndexManager = create_exploration_index_manager(
        index_computation=index_computation
    )

    algorithm_node_tree_manager: AlgorithmNodeTreeManager = AlgorithmNodeTreeManager(
        node_evaluator=node_evaluator,
        tree_manager=tree_manager,
        algorithm_node_updater=algorithm_node_updater,
        evaluation_queries=evaluation_queries,
        index_manager=exploration_index_manager
    )

    return algorithm_node_tree_manager
