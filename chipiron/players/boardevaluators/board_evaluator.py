import queue
from enum import Enum
from typing import Any
from typing import Protocol

import chess

from chipiron.environments.chess.board.board import BoardChi
from chipiron.utils.communication.gui_messages import EvaluationMessage
from chipiron.utils.is_dataclass import IsDataclass


# VALUE_WHITE_WHEN_OVER is the value_white default value when the node is over
# set atm to be symmetric and high to be preferred

class ValueWhiteWhenOver(float, Enum):
    VALUE_WHITE_WHEN_OVER_WHITE_WINS = 1000.
    VALUE_WHITE_WHEN_OVER_DRAW = 0.
    VALUE_WHITE_WHEN_OVER_BLACK_WINS = -1000.


class BoardEvaluator(Protocol):
    """
    This class evaluates a board
    """

    def value_white(
            self,
            board: BoardChi
    ) -> float:
        """Evaluates a board"""
        ...


class IGameBoardEvaluator(Protocol):
    """

    """

    def evaluate(
            self,
            board: BoardChi
    ) -> tuple[float, float]:
        ...

    def add_evaluation(
            self,
            player_color: chess.Color,
            evaluation: float
    ) -> None:
        # clean at some point!
        ...


class GameBoardEvaluator:
    """
    This class is a collection of evaluator that display their analysis during the game.
    They are not players just external analysis and display
    """
    board_evaluator_stock: BoardEvaluator
    board_evaluator_chi: BoardEvaluator

    def __init__(
            self,
            board_evaluator_stock: BoardEvaluator,
            board_evaluator_chi: BoardEvaluator
    ):
        self.board_evaluator_stock = board_evaluator_stock
        self.board_evaluator_chi = board_evaluator_chi

    def evaluate(
            self,
            board: BoardChi
    ) -> tuple[float, float]:
        evaluation_chi = self.board_evaluator_chi.value_white(board=board)
        evaluation_stock = self.board_evaluator_stock.value_white(board=board)
        return evaluation_stock, evaluation_chi

    def add_evaluation(
            self,
            player_color: chess.Color,
            evaluation: float
    ) -> None:
        # clean at some point!
        ...


class ObservableBoardEvaluator:
    # TODO see if it is possible and desirable to  make a general Observable wrapper that goes all that automatically
    # as i do the same for board and game info
    # todo its becoming hacky...

    game_board_evaluator: GameBoardEvaluator
    mailboxes: list[queue.Queue[IsDataclass]]
    evaluation_stock: Any
    evaluation_chi: Any
    evaluation_player_black: Any
    evaluation_player_white: Any

    def __init__(
            self,
            game_board_evaluator: GameBoardEvaluator
    ):
        self.game_board_evaluator = game_board_evaluator
        self.mailboxes = []
        self.evaluation_stock = None
        self.evaluation_chi = None
        self.evaluation_player_black = None
        self.evaluation_player_white = None

    def subscribe(
            self,
            mailbox: queue.Queue[IsDataclass]
    ) -> None:
        self.mailboxes.append(mailbox)

    # wrapped function
    def evaluate(
            self,
            board: BoardChi
    ) -> tuple[float, float]:
        self.evaluation_stock, self.evaluation_chi = self.game_board_evaluator.evaluate(board=board)

        self.notify_new_results()
        return self.evaluation_stock, self.evaluation_chi

    def add_evaluation(
            self,
            player_color: chess.Color,
            evaluation: float
    ) -> None:
        if player_color == chess.BLACK:
            self.evaluation_player_black = evaluation
        if player_color == chess.WHITE:
            self.evaluation_player_white = evaluation
        self.notify_new_results()

    def notify_new_results(self) -> None:
        for mailbox in self.mailboxes:
            message: EvaluationMessage = EvaluationMessage(
                evaluation_stock=self.evaluation_stock,
                evaluation_chipiron=self.evaluation_chi,
                evaluation_player_white=self.evaluation_player_white,
                evaluation_player_black=self.evaluation_player_black
            )
            mailbox.put(item=message)

    # forwarding
