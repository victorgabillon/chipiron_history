from dataclasses import dataclass

import chipiron.players.boardevaluators.neural_networks as board_nn
from chipiron.players.move_selector.treevalue.node_evaluator import NodeEvaluatorArgs
from chipiron.players.move_selector.treevalue.node_evaluator.all_node_evaluators import NodeEvaluatorTypes


@dataclass
class NeuralNetNodeEvalArgs(NodeEvaluatorArgs):
    neural_network: board_nn.NeuralNetBoardEvalArgs

    def __post_init__(self):
        if self.type != NodeEvaluatorTypes.NeuralNetwork:
            raise ValueError('Expecting neural_network as name')
