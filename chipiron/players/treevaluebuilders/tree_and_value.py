from players.player import Player
from players.treevaluebuilders.trees.opening_instructions import OpeningInstructor
import random
import settings
from players.treevaluebuilders.notations_and_statics import softmax


class TreeAndValue(Player):
    # at the moment it look like i dont need this class i could go directly
    # for the tree builder no? think later bout that? maybe one is for multi round and the other is not?

    def __init__(self, arg):
        self.tree = None
        self.arg = arg
        self.tree_move_limit = arg['tree_move_limit'] if 'tree_move_limit' in arg else None
        self.opening_instructor = OpeningInstructor(arg['opening_type']) if 'opening_type' in arg else None

    def continue_exploring(self):
        if self.tree.root_node.is_over():
            return False
        bool_ = True
        if self.tree_move_limit is not None:
            bool_ = self.tree.move_count < self.tree_move_limit
        return bool_

    def print_info_during_move_computation(self):
        if self.tree.root_node.best_node_sequence:
            current_best_child = self.tree.root_node.best_node_sequence[0]
            current_best_move = self.tree.root_node.moves_children.inverse[current_best_child]
            assert (self.tree.root_node.get_value_white() == current_best_child.get_value_white())

        else:
            current_best_move = '?'
        print('========= tree move counting:', self.tree.move_count, 'out of', self.tree_move_limit,
              '|',
              "{0:.0%}".format(self.tree.move_count / self.tree_move_limit),
              '| current best move:', current_best_move, '| current white value:',
              self.tree.root_node.value_white_minmax)  # ,end='\r')
        self.tree.print_best_line()


    def recommend_move_after_exploration(self):
        # for debug we fix the choice in the next lines
        if settings.deterministic_behavior:
            print(' FIXED CHOICE FOR DEBUG')
            best_child = self.tree.root_node.get_all_of_the_best_moves(how_equal='considered_equal')[-1]
            print('We have as best: ', self.tree.root_node.moves_children.inverse[best_child])
            best_move = self.tree.root_node.moves_children.inverse[best_child]

        else:  # normal behavior
            selection_rule = self.arg['move_selection_rule']['type']
            if  selection_rule == 'softmax':
                temperature = self.arg['move_selection_rule']['temperature']
                values = [self.tree.root_node.subjective_value_of(node) for node in
                          self.tree.root_node.moves_children.values()]
                softmax_ = softmax(values, temperature)
                move_as_list = random.choices(list(self.tree.root_node.moves_children.keys()), weights=softmax_, k=1)
                best_move = move_as_list[0]
            elif selection_rule == 'almost_equal' or selection_rule == 'almost_equal_logistic':
                # find best first move allowing for random choice for almost equally valued moves.
                best_root_children = self.tree.root_node.get_all_of_the_best_moves(how_equal=selection_rule )
                print('We have as bests: ', [ self.tree.root_node.moves_children.inverse[best] for best in best_root_children])
                best_child = random.choice(best_root_children)
                best_move = self.tree.root_node.moves_children.inverse[best_child]
            else:
                raise (Exception('move_selection_rule is not valid it seems'))
        return best_move

    def tree_explore(self, board):
        self.tree = self.create_tree(board)
        self.tree.add_root_node(board)

        self.count = 0
        while self.continue_exploring():
            assert (not self.tree.root_node.is_over())
            self.print_info_during_move_computation()

            opening_instructions_batch = self.choose_node_and_move_to_open()

            self.tree.save_raw_data_to_file(self.count)
            self.count += 1
            input("Press Enter to continue...")
            opening_instructions_batch.print_info()

            while opening_instructions_batch and self.continue_exploring():
                #  opening_instructions_batch.print_info()

                if self.tree_move_limit is not None:
                    opening_instructions_subset = opening_instructions_batch.pop_items(
                        self.tree_move_limit - self.tree.move_count)
                else:
                    opening_instructions_subset = opening_instructions_batch

                self.tree.open_and_update(opening_instructions_subset)
                if settings.testing_bool:
                    self.tree.test_the_tree()

        if settings.testing_bool:
            self.tree.test_the_tree()

        if self.tree_move_limit is not None:
            assert self.tree_move_limit == self.tree.move_count or self.tree.root_node.is_over()
        self.tree.save_raw_data_to_file()
        self.tree.print_some_stats()
        for move, child in self.tree.root_node.moves_children.items():
            print(move, self.tree.root_node.moves_children[move].get_value_white(), child.over_event.get_over_tag())
        print('evaluation for white: ', self.tree.root_node.get_value_white())

    def get_move_from_player(self, board, time):
        self.tree_explore(board)
        best_move = self.recommend_move_after_exploration()
        self.tree.print_best_line()  # todo maybe almost best choosen line no?

        return best_move

    def print_info(self):
        super().print_info()
        print('type: Tree and Value')
