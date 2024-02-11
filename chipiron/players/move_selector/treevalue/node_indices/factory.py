import chipiron.players.move_selector.treevalue.nodes as nodes
from .index_data import NodeExplorationData, RecurZipfQuoolExplorationData, MinMaxPathValue, IntervalExplo, \
    MaxDepthDescendants
from .index_types import IndexComputationType
from .node_exploration_manager import UpdateIndexZipfFactoredProba, UpdateIndexGlobalMinChange, \
    UpdateIndexLocalMinChange, NodeExplorationIndexManager, NullNodeExplorationIndexManager
from typing import Callable
from dataclasses import make_dataclass


def create_exploration_index_manager(
        index_computation: IndexComputationType | None = None
) -> NodeExplorationIndexManager:
    if index_computation is None:
        node_exploration_manager: NodeExplorationIndexManager = NullNodeExplorationIndexManager()
    else:

        node_exploration_manager: NodeExplorationIndexManager
        match index_computation:
            case IndexComputationType.MinGlobalChange:
                node_exploration_manager = UpdateIndexGlobalMinChange()
            case IndexComputationType.RecurZipf:
                node_exploration_manager = UpdateIndexZipfFactoredProba()
            case IndexComputationType.MinLocalChange:
                node_exploration_manager = UpdateIndexLocalMinChange()
            case other:
                raise ValueError(f'player creator: can not find {other} in {__name__}')

    return node_exploration_manager


ExplorationIndexDataFactory = Callable[[nodes.TreeNode], NodeExplorationData | None]


def create_exploration_index_data(
        tree_node: nodes.TreeNode,
        index_computation: IndexComputationType | None = None,
        depth_index: bool = False
) -> NodeExplorationData | None:
    exploration_index_data: NodeExplorationData | None
    match index_computation:
        case None:
            base_index_dataclass_name = None
        case IndexComputationType.MinLocalChange:
            base_index_dataclass_name = IntervalExplo
            # exploration_index_data: IntervalExplo = IntervalExplo(tree_node=tree_node)
        case IndexComputationType.MinGlobalChange:
            base_index_dataclass_name = MinMaxPathValue
            # exploration_index_data: MinMaxPathValue = MinMaxPathValue(tree_node=tree_node)
        case IndexComputationType.RecurZipf:
            base_index_dataclass_name = RecurZipfQuoolExplorationData
            # exploration_index_data = RecurZipfQuoolExplorationData(tree_node=tree_node)
        case other:
            raise ValueError(f'not finding good case for {other} in file {__name__}')

    if depth_index:
        # adding a field to the dataclass for keeping track of the depth
        index_dataclass_name = make_dataclass('DepthExtendedDataclass',
                                              fields=[],
                                              bases=(base_index_dataclass_name, MaxDepthDescendants))
    else:
        index_dataclass_name = base_index_dataclass_name

    if index_dataclass_name is not None:
        exploration_index_data = index_dataclass_name(tree_node=tree_node)
    else:
        exploration_index_data = None

    return exploration_index_data
