DISCOUNT =.999999

# TODO check what is this discount abount, probably remove it no?


class NodeEvaluator:
    """
    This class evaluates a node, see if this is need. Reformating the code atm to have board
     evaluator independent from the node business
    """

    def __init__(self):
        pass

    def compute_representation(self, node, parent_node, board_modifications):
        pass

    def evaluate_all_not_over(self, not_over_nodes):
        for node_not_over in not_over_nodes:
            evaluation = self.value_white(node_not_over)
            processed_evaluation = self.process_evalution_not_over(evaluation, node_not_over)
            node_not_over.minmax_evaluation.set_evaluation(processed_evaluation)

    def process_evalution_not_over(self, evaluation, node):
        processed_evaluation = (1 / DISCOUNT) ** node.half_move * evaluation
        return processed_evaluation
