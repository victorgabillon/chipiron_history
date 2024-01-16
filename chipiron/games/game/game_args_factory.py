import chess
from chipiron.players.factory import create_player
import random
from chipiron.utils.small_tools import unique_int_from_list
from chipiron.players.boardevaluators.table_base.syzygy import SyzygyTable
from chipiron.players.factory import PlayerArgs
from enum import Enum
from dataclasses import dataclass
import typing
from .game_args import GameArgs
from chipiron.players import Player

if typing.TYPE_CHECKING:
    import chipiron.games.match as match


class StaringPositionArgsType(str, Enum):
    fromFile = 'from_file'
    fen = 'fen'


@dataclass
class StaringPositionArgs:
    type: StaringPositionArgsType


@dataclass
class FenStaringPositionArgs(StaringPositionArgs):
    fen: str


@dataclass
class FileStaringPositionArgs(StaringPositionArgs):
    file_name: str


class GameArgsFactory:
    # TODO MAYBE CHANGE THE NAME, ALSO MIGHT BE SPLIT IN TWO (players and rules)?
    """
    The GameArgsFactory creates the players and decides the rules.
    So far quite simple
    This class is supposed to be dependent of Match-related classes (contrarily to the GameArgsFactory)

    """

    args_match: 'match.MatchArgs'
    seed: int | None
    args_player_one: PlayerArgs
    args_player_two: PlayerArgs
    args_game: GameArgs
    game_number: int

    def __init__(self,
                 args_match: 'match.MatchArgs',
                 args_player_one: PlayerArgs,
                 args_player_two: PlayerArgs,
                 seed: int | None,
                 args_game: GameArgs):
        self.args_match = args_match
        self.seed = seed
        self.args_player_one = args_player_one
        self.args_player_two = args_player_two
        self.args_game = args_game
        self.game_number = 0

    def generate_game_args(
            self,
            game_number: int
    ) -> tuple[dict[chess.COLORS, Player], GameArgs]:

        # Creating the players
        syzygy_table = SyzygyTable('')

        merged_seed = unique_int_from_list([self.seed, game_number])

        # if seed is None random uses the current system time as seed
        random_generator: random.Random = random.Random(merged_seed)
        player_one: Player = create_player(args=self.args_player_one,
                                           syzygy=syzygy_table,
                                           random_generator=random_generator)
        player_two: Player = create_player(args=self.args_player_two,
                                           syzygy=syzygy_table,
                                           random_generator=random_generator)

        player_color_to_player: dict[chess.COLORS, Player]
        if game_number < self.args_match.number_of_games_player_one_white:
            player_color_to_player = {chess.WHITE: player_one, chess.BLACK: player_two}
        else:
            player_color_to_player = {chess.WHITE: player_two, chess.BLACK: player_one}
        self.game_number += 1

        return player_color_to_player, self.args_game

    def is_match_finished(self):
        return (self.game_number >= self.args_match.number_of_games_player_one_white
                + self.args_match.number_of_games_player_one_black)
