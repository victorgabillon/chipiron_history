from dataclasses import asdict
from typing import Protocol, Self
from typing import TypeVar, Any

import chess
import yaml

from chipiron.environments.chess.board.board_modification import BoardModification
from chipiron.environments.chess.move import moveUci, IMove
from chipiron.environments.chess.move.imove import moveKey
from .utils import FenPlusMoveHistory, FenPlusHistory
from .utils import fen

boardKey = tuple[int, int, int, int, int, int, bool, int, int | None, int, int, int, int, int]
boardKeyWithoutCounters = tuple[int, int, int, int, int, int, bool, int, int | None, int, int, int]

T_Move = TypeVar('T_Move', bound=IMove)


class LegalMoveGeneratorUciP(Protocol):
    generated_moves: list[IMove]
    all_generated_keys: list[moveKey] | None
    sort_legal_moves: bool

    def __iter__(self):
        ...

    def __next__(self) -> moveKey:
        ...

    def more_than_one_move(self) -> bool:
        ...

    def get_all(self) -> list[moveKey]:
        ...


def compute_key(
        pawns: int,
        knights: int,
        bishops: int,
        rooks: int,
        queens: int,
        kings: int,
        turn: bool,
        castling_rights: int,
        ep_square: int | None,
        white: int,
        black: int,
        promoted: int,
        fullmove_number: int,
        halfmove_clock: int
) -> boardKey:
    """
    Computes and returns a unique key representing the current state of the chess board.

    The key is computed by concatenating various attributes of the board, including the positions of pawns, knights,
    bishops, rooks, queens, and kings, as well as the current turn, castling rights, en passant square, halfmove clock,
    occupied squares for each color, promoted pieces, and the fullmove number.
    It is faster than calling the fen.
    Returns:
        str: A unique key representing the current state of the chess board.
    """
    string: boardKey = (
        pawns, knights, bishops,
        rooks, queens, kings,
        turn, castling_rights, ep_square,
        white, black, promoted,
        fullmove_number, halfmove_clock
    )
    return string


class IBoard(Protocol[T_Move]):
    fast_representation_: boardKey
    legal_moves_: LegalMoveGeneratorUciP | None = None

    def get_move_from_move_key(self, move_key: moveKey) -> IMove:
        return self.legal_moves_.generated_moves[move_key]

    def get_uci_from_move_key(self, move_key: moveKey) -> moveUci:
        return self.legal_moves_.generated_moves[move_key].uci()

    def play_move_key(
            self,
            move: moveKey
    ) -> BoardModification | None:
        ...

    def play_move_uci(
            self,
            move_uci: moveUci
    ) -> BoardModification | None:
        ...

    @property
    def fen(self) -> str:
        ...

    @property
    def move_history_stack(
            self,
    ) -> list[moveUci]:
        ...

    def ply(self) -> int:
        """
        Returns the number of half-moves (plies) that have been played on the board.

        :return: The number of half-moves played on the board.
        :rtype: int
        """
        ...

    @property
    def turn(self) -> chess.Color:
        """
        Get the current turn color.

        Returns:
            chess.Color: The color of the current turn.
        """
        ...

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

    def is_game_over(self) -> bool:
        """
        Check if the game is over.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        ...

    @property
    def pawns(self) -> chess.Bitboard:
        ...

    @property
    def knights(self) -> chess.Bitboard:
        ...

    @property
    def bishops(self) -> chess.Bitboard:
        ...

    @property
    def rooks(self) -> chess.Bitboard:
        ...

    @property
    def queens(self) -> chess.Bitboard:
        ...

    @property
    def kings(self) -> chess.Bitboard:
        ...

    @property
    def white(self) -> chess.Bitboard:
        ...

    @property
    def black(self) -> chess.Bitboard:
        ...

    @property
    def halfmove_clock(self) -> int:
        ...

    @property
    def promoted(self) -> chess.Bitboard:
        ...

    @property
    def fullmove_number(self) -> int:
        ...

    @property
    def castling_rights(self) -> chess.Bitboard:
        ...

    @property
    def occupied(self) -> chess.Bitboard:
        ...

    def occupied_color(self, color: chess.Color) -> chess.Bitboard:
        ...

    def result(
            self,
            claim_draw: bool = False
    ) -> str:
        ...

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
    def ep_square(self) -> int | None:
        ...

    @property
    def fast_representation(self) -> boardKey:
        """
        Returns a fast representation of the board.

        This method computes and returns a string representation of the board
        that can be quickly generated and used for various purposes.

        :return: A string representation of the board.
        :rtype: str
        """
        return self.fast_representation_

    @property
    def fast_representation_without_counters(self) -> boardKeyWithoutCounters:
        """
        Returns a fast representation of the board.

        This method computes and returns a string representation of the board
        that can be quickly generated and used for various purposes.

        :return: A string representation of the board.
        :rtype: str
        """
        assert self.fast_representation_ is not None
        return self.fast_representation_[:-2]

    def is_zeroing(
            self,
            move: T_Move
    ) -> bool:
        ...

    def is_attacked(
            self,
            a_color: chess.Color
    ) -> bool:
        ...

    @property
    def legal_moves(self) -> LegalMoveGeneratorUciP:
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

    def into_fen_plus_history(self) -> FenPlusHistory:
        ...
