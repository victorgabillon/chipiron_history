from chipiron.players.treevalue.node_selector.notations_and_statics import softmax
from chipiron.players.boardevaluators.over_event import OverEvent
from chipiron.players.treevalue.stopping_criterion import StoppingCriterion, create_stopping_criterion
from chipiron.players.treevalue.node_selector.opening_instructions import OpeningInstructor

from . import tree_manager as tree_man
from . import node_selector as node_sel
from . import trees


def create_tree_exploration(
        arg,
        random_generator,
        board,
        board_evaluators_wrapper):
    opening_instructor: OpeningInstructor = OpeningInstructor(arg['opening_type'],
                                                              random_generator) if 'opening_type' in arg else None

    node_selector: node_sel.NodeSelector
    node_selector = node_sel.create(
        arg=arg,
        opening_instructor=opening_instructor,
        random_generator=random_generator)

    stopping_criterion: StoppingCriterion = create_stopping_criterion(
        arg['stopping_criterion'],
        node_selector=node_selector)

    tree_manager: tree_man.TreeManager
    tree_manager = tree_man.create_tree_manager(
        args=arg,
        board_evaluators_wrapper=board_evaluators_wrapper,
        board=board,
        expander_subscribers=[node_selector])

    tree_exploration = TreeExploration(
        tree_manager=tree_manager,
        stopping_criterion=stopping_criterion,
        node_selector=node_selector,
        random_generator=random_generator,
        args=arg)
    return tree_exploration


class TreeExploration:

    def __init__(
            self,
            tree_manager,
            stopping_criterion,
            node_selector,
            random_generator,
            args):
        self.arg = args
        self.tree_manager = tree_manager
        self.stopping_criterion = stopping_criterion
        self.node_selector = node_selector
        self.random_generator = random_generator

    def print_info_during_move_computation(self):
        if self.tree_manager.tree.root_node.best_node_sequence:
            current_best_child = self.tree_manager.tree.root_node.best_node_sequence[0]
            current_best_move = self.tree_manager.tree.root_node.moves_children.inverse[current_best_child]
            assert (self.tree_manager.tree.root_node.get_value_white() == current_best_child.get_value_white())

        else:
            current_best_move = '?'
        if self.random_generator.random() < .05:
            str_progress = self.stopping_criterion.get_string_of_progress(self.tree_manager.tree)
            print(str_progress,
                  '| current best move:', current_best_move, '| current white value:',
                  self.tree_manager.tree.root_node.value_white_minmax)  # ,end='\r')
            self.tree_manager.tree.root_node.print_children_sorted_by_value_and_exploration()
            self.tree_manager.print_best_line()

    def recommend_move_after_exploration(
            self,
            tree: trees.MoveAndValueTree):
        # todo the preference for action that have been explored more is not super clear, is it weel implemented, ven for debug?

        # for debug we fix the choice in the next lines
        # if global_variables.deterministic_behavior:
        #     print(' FIXED CHOICE FOR DEBUG')
        #     best_child = self.tree.root_node.get_all_of_the_best_moves(how_equal='considered_equal')[-1]
        #     print('We have as best: ', self.tree.root_node.moves_children.inverse[best_child])
        #     best_move = self.tree.root_node.moves_children.inverse[best_child]

        if True:  # normal behavior
            selection_rule = self.arg['move_selection_rule']['type']
            if selection_rule == 'softmax':
                temperature = self.arg['move_selection_rule']['temperature']
                values = [tree.root_node.subjective_value_of(node) for node in
                          tree.root_node.moves_children.values()]

                softmax_ = softmax(values, temperature)
                print(values)
                print('SOFTMAX', temperature, [i / sum(softmax_) for i in softmax_],
                      sum([i / sum(softmax_) for i in softmax_]))

                move_as_list = self.random_generator.choices(
                    list(tree.root_node.moves_children.keys()),
                    weights=softmax_, k=1)
                best_move = move_as_list[0]
            elif selection_rule == 'almost_equal' or selection_rule == 'almost_equal_logistic':
                # find the best first move allowing for random choice for almost equally valued moves.
                best_root_children = tree.root_node.get_all_of_the_best_moves(
                    how_equal=selection_rule)
                print('We have as bests: ',
                      [tree.root_node.moves_children.inverse[best] for best in best_root_children])
                best_child = self.random_generator.choice(best_root_children)
                if tree.root_node.over_event.how_over == OverEvent.WIN:
                    assert (best_child.over_event.how_over == OverEvent.WIN)
                best_move = tree.root_node.moves_children.inverse[best_child]
            else:
                raise (Exception('move_selection_rule is not valid it seems'))
        return best_move

    def explore(self):

        while self.stopping_criterion.should_we_continue(tree=self.tree_manager.tree):
            assert (not self.tree_manager.tree.root_node.is_over())
            self.print_info_during_move_computation()

            opening_instructions_batch: node_sel.OpeningInstructionsBatch
            opening_instructions_batch = self.node_selector.choose_node_and_move_to_open(self.tree_manager.tree)

            if self.arg['stopping_criterion']['name'] == 'tree_move_limit':
                tree_move_limit = self.arg['stopping_criterion']['tree_move_limit']
                opening_instructions_subset = opening_instructions_batch.pop_items(
                    tree_move_limit - self.tree_manager.tree.move_count)
            else:
                opening_instructions_subset = opening_instructions_batch

            self.tree_manager.open_and_update(opening_instructions_subset)

        #  self.tree.save_raw_data_to_file()
        self.tree_manager.print_some_stats()
        for move, child in self.tree_manager.tree.root_node.moves_children.items():
            print(f'{move} {self.tree_manager.tree.root_node.moves_children[move].get_value_white()}'
                  f' {child.over_event.get_over_tag()}')
        print(f'evaluation for white: {self.tree_manager.tree.root_node.get_value_white()}')

        best_move = self.recommend_move_after_exploration(self.tree_manager.tree)
        self.tree_manager.print_best_line()  # todo maybe almost best chosen line no?

        return best_move
