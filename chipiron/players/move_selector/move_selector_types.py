from enum import Enum


class MoveSelectorTypes(str, Enum):
    Random: str = 'Random'
    TreeAndValue: str = 'TreeAndValue'
    Stockfish: str = 'Stockfish'
    Human: str = 'Human'
