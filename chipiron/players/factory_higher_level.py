"""
Module for creating player observers.
"""

import multiprocessing
import queue
from functools import partial
from typing import Any, Protocol

import chess

from chipiron.environments.chess.board import IBoard
from chipiron.utils import seed
from chipiron.utils.communication.player_game_messages import BoardMessage
from chipiron.utils.dataclass import IsDataclass

from ..scripts.chipiron_args import ImplementationArgs
from .boardevaluators.table_base import SyzygyTable
from .factory import create_game_player
from .game_player import (
    GamePlayer,
    game_player_computes_move_on_board_and_send_move_in_queue,
)
from .player_args import PlayerFactoryArgs
from .player_thread import PlayerProcess


# function that will be called by the observable game when the board is updated, which should query at least one player
# to compute a move
# MoveFunction = Callable[[BoardChi, seed], None]
class MoveFunction(Protocol):
    """
    Represents a move function that can be called on a game board.

    Args:
        board (BoardChi): The game board on which the move function is applied.
        seed_int (seed): The seed used for the move function.

    Returns:
        None: This function does not return any value.
    """

    def __call__(self, board: IBoard, seed_int: seed) -> None: ...


def send_board_to_player_process_mailbox(
    board: IBoard, seed_int: int, player_process_mailbox: queue.Queue[BoardMessage]
) -> None:
    """Sends the board and seed to the player process mailbox.

    This function creates a BoardMessage object with the given board and seed,
    and puts it into the player_process_mailbox.

    Args:
        board (IBoard): The board to send.
        seed_int (int): The seed to send.
        player_process_mailbox (queue.Queue[BoardMessage]): The mailbox to put the message into.
    """
    message: BoardMessage = BoardMessage(
        fen_plus_moves=board.into_fen_plus_history(), seed=seed_int
    )
    player_process_mailbox.put(item=message)


class PlayerObserverFactory(Protocol):
    """
    creates the player and the means to communicate with it
    """

    def __call__(
        self,
        player_factory_args: PlayerFactoryArgs,
        player_color: chess.Color,
        main_thread_mailbox: queue.Queue[IsDataclass],
    ) -> tuple[GamePlayer | PlayerProcess, MoveFunction]: ...


def create_player_observer_factory(
    each_player_has_its_own_thread: bool,
    implementation_args: ImplementationArgs,
    universal_behavior: bool,
    syzygy_table: SyzygyTable[Any] | None,
) -> PlayerObserverFactory:
    player_observer_factory: PlayerObserverFactory
    if each_player_has_its_own_thread:
        player_observer_factory = partial(
            create_player_observer_distributed_players,
            implementation_args=implementation_args,
            universal_behavior=universal_behavior,
        )
    else:
        player_observer_factory = partial(
            create_player_observer_mono_process, syzygy_table=syzygy_table
        )
    return player_observer_factory


def create_player_observer_distributed_players(
    player_factory_args: PlayerFactoryArgs,
    player_color: chess.Color,
    main_thread_mailbox: queue.Queue[IsDataclass],
    implementation_args: ImplementationArgs,
    universal_behavior: bool,
) -> tuple[GamePlayer | PlayerProcess, MoveFunction]:
    """Create a player observer.

    This function creates a player observer based on the given parameters.

    Args:
        board_factory: the board factory to create a board
        player_factory_args (PlayerFactoryArgs): The arguments for creating the player.
        player_color (chess.Color): The color of the player.
        main_thread_mailbox (queue.Queue[IsDataclass]): The mailbox for communication between the main thread
        and the player.

    Returns:
        tuple[ PlayerProcess, MoveFunction]: A tuple containing the player observer and the move function.

    """
    generic_player: PlayerProcess
    move_function: MoveFunction

    # case with multiprocessing when each player is a separate process
    # creating objects Queue that is the mailbox for the player thread
    player_process_mailbox = multiprocessing.Manager().Queue()

    # creating and starting the thread for the player
    player_process: PlayerProcess = PlayerProcess(
        player_factory_args=player_factory_args,
        player_color=player_color,
        queue_receiving_board=player_process_mailbox,
        queue_sending_move=main_thread_mailbox,
        implementation_args=implementation_args,
        universal_behavior=universal_behavior,
    )
    player_process.start()
    generic_player = player_process

    move_function = partial(
        send_board_to_player_process_mailbox,
        player_process_mailbox=player_process_mailbox,
    )

    return generic_player, move_function


def create_player_observer_mono_process(
    player_factory_args: PlayerFactoryArgs,
    player_color: chess.Color,
    main_thread_mailbox: queue.Queue[IsDataclass],
    syzygy_table: SyzygyTable[Any] | None,
) -> tuple[GamePlayer, MoveFunction]:
    """Create a player observer.

    This function creates a player observer based on the given parameters.

    Args:
        player_factory_args (PlayerFactoryArgs): The arguments for creating the player.
        player_color (chess.Color): The color of the player.
        main_thread_mailbox (queue.Queue[IsDataclass]): The mailbox for communication between the main thread
        and the player.

    Returns:
        tuple[GamePlayer | PlayerProcess, MoveFunction]: A tuple containing the player observer and the move function.

    """
    generic_player: GamePlayer
    move_function: MoveFunction

    # case without multiprocessing all players and match manager in the same process

    generic_player = create_game_player(
        player_factory_args=player_factory_args,
        player_color=player_color,
        syzygy_table=syzygy_table,
        queue_progress_player=main_thread_mailbox,
    )
    move_function = partial(
        game_player_computes_move_on_board_and_send_move_in_queue,
        game_player=generic_player,
        queue_move=main_thread_mailbox,
    )

    return generic_player, move_function
