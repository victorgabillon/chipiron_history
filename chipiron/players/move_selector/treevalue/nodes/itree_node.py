from __future__ import annotations  # (helping with recursive type annotation)
from typing import Protocol
from bidict import bidict
from chipiron.environments.chess.board.board import BoardChi
import chess


class ITreeNode(Protocol):

    @property
    def id(self) -> int:
        ...

    @property
    def board(self) -> BoardChi:
        ...

    @property
    def half_move(self) -> int:
        ...

    @property
    def moves_children(self) -> bidict[chess.Move, ITreeNode]:
        ...

    @property
    def parent_nodes(self) -> set[ITreeNode]:
        ...

    def add_parent(self, new_parent_node: ITreeNode):
        ...
