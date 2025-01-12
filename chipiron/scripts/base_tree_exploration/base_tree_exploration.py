"""
This module contains the implementation of the BaseTreeExplorationScript class.

The BaseTreeExplorationScript class is responsible for running a script that performs base tree exploration in a chess game.
"""

import os
import random
from dataclasses import dataclass, field

from chipiron.environments.chess.board.factory import create_board
from chipiron.players.boardevaluators.table_base.factory import create_syzygy
from chipiron.players.factory import create_player
from chipiron.players.player_args import PlayerArgs
from chipiron.players.player_ids import PlayerConfigFile
from chipiron.players.utils import fetch_player_args_convert_and_save
from chipiron.scripts.chipiron_args import ImplementationArgs
from chipiron.scripts.script import Script
from chipiron.scripts.script_args import BaseScriptArgs


@dataclass
class BaseTreeExplorationArgs:
    base_script_args: BaseScriptArgs = field(default_factory=BaseScriptArgs)
    implementation_args: ImplementationArgs = field(default_factory=ImplementationArgs)


class BaseTreeExplorationScript:
    """
    The BaseTreeExplorationScript
    """

    args_dataclass_name: type[BaseTreeExplorationArgs] = BaseTreeExplorationArgs
    base_experiment_output_folder = os.path.join(
        Script.base_experiment_output_folder, "base_tree_exploration/outputs/"
    )
    base_script: Script

    def __init__(self, base_script: Script) -> None:
        """
        Initializes a new instance of the BaseTreeExploration class.

        Args:
            base_script (Script): The base script to be used for tree exploration.
        """
        self.base_script = base_script

        # Calling the init of Script that takes care of a lot of stuff, especially parsing the arguments into args
        self.args: BaseTreeExplorationArgs = self.base_script.initiate(
            experiment_output_folder=self.base_experiment_output_folder,
            args_dataclass_name=BaseTreeExplorationArgs,
        )

    def run(self) -> None:
        """
        Runs the base tree exploration script.
        """
        syzygy = create_syzygy(use_rust=self.args.implementation_args.use_rust_boards)

        file_name_player = PlayerConfigFile.Uniform

        player_one_args: PlayerArgs = fetch_player_args_convert_and_save(
            file_name_player=file_name_player
        )

        # player_one_args.main_move_selector.stopping_criterion.tree_move_limit = 1000000
        random_generator = random.Random()
        random_generator.seed(self.args.implementation_args.use_rust_boards)
        player = create_player(
            args=player_one_args, syzygy=syzygy, random_generator=random_generator
        )

        board = create_board(
            use_rust_boards=self.args.implementation_args.use_rust_boards,
            use_board_modification=self.args.implementation_args.use_board_modification,
        )
        player.select_move(
            board=board, seed_int=self.args.implementation_args.use_rust_boards
        )

    def terminate(self) -> None:
        """
        Terminates the base tree exploration script.
        """
        self.base_script.terminate()
