"""
Module for creating board evaluators.
"""

import sys
from dataclasses import dataclass
from typing import Any

import dacite
import yaml

from chipiron.players.boardevaluators.basic_evaluation import BasicEvaluation
from chipiron.players.boardevaluators.neural_networks.factory import (
    create_nn_board_eval,
)
from chipiron.players.boardevaluators.neural_networks.neural_net_board_eval_args import (
    NeuralNetBoardEvalArgs,
)
from chipiron.players.boardevaluators.stockfish_board_evaluator import (
    StockfishBoardEvalArgs,
    StockfishBoardEvaluator,
)

from .board_evaluator import (
    BoardEvaluator,
    GameBoardEvaluator,
    IGameBoardEvaluator,
    ObservableBoardEvaluator,
)
from .neural_networks.input_converters.RepresentationType import RepresentationType


class TableBaseArgs:
    """A class representing the arguments for the TableBase class.

    This class provides a template for the arguments that can be passed to the TableBase class.
    It serves as a base class for defining specific argument classes for different implementations
    of the TableBase class.

    Attributes:
        None

    Methods:
        None
    """

    ...


class BasicEvaluationArgs:
    """A class representing the arguments for basic evaluation.

    This class provides a way to store and access the arguments needed for basic evaluation.

    Attributes:
        None

    Methods:
        None
    """

    ...


BoardEvalArgs = (
    NeuralNetBoardEvalArgs
    | StockfishBoardEvalArgs
    | TableBaseArgs
    | BasicEvaluationArgs
)


@dataclass
class BoardEvalArgsWrapper:
    """A wrapper class for the BoardEvalArgs object.

    This class provides a convenient way to access the board_evaluator attribute of the BoardEvalArgs object.

    Attributes:
        board_evaluator (BoardEvalArgs): The BoardEvalArgs object to be wrapped.
    """

    board_evaluator: BoardEvalArgs


def create_board_evaluator(
    args_board_evaluator: BoardEvalArgs,
) -> BoardEvaluator:
    """Create a board evaluator based on the given arguments.

    Args:
        args_board_evaluator (BoardEvalArgs): The arguments for the board evaluator.

    Returns:
        BoardEvaluator: The created board evaluator.

    Raises:
        SystemExit: If the given arguments do not match any supported board evaluator.

    """
    board_evaluator: BoardEvaluator
    match args_board_evaluator:
        case StockfishBoardEvalArgs():
            board_evaluator = StockfishBoardEvaluator(args_board_evaluator)
        case BasicEvaluationArgs():
            board_evaluator = BasicEvaluation()
        case NeuralNetBoardEvalArgs():
            board_evaluator = create_nn_board_eval(
                arg=args_board_evaluator,
                representation_type=RepresentationType.NOBUG364,
            )

        #  case TableBaseArgs():
        #      board_evaluator = None
        case other:
            sys.exit(f"Board Eval: cannot find {other} in file {__name__}")

    return board_evaluator


def create_game_board_evaluator_not_observable(can_stockfish:bool) -> GameBoardEvaluator:
    """Create a game board evaluator that is not observable.

    This function creates a game board evaluator that consists of two board evaluators:
    - board_evaluator_stock: A board evaluator created using the StockfishBoardEvalArgs.
    - board_evaluator_chi: A board evaluator created using the board evaluator configuration
    specified in the 'base_chipiron_board_eval.yaml' file.

    Returns:
        GameBoardEvaluator: The created game board evaluator.
    """
    board_evaluator_stock: BoardEvaluator | None
    if can_stockfish:
        board_evaluator_stock = create_board_evaluator(
                args_board_evaluator=StockfishBoardEvalArgs()
        )
    else:
        board_evaluator_stock =None

    chi_board_eval_yaml_path: str = (
        "data/players/board_evaluator_config/base_chipiron_board_eval.yaml"
    )
    with open(chi_board_eval_yaml_path, "r") as chi_board_eval_yaml_file:
        chi_board_eval_dict: dict[Any, Any] = yaml.load(
            stream=chi_board_eval_yaml_file, Loader=yaml.FullLoader
        )

        # atm using a wrapper because dacite does not accept unions as data_class argument
        chi_board_eval_args: BoardEvalArgsWrapper = dacite.from_dict(
            data_class=BoardEvalArgsWrapper, data=chi_board_eval_dict
        )
        board_evaluator_chi: BoardEvaluator = create_board_evaluator(
            args_board_evaluator=chi_board_eval_args.board_evaluator
        )

    game_board_evaluator: GameBoardEvaluator = GameBoardEvaluator(
        board_evaluator_stock=board_evaluator_stock,
        board_evaluator_chi=board_evaluator_chi,
    )

    return game_board_evaluator


def create_game_board_evaluator(gui: bool, can_stockfish:bool) -> IGameBoardEvaluator:
    """Create a game board evaluator based on the given GUI flag.

    Args:
        gui (bool): A flag indicating whether the GUI is enabled or not.

    Returns:
        IGameBoardEvaluator: An instance of the game board evaluator.

    """
    game_board_evaluator_res: IGameBoardEvaluator
    game_board_evaluator: GameBoardEvaluator = (
        create_game_board_evaluator_not_observable(can_stockfish=can_stockfish)
    )
    if gui:
        game_board_evaluator_res = ObservableBoardEvaluator(
            game_board_evaluator=game_board_evaluator
        )
    else:
        game_board_evaluator_res = game_board_evaluator

    return game_board_evaluator_res
