class GamePlayer:
    """A class that wraps a player for a game purposes
    it adds the color information and probably stuff to continue the computation when the opponent is computing"""

    def __init__(self, player, color):
        self.color = color
        self._player = player

    @property
    def player(self):
        return self._player

    def select_move(self, board):
        best_move = self._player.select_move(board)
        return best_move
