"""
Module to create a chess board.
"""
from collections import Counter
from functools import partial
from typing import Protocol, Any

import chess
import shakmaty_python_binding

from .board_chi import BoardChi
from .iboard import IBoard, compute_key, boardKey
from .rusty_board import RustyBoardChi
from .utils import fen, FenPlusHistory


class BoardFactory(Protocol):
    def __call__(
            self,
            fen_with_history: FenPlusHistory | None = None
    ) -> IBoard[Any]:
        ...


def create_board_factory(
        use_rust_boards: bool = False,
        use_board_modification: bool = False,
        sort_legal_moves: bool = False
) -> BoardFactory:
    board_factory: BoardFactory
    if use_rust_boards:
        board_factory = partial(
            create_rust_board,
            use_board_modification=use_board_modification,
            sort_legal_moves=sort_legal_moves
        )
    else:
        board_factory = partial(
            create_board,
            use_board_modification=use_board_modification,
            sort_legal_moves=sort_legal_moves
        )
    return board_factory


def create_board_chi_from_pychess_board(
        chess_board: chess.Board,
        use_board_modification: bool = False,
        sort_legal_moves: bool = False
) -> BoardChi:
    board_key_representation: boardKey = compute_key(
        pawns=chess_board.pawns,
        knights=chess_board.knights,
        bishops=chess_board.bishops,
        rooks=chess_board.rooks,
        queens=chess_board.queens,
        kings=chess_board.kings,
        turn=chess_board.turn,
        castling_rights=chess_board.castling_rights,
        ep_square=chess_board.ep_square,
        white=chess_board.occupied_co[chess.WHITE],
        black=chess_board.occupied_co[chess.BLACK],
        promoted=chess_board.promoted,
        fullmove_number=chess_board.fullmove_number,
        halfmove_clock=chess_board.halfmove_clock
    )

    board: BoardChi = BoardChi(
        chess_board=chess_board,
        compute_board_modification=use_board_modification,
        fast_representation_=board_key_representation,
        sort_legal_moves=sort_legal_moves
    )
    return board


def create_board(
        fen_with_history: FenPlusHistory | None = None,
        use_board_modification: bool = False,
        sort_legal_moves: bool = False
) -> BoardChi:
    """
    Create a chess board.

    Args:
        use_board_modification (bool): whether to use the board modification
        fen_with_history (FenPlusMoves | None): The BoardWithHistory that contains a fen and the subsequent moves.
            The FEN (Forsyth-Edwards Notation) string representing the board position. If None, the starting position
            is used.

    Returns:
        BoardChi: The created chess board.

    """
    chess_board: chess.Board
    current_fen: fen

    if fen_with_history is not None:
        current_fen = fen_with_history.current_fen
        chess_board = chess.Board(fen=current_fen)
        chess_board.move_stack = [chess.Move.from_uci(move) for move in fen_with_history.historical_moves]
        chess_board._stack = fen_with_history.historical_boards

    else:
        chess_board = chess.Board()

    board: BoardChi = create_board_chi_from_pychess_board(
        chess_board=chess_board,
        use_board_modification=use_board_modification,
        sort_legal_moves=sort_legal_moves
    )
    return board


def create_rust_board(
        fen_with_history: FenPlusHistory | None = None,
        use_board_modification: bool = False,
        sort_legal_moves: bool = False
) -> RustyBoardChi:
    """
    Create a rust chess board.

    Args:
        use_board_modification (bool): whether to use the board modification
        board_with_history (FenPlusMoves | None): The BoardWithHistory that contains a fen and the subsequent moves.
            The FEN (Forsyth-Edwards Notation) string representing the board position. If None, the starting position
            is used.

    Returns:
        RustyBoardChi: The created chess board.

    """
    current_fen: fen
    chess_rust_binding: shakmaty_python_binding.MyChess

    if fen_with_history is not None:
        current_fen = fen_with_history.current_fen
        chess_rust_binding = shakmaty_python_binding.MyChess(_fen_start=current_fen)

    else:
        chess_rust_binding = shakmaty_python_binding.MyChess(_fen_start=chess.STARTING_FEN)

    pawns: int = chess_rust_binding.pawns()
    knights: int = chess_rust_binding.knights()
    bishops: int = chess_rust_binding.bishops()
    rooks: int = chess_rust_binding.rooks()
    queens: int = chess_rust_binding.queens()
    kings: int = chess_rust_binding.kings()
    turn: bool = bool(chess_rust_binding.turn())
    white: int = chess_rust_binding.white()
    black: int = chess_rust_binding.black()
    ep_square_int: int = chess_rust_binding.ep_square()
    promoted: int = chess_rust_binding.promoted()
    castling_rights: int = chess_rust_binding.castling_rights()

    if ep_square_int == -1:
        ep_square = None
    else:
        ep_square = ep_square_int

    board_key_representation: boardKey = compute_key(
        pawns=pawns,
        knights=knights,
        bishops=bishops,
        rooks=rooks,
        queens=queens,
        kings=kings,
        turn=turn,
        castling_rights=castling_rights,
        ep_square=ep_square,
        white=white,
        black=black,
        promoted=promoted,
        fullmove_number=chess_rust_binding.fullmove_number(),
        halfmove_clock=chess_rust_binding.halfmove_clock()
    )

    rusty_board_chi: RustyBoardChi = RustyBoardChi(
        chess_=chess_rust_binding,
        compute_board_modification=use_board_modification,
        rep_to_count=Counter(),
        fast_representation_=board_key_representation,
        sort_legal_moves=sort_legal_moves,
        pawns_=pawns,
        knights_=knights,
        kings_=kings,
        rooks_=rooks,
        queens_=queens,
        bishops_=bishops,
        black_=black,
        white_=white,
        turn_=turn,
        ep_square_=ep_square,
        castling_rights_=castling_rights,
        promoted_=promoted
    )

    if fen_with_history is not None:
        rusty_board_chi.move_stack = fen_with_history.historical_moves

    return rusty_board_chi
