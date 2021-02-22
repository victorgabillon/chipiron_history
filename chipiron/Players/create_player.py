import sys
from Players.RandomPlayer import RandomPlayer
from Players.TreeAndValueBuilders.create_tree_and_value import create_tree_and_value_builders
from Players.Human import Human


def create_player(arg, chess_simulator, syzygy):
    if arg['type'] == 'RandomPlayer':
        player = RandomPlayer()
    elif arg['type'] == 'TreeAndValue':
        player = create_tree_and_value_builders(arg, chess_simulator,syzygy)
    elif arg['type'] == 'Human':
        player = Human(arg, chess_simulator)
    else:
        sys.exit('cant find ' + arg['type'])

    player.player_name = arg['name']
    player.syzygy_play = arg['syzygy_play']
    if player.syzygy_play:
        player.syzygy_player = syzygy
    player.print_info()
    return player
