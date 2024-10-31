from abc import abstractmethod
from dataclasses import asdict
from typing import Protocol, Self
from typing import TypeVar, Any

import chess
import yaml

from chipiron.environments.chess.board.board_modification import BoardModification
from chipiron.environments.chess.move import moveUci, IMove
from .utils import FenPlusMoveHistory
from .utils import fen

board_key = tuple[int, int, int, int, int, int, bool, int, int | None, int, int, int, int, int]
board_key_without_counters = tuple[int, int, int, int, int, int, bool, int, int | None, int, int, int]

T_Move = TypeVar('T_Move', bound=IMove)


class IBoard(Protocol[T_Move]):
    fast_representation_: board_key

    @abstractmethod
    def play_move(
            self,
            move: T_Move
    ) -> BoardModification | None:
        ...

    @property
    @abstractmethod
    def fen(self) -> str:
        ...

    @property
    @abstractmethod
    def move_history_stack(
            self,
    ) -> list[moveUci]:
        ...

    @abstractmethod
    def ply(self) -> int:
        """
        Returns the number of half-moves (plies) that have been played on the board.

        :return: The number of half-moves played on the board.
        :rtype: int
        """
        ...

    @property
    @abstractmethod
    def turn(self) -> chess.Color:
        """
        Get the current turn color.

        Returns:
            chess.Color: The color of the current turn.
        """
        ...

    @abstractmethod
    def copy(
            self,
            stack: bool
    ) -> Self:
        """
        Create a copy of the current board.

        Args:
            stack (bool): Whether to copy the move stack as well.

        Returns:
            BoardChi: A new instance of the BoardChi class with the copied board.
        """
        ...

    @abstractmethod
    def is_game_over(self) -> bool:
        """
        Check if the game is over.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        ...

    @property
    @abstractmethod
    def pawns(self) -> chess.Bitboard:
        ...

    @property
    @abstractmethod
    def knights(self) -> chess.Bitboard:
        ...

    @property
    @abstractmethod
    def bishops(self) -> chess.Bitboard:
        ...

    @property
    @abstractmethod
    def rooks(self) -> chess.Bitboard:
        ...

    @property
    @abstractmethod
    def queens(self) -> chess.Bitboard:
        ...

    @property
    @abstractmethod
    def kings(self) -> chess.Bitboard:
        ...

    @property
    @abstractmethod
    def white(self) -> chess.Bitboard:
        ...

    @property
    @abstractmethod
    def black(self) -> chess.Bitboard:
        ...

    @property
    @abstractmethod
    def halfmove_clock(self) -> int:
        ...

    @property
    @abstractmethod
    def promoted(self) -> chess.Bitboard:
        ...

    @property
    @abstractmethod
    def fullmove_number(self) -> int:
        ...

    @property
    @abstractmethod
    def castling_rights(self) -> chess.Bitboard:
        ...

    @property
    @abstractmethod
    def occupied(self) -> chess.Bitboard:
        ...

    @abstractmethod
    def occupied_color(self, color: chess.Color) -> chess.Bitboard:
        ...

    @abstractmethod
    def result(
            self,
            claim_draw: bool = False
    ) -> str:
        ...

    @abstractmethod
    def termination(self) -> chess.Termination | None:
        ...

    def dump(self, file: Any) -> None:
        # create minimal info for reconstruction that is the class FenPlusMoveHistory

        current_fen: fen = self.fen
        fen_plus_moves: FenPlusMoveHistory = FenPlusMoveHistory(
            current_fen=current_fen,
            historical_moves=self.move_history_stack
        )

        yaml.dump(asdict(fen_plus_moves), file, default_flow_style=False)

    @property
    @abstractmethod
    def ep_square(self) -> int | None:
        ...

    def compute_key(self) -> board_key:
        """
        Computes and returns a unique key representing the current state of the chess board.

        The key is computed by concatenating various attributes of the board, including the positions of pawns, knights,
        bishops, rooks, queens, and kings, as well as the current turn, castling rights, en passant square, halfmove clock,
        occupied squares for each color, promoted pieces, and the fullmove number.
        It is faster than calling the fen.
        Returns:
            str: A unique key representing the current state of the chess board.
        """
        string = (self.pawns, self.knights, self.bishops, self.rooks, self.queens, self.kings,
                  self.turn, self.castling_rights, self.ep_square,
                  self.white, self.black, self.promoted, self.fullmove_number, self.halfmove_clock)
        return string

    @property
    def fast_representation(self) -> board_key:
        """
        Returns a fast representation of the board.

        This method computes and returns a string representation of the board
        that can be quickly generated and used for various purposes.

        :return: A string representation of the board.
        :rtype: str
        """
        return self.fast_representation_

    @property
    def fast_representation_without_counters(self) -> board_key_without_counters:
        """
        Returns a fast representation of the board.

        This method computes and returns a string representation of the board
        that can be quickly generated and used for various purposes.

        :return: A string representation of the board.
        :rtype: str
        """
        assert self.fast_representation_ is not None
        return self.fast_representation_[:-2]

    @abstractmethod
    def is_zeroing(
            self,
            move: T_Move
    ) -> bool:
        ...

    @abstractmethod
    def is_attacked(
            self,
            a_color: chess.Color
    ) -> bool:
        ...

    @property
    @abstractmethod
    def legal_moves(self) -> set[T_Move]:
        ...

    def number_of_pieces_on_the_board(self) -> int:
        ...

    def piece_map(
            self
    ) -> dict[chess.Square, tuple[int, bool]]:
        ...

    def has_kingside_castling_rights(
            self,
            color: chess.Color
    ) -> bool:
        ...

    def has_queenside_castling_rights(
            self,
            color: chess.Color
    ) -> bool:
        ...

    def print_chess_board(self) -> None:
        ...

    def tell_result(self) -> None:
        ...