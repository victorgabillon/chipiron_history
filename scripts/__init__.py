"""
init for scripts module
"""
from .one_match.one_match import OneMatchScript
from .replay_game import ReplayGameScript
from .tree_visualization.tree_visualizer import VisualizeTreeScript
from .learn_nn_supervised.learn_nn_from_supervised_datasets import LearnNNScript
from .record_states import RecordStates
from .record_states_eval_stockfish_1 import RecordStateEvalStockfish1
from scripts.league.runtheleague import RunTheLeagueScript
from .script_gui import script_gui
from .script import Script
from .base_tree_exploration.base_tree_exploration import BaseTreeExplorationScript


# instantiate relevant script
def get_script_from_name(
        script_name: str,
        gui_args: object
) -> Script:
    """
    Looks at the script name and starts the corresponding script
    Args:
        script_name:
        gui_args:

    Returns:

    """
    # launch the relevant script
    match script_name:
        case 'one_match':
            script_object = OneMatchScript(gui_args)
        case 'tree_visualization':
            script_object = VisualizeTreeScript()
        case 'learn_nn':
            script_object = LearnNNScript()
        case 'record_states':
            script_object = RecordStates()
        case 'record_state_eval_stockfish':
            script_object = RecordStateEvalStockfish1()
        case 'replay_game':
            script_object = ReplayGameScript()
        case 'run_the_league':
            script_object = RunTheLeagueScript()
        case 'base_tree_exploration':
            script_object = BaseTreeExplorationScript()
        case other:
            raise Exception(f'Cannot find {other}')
    return script_object
