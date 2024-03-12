from .algorithm_node_tree_manager import AlgorithmNodeTreeManager
from .tree_manager import TreeManager
from chipiron.players.move_selector.treevalue import node_factory
import chipiron.players.move_selector.treevalue.updates as upda
from chipiron.players.move_selector.treevalue.node_evaluator import NodeEvaluator, EvaluationQueries
from chipiron.players.move_selector.treevalue.indices.index_manager import NodeExplorationIndexManager, \
    create_exploration_index_manager

from chipiron.players.move_selector.treevalue.indices.node_indices.index_types import IndexComputationType
from chipiron.players.move_selector.treevalue.updates.index_updater import IndexUpdater
import chipiron.players.move_selector.treevalue.nodes as nodes


def create_algorithm_node_tree_manager(
        node_evaluator: NodeEvaluator | None,
        algorithm_node_factory: node_factory.AlgorithmNodeFactory,
        index_computation: IndexComputationType | None,
        index_updater: IndexUpdater | None
) -> AlgorithmNodeTreeManager:
    tree_manager: TreeManager[nodes.AlgorithmNode] = TreeManager(
        node_factory=algorithm_node_factory
    )

    algorithm_node_updater: upda.AlgorithmNodeUpdater = upda.create_algorithm_node_updater(
        index_updater=index_updater
    )

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
