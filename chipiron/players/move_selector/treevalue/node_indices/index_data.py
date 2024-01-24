from chipiron.players.move_selector.treevalue.nodes.tree_node import TreeNode

from dataclasses import dataclass


@dataclass(slots=True)
class NodeExplorationData:
    tree_node: TreeNode
    index: float | None = None

    def dot_description(self):
        return f'index:{self.index}'


@dataclass(slots=True)
class RecurZipfQuoolExplorationData(NodeExplorationData):
    # the 'proba' associated by recursively multiplying 1/rank of the node with the max zipf_factor of the parents
    zipf_factored_proba: float | None = None

    def dot_description(self):
        return f'index:{self.index} zipf_factored_proba:{self.zipf_factored_proba}'
