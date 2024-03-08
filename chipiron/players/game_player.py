import chess
from .player import Player
from chipiron.environments.chess.board import BoardChi
import queue
import copy
from chipiron.utils.communication.player_game_messages import MoveMessage
from chipiron.players.move_selector.move_selector import MoveRecommendation


class GamePlayer:
    """A class that wraps a player for a game purposes
    it adds the color information and probably stuff to continue the computation when the opponent is computing"""

    player: Player
    color: chess.Color

    def __init__(self,
                 player: Player,
                 color: chess.Color):
        self.color = color
        self._player = player

    @property
    def player(self):
        return self._player

    def select_move(
            self,
            board: BoardChi,
            seed: int | None = None
    ) -> MoveRecommendation:
        all_legal_moves = list(board.legal_moves)
        if not all_legal_moves:
            raise Exception('No legal moves in this position')
        best_move: MoveRecommendation = self._player.select_move(
            board=board,
            seed=seed
        )
        return best_move


def game_player_computes_move_on_board_and_send_move_in_queue(
        board: BoardChi,
        game_player: GamePlayer,
        queue_move: queue.Queue,
        seed: int
) -> None:
    if board.turn == game_player.color and not board.board.is_game_over():
        move_recommendation: MoveRecommendation = game_player.select_move(
            board=board,
            seed=seed
        )
        message = MoveMessage(
            move=move_recommendation.move,
            corresponding_board=board.fen(),
            player_name=game_player.player.id,
            evaluation=move_recommendation.evaluation,
            color_to_play=game_player.color
        )
        deep_copy_message = copy.deepcopy(message)
        print('sending ', message)
        queue_move.put(deep_copy_message)
