"""
Module where we define the Stockfish Board Evaluator
"""
import chess.engine
import chipiron.environments.chess.board as boards
from dataclasses import dataclass


# TODO are we calling this?
@dataclass
class StockfishBoardEvalArgs:
    depth: int = 20
    time_limit: float = 0.1


class StockfishBoardEvaluator:
    """
    A board evaluator powered by stockfish
    """

    def __init__(self,
                 args: StockfishBoardEvalArgs):
        self.engine = None

    def value_white(
            self,
            board: boards.BoardChi
    ):
        print('infos')
        # todo make a large reformat so that the players are created after the launch of process
        """ computes the value white of the board"""
        if self.engine is None:
            # if this object is created in the init then seending the object
            self.engine = chess.engine.SimpleEngine.popen_uci(
                # TODO: should we remove the hardcoding
                r"stockfish/stockfish/stockfish-ubuntu-x86-64-avx2")
            # self.engine = chess.engine.SimpleEngine.popen_uci("/home/victor_old/.pycharm/chipiron/stockfish/stockfish/stockfish_14.1_linux_x64")
        # looks like the engine dos not work when the gui is on ???!!!???
        # info = engine.analyse(board, chess.engine.Limit(time=0.1))
        info = self.engine.analyse(board, chess.engine.Limit(time=0.1))
        self.engine.quit()
        self.engine = None
        return info["score"]


