from dataclasses import dataclass, field
from typing import Self

import chess
import shakmaty_python_binding

from chipiron.environments.chess.board.board_modification import BoardModification
from .utils import fen


@dataclass
class RustyBoardChi:
    """
    Rusty Board Chipiron
    object that describes the current board. it wraps the chess Board from the chess package so it can have more in it
    but im not sure its really necessary.i keep it for potential usefulness

    This is the Rust version for speedy execution
    It is based on the binding library shakmaty_python_binding to use the rust library shakmaty
    """

    chess_: shakmaty_python_binding.MyChess

    # the move history is kept here because shakmaty_python_binding.MyChess does not have a move stack at the moment
    move_stack: list[chess.Move]  = field(default_factory=list)

    _original_fen: fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    fast_representation_: str | None = None

    @property
    def original_fen(
            self,
    ) -> fen:
        return self._original_fen

    def play_move(
            self,
            move: chess.Move
    ) -> BoardModification | None:
        self.chess_.play(move.uci())
        return None

    def ply(self) -> int:
        """
        Returns the number of half-moves (plies) that have been played on the board.

        :return: The number of half-moves played on the board.
        :rtype: int
        """
        print('r', self.chess_.ply())
        return self.chess_.ply()

    @property
    def turn(self) -> chess.Color:
        """
        Get the current turn color.

        Returns:
            chess.Color: The color of the current turn.
        """
        return bool(self.chess_.turn())

    def is_game_over(self) -> bool:
        """
        Check if the game is over.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        # todo check the move stack : check for repetition as the rust version not do it
        return self.chess_.is_game_over()

    def copy(
            self,
            stack: bool
    ) -> Self:
        """
        Create a copy of the current board.

        Args:
            stack (bool): Whether to copy the move stack as well.

        Returns:
            RustyBoardChi: A new instance of the BoardChi class with the copied board.
        """
        # todo move stack !!
        chess_copy: shakmaty_python_binding.MyChess = self.chess_.copy()
        return RustyBoardChi(
            chess_=chess_copy
        )

    @property
    def legal_moves(self) -> set[chess.Move]:
        # todo minimize this call and understand when the role of the ariable all legal move generated
        srt_legal_moves = self.chess_.legal_moves()
        move_legal_moves = set()
        for str_move in srt_legal_moves:
            move_legal_moves.add(chess.Move.from_uci(str_move))
        return move_legal_moves

    def number_of_pieces_on_the_board(self) -> int:
        """
        Returns the number of pieces currently on the board.

        Returns:
            int: The number of pieces on the board.
        """
        return self.chess_.number_of_pieces_on_the_board()

    def fen(self) -> str:
        """
        Returns the Forsyth-Edwards Notation (FEN) representation of the chess board.

        :return: The FEN string representing the current state of the board.
        """
        return self.chess_.fen()

    def fast_representation(self) -> str:
        """
        Returns a fast representation of the board.

        This method computes and returns a string representation of the board
        that can be quickly generated and used for various purposes.

        :return: A string representation of the board.
        :rtype: str
        """
        if self.fast_representation_ is None:
            self.fast_representation_ = self.chess_.fen()
        return self.fast_representation_

    def piece_at(
            self,
            square: chess.Square
    ) -> chess.Piece | None:
        """
        Returns the piece at the specified square on the chess board.

        Args:
            square (chess.Square): The square on the chess board.

        Returns:
            chess.Piece | None: The piece at the specified square, or None if there is no piece.

        """
        color: bool
        role: int
        piece_or_none = self.chess_.piece_at(square)
        piece: chess.Piece | None
        if piece_or_none is None:
            piece = None
        else:
            piece = chess.Piece(piece_type=piece_or_none[1], color=piece_or_none[0])
        return piece

    def piece_map(
            self
    ) -> dict[chess.Square, (int, bool)]:
        dict_raw = self.chess_.piece_map()
        return dict_raw

    def has_kingside_castling_rights(
            self,
            color: chess.Color
    ) -> bool:
        """
        Check if the specified color has kingside castling rights.

        Args:
            color (chess.Color): The color to check for kingside castling rights.

        Returns:
            bool: True if the specified color has kingside castling rights, False otherwise.
        """
        return self.chess_.has_kingside_castling_rights(color)

    def has_queenside_castling_rights(
            self,
            color: chess.Color
    ) -> bool:
        """
        Check if the specified color has queenside castling rights.

        Args:
            color (chess.Color): The color to check for queenside castling rights.

        Returns:
            bool: True if the specified color has kingside castling rights, False otherwise.
        """
        return self.chess_.has_queenside_castling_rights(color)

    def print_chess_board(self) -> None:
        """
        Prints the current state of the chess board.

        This method prints the current state of the chess board, including the position of all the pieces.
        It also prints the FEN (Forsyth–Edwards Notation) representation of the board.

        Returns:
            None
        """
        print(self.chess_.fen())

    def tell_result(self) -> None:
        ...

    def result(self) -> str:
        return '*'

    def move_stack(self) -> list:
        return []

    def dump(self, f) -> None:
        ...
