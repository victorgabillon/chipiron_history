"""
This module defines the interface for a tree node in a chess move selector.

The `ITreeNode` protocol represents a node in a tree structure used for selecting chess moves.
It provides properties and methods for accessing information about the node, such as its ID,
the chess board state, the half move count, the child nodes, and the parent nodes.

The `ITreeNode` protocol also defines methods for adding a parent node, generating a dot description
for visualization, checking if all legal moves have been generated, accessing the legal moves,
and checking if the game is over.

Note: This is an interface and should not be instantiated directly.
"""

from __future__ import annotations  # (helping with recursive type annotation)

from typing import Protocol

import chess
from bidict import bidict

from chipiron.environments.chess.board.board import BoardChi


class ITreeNode(Protocol):
    """
    The `ITreeNode` protocol represents a node in a tree structure used for selecting chess moves.
    """

    @property
    def id(
            self
    ) -> int:
        """
        Get the ID of the node.

        Returns:
            The ID of the node.
        """

    # actually giving access to the boars gives access to a lot of sub fucntion so might
    # be no need to ask for them in the interfacec expicitly
    @property
    def board(
            self
    ) -> BoardChi:
        """
        Get the chess board state of the node.

        Returns:
            The chess board state of the node.
        """

    @property
    def half_move(self) -> int:
        """
        Get the half move count of the node.

        Returns:
            The half move count of the node.
        """

    @property
    def moves_children(
            self
    ) -> bidict[chess.Move, ITreeNode | None]:
        """
        Get the child nodes of the node.

        Returns:
            A bidirectional dictionary mapping chess moves to child nodes.
        """

    @property
    def parent_nodes(
            self
    ) -> set[ITreeNode]:
        """
        Get the parent nodes of the node.

        Returns:
            A set of parent nodes.
        """

    def add_parent(
            self,
            new_parent_node: ITreeNode
    ) -> None:
        """
        Add a parent node to the node.

        Args:
            new_parent_node: The parent node to add.
        """

    def dot_description(self) -> str:
        """
        Generate a dot description for visualization.

        Returns:
            A string containing the dot description.
        """

    @property
    def all_legal_moves_generated(self) -> bool:
        """
        Check if all legal moves have been generated.

        Returns:
            True if all legal moves have been generated, False otherwise.
        """

    @all_legal_moves_generated.setter
    def all_legal_moves_generated(self) -> None:
        """
        Set the flag indicating that all legal moves have been generated.
        """

    @property
    def legal_moves(self) -> chess.LegalMoveGenerator:
        """
        Get the legal moves of the node.

        Returns:
            A generator for iterating over the legal moves.
        """

    @property
    def fast_rep(self) -> str:
        """
        Get the fast representation of the node.

        Returns:
            The fast representation of the node as a string.
        """

    def is_over(self) -> bool:
        """
        Check if the game is over.

        Returns:
            True if the game is over, False otherwise.
        """
