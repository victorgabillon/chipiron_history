import typing

import chess

import chipiron.environments.chess.board as board_mod
import chipiron.players.move_selector.treevalue.nodes as node
import chipiron.players.move_selector.treevalue.trees as trees
from chipiron.players.move_selector.treevalue.node_factory.node_factory import TreeNodeFactory
from chipiron.players.move_selector.treevalue.node_selector.opening_instructions import OpeningInstructions
from chipiron.players.move_selector.treevalue.tree_manager.tree_expander import TreeExpansion, TreeExpansions

# todo should we use a discount? and discounted per round reward?
# todo maybe convenient to seperate this object into openner updater and dsiplayer
# todo have the reward with a discount
# DISCOUNT = 1/.99999
if typing.TYPE_CHECKING:
    import chipiron.players.move_selector.treevalue.node_selector as node_sel


class TreeManager:
    """

    This class that and manages a tree by opening new nodes and updating the values and indexes on the nodes
    """

    def __init__(
            self,
            node_factory: TreeNodeFactory
    ) -> None:
        self.node_factory = node_factory

    def open_node_move(
            self,
            tree: trees.MoveAndValueTree,
            parent_node: node.ITreeNode,
            move: chess.Move
    ) -> TreeExpansion:
        """
        Opening a Node that contains a board following a move.
        Args:
            tree:
            parent_node: The Parent node that we want to expand
            move: the move to play to expend the Node

        Returns:

        """
        # The parent board is copied, we only copy the stack (history of previous board) if the depth is smaller than 2
        # Having the stack information allows checking for draw by repetition.
        # To limit computation we limit copying it all the time. The resulting policy will only be aware of immediate
        # risk of draw by repetition
        copy_stack: bool = (tree.node_depth(parent_node) < 2)
        board: board_mod.BoardChi = parent_node.board.copy(stack=copy_stack)

        # The move is played. The board is now a new board
        modifications: board_mod.BoardModification = board.play_move(move=move)

        return self.open_node(
            tree=tree,
            parent_node=parent_node,
            board=board,
            modifications=modifications,
            move=move
        )

    def open_node(
            self,
            tree: trees.MoveAndValueTree,
            parent_node: node.ITreeNode,
            board: board_mod.BoardChi,
            modifications: board_mod.BoardModification | None,
            move: chess.Move
    ) -> TreeExpansion:
        """
        Opening a Node that contains a board given the modifications.
        Args:
            modifications:
            board:
            tree:
            parent_node: The Parent node that we want to expand
            move: the move to play to expend the Node

        Returns:

        """

        # Creation of the child node. If the board already exited in another node, that node is returned as child_node.
        half_move: int = parent_node.half_move + 1
        fast_rep: str = board.fast_representation()

        child_node: node.ITreeNode
        need_creation_child_node: bool = (tree.root_node is None
                                          or tree.descendants.is_new_generation(half_move)
                                          or fast_rep not in tree.descendants.descendants_at_half_move[half_move])
        if need_creation_child_node:
            child_node = self.node_factory.create(
                board=board,
                half_move=half_move,
                count=tree.nodes_count,
                parent_node=parent_node,
                modifications=modifications
            )
            tree.nodes_count += 1
            tree.descendants.add_descendant(child_node)  # add it to the list of descendants
        else:  # the node already exists
            child_node = tree.descendants[half_move][fast_rep]
            child_node.add_parent(parent_node)

        tree_expansion: TreeExpansion = TreeExpansion(
            child_node=child_node,
            parent_node=parent_node,
            board_modifications=modifications,
            creation_child_node=need_creation_child_node
        )

        # add it to the list of opened move and out of the non-opened moves
        parent_node.moves_children[move] = tree_expansion.child_node
        #   parent_node.tree_node.non_opened_legal_moves.remove(move)
        tree.move_count += 1  # counting moves

        return tree_expansion

    def open_instructions(
            self,
            tree: trees.MoveAndValueTree,
            opening_instructions: OpeningInstructions
    ) -> TreeExpansions:
        """

        Args:
            tree: the tree object to open
            opening_instructions: the opening instructions

        Returns: the expansions that have been performed

        """

        # place to store the tree expansion logs generated by the openings
        tree_expansions: TreeExpansions = TreeExpansions()

        opening_instruction: node_sel.OpeningInstruction
        for opening_instruction in opening_instructions.values():
            # open
            tree_expansion: TreeExpansion = self.open_node_move(
                tree=tree,
                parent_node=opening_instruction.node_to_open,
                move=opening_instruction.move_to_play
            )

            # concatenate the tree expansions
            tree_expansions.add(tree_expansion=tree_expansion)

        return tree_expansions

    def print_some_stats(
            self,
            tree: trees.MoveAndValueTree,
    ) -> None:
        print('Tree stats: move_count', tree.move_count, ' node_count',
              tree.descendants.get_count())
        sum_ = 0
        tree.descendants.print_stats()
        for half_move in tree.descendants:
            sum_ += len(tree.descendants[half_move])
            print('half_move', half_move, len(tree.descendants[half_move]), sum_)

    def test_count(
            self,
            tree: trees.MoveAndValueTree,
    ) -> None:
        assert (tree.descendants.get_count() == tree.nodes_count)

    def print_best_line(
            self,
            tree: trees.MoveAndValueTree,
    ) -> None:
        raise Exception('should not be called no? Think about modifying...')
