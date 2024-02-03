from bidict import bidict
import chess
import chipiron.environments.chess.board as boards
from .itree_node import ITreeNode
from dataclasses import dataclass, field


@dataclass(slots=True)
class TreeNode:
    # id is a number to identify this node for easier debug
    id: int

    # number of half-moves since the start of the game to get to the board position in self.board
    half_move_: int

    # the node represents a board position. we also store the fast representation of the board.
    board_: boards.BoardChi

    # the set of parent nodes to this node. Note that a node can have multiple parents!
    parent_nodes: set[ITreeNode]

    # all_legal_moves_generated  is a boolean saying whether all moves have been generated.
    # If true the moves are either opened in which case the corresponding opened node is stored in
    # the dictionary self.moves_children, otherwise it is stored in self.non_opened_legal_moves
    all_legal_moves_generated: bool = False
    non_opened_legal_moves: set = field(default_factory=set)

    # bijection dictionary between moves and children nodes. node is set to None is not created
    moves_children_: bidict[chess.Move, ITreeNode] = field(default_factory=bidict)

    fast_rep: str = field(default_factory=str)

    # the color of the player that has to move in the board
    player_to_move_: chess.Color = field(default_factory=chess.Color)

    def __post_init__(self):
        if self.board_:
            self.fast_rep = self.board_.fast_representation()
            self.player_to_move_: chess.Color = self.board_.turn

    @property
    def player_to_move(self):
        return self.player_to_move_

    @property
    def board(self) -> boards.BoardChi:
        return self.board_

    @property
    def half_move(self) -> int:
        return self.half_move_

    @property
    def moves_children(self) -> bidict:
        return self.moves_children_

    def is_root_node(self) -> bool:
        return not self.parent_nodes

    def add_parent(self, new_parent_node):
        assert (new_parent_node not in self.parent_nodes)  # there cannot be two ways to link the same child-parent
        self.parent_nodes.add(new_parent_node)

    def print_moves_children(self):
        print('here are the ', len(self.moves_children_), ' moves-children link of node', self.id, ': ', end=' ')
        for move, child in self.moves_children_.items():
            if child is None:
                print(move, child, end=' ')
            else:
                print(move, child.id, end=' ')
        print(' ')


    def test(self):
        # print('testing node', selbestf.id)
        self.test_all_legal_moves_generated()

    def dot_description(self):
        return 'id:' + str(self.id) + ' dep: ' + str(self.half_move) + '\nfen:' + str(self.board)

    def test_all_legal_moves_generated(self):
        # print('test_all_legal_moves_generated')
        if self.all_legal_moves_generated:
            for move in self.board.get_legal_moves():
                assert (bool(move in self.moves_children_) != bool(move in self.non_opened_legal_moves))
        else:
            move_not_in = []
            legal_moves = list(self.board.get_legal_moves())
            for move in legal_moves:
                if move not in self.moves_children_:
                    move_not_in.append(move)
            if move_not_in == []:
                pass
                # print('test', move_not_in, list(self.board.get_legal_moves()), self.moves_children)
                # print(self.board)
            assert (move_not_in != [] or legal_moves == [])

    def get_descendants(self):
        des = {self: None}  # include itself
        generation = set(self.moves_children_.values())
        while generation:
            next_depth_generation = set()
            for node in generation:

                des[node] = None
                for move, next_generation_child in node.moves_children.items():
                    next_depth_generation.add(next_generation_child)
            generation = next_depth_generation
        return des

    def get_descendants_candidate_to_open(self):
        """ returns descendants that are both not opened and not over"""
        if not self.all_legal_moves_generated and not self.is_over():
            # should use are_all_moves_and_children_opened() but its messy!
            # also using is_over is  messy as over_events are defined in a child class!!!
            des = {self: None}  # include itself maybe
        else:
            des = {}
        generation = set(self.moves_children_.values())
        while generation:
            next_depth_generation = set()
            for node in generation:
                if not node.all_legal_moves_generated and not node.is_over():
                    des[node] = None
                for move, next_generation_child in node.moves_children.items():
                    next_depth_generation.add(next_generation_child)
            generation = next_depth_generation
        return des
