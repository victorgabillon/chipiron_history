"""
This module contains classes for handling datasets used in board evaluation tasks.

Classes:
- MyDataSet: A custom dataset class that loads and preprocesses data.
- FenAndValueDataSet: A subclass of MyDataSet that processes raw rows into input and target value tensors.

Functions:
- process_stockfish_value: A function that processes the stockfish value for a given board and row.
"""

import time
from typing import Any

import chess
import numpy as np
import pandas
import pandas as pd
import torch
from torch.utils.data import Dataset

from chipiron.environments.chess.board import BoardChi
from chipiron.environments.chess.board.factory import create_board_chi
from chipiron.environments.chess.board.utils import FenPlusHistory
from chipiron.players.boardevaluators.neural_networks.input_converters.board_to_input import (
    BoardToInputFunction,
)


class MyDataSet(Dataset[Any]):
    """
    A custom dataset class that loads and preprocesses data.

    Attributes:
    - file_name (str): The file name of the dataset.
    - preprocessing (bool): Flag indicating whether to preprocess the dataset.
    - data (pandas.DataFrame | list[tuple[torch.Tensor, torch.Tensor]] | None): The loaded and processed data.
    - len (int | None): The length of the dataset.

    Methods:
    - load(): Loads the dataset from the file.
    - process_raw_row(row: pandas.Series) -> tuple[torch.Tensor, torch.Tensor]: Processes a raw row into input and target tensors.
    """

    data: pandas.DataFrame | list[tuple[torch.Tensor, torch.Tensor]] | None
    len: int | None

    def __init__(self, file_name: str, preprocessing: bool) -> None:
        """
        Initializes a new instance of the MyDataSet class.

        Args:
        - file_name (str): The file name of the dataset.
        - preprocessing (bool): Flag indicating whether to preprocess the dataset.
        """
        self.file_name = file_name
        self.preprocessing = preprocessing
        self.data = None
        self.len = None

    def load(self) -> None:
        """
        Loads the dataset from the file.
        """
        print("Loading the dataset...")
        start_time = time.time()
        raw_data: pandas.DataFrame = pd.read_pickle(self.file_name)
        print("raw_data", type(raw_data))
        raw_data = (
            raw_data.copy()
        )  # gets read of compatibility problem between various version of panda and pickle
        print("--- LOAD READ PICKLE %s seconds ---" % (time.time() - start_time))
        print("Dataset  loaded with {} items".format(len(raw_data)))

        # preprocessing
        if self.preprocessing:
            print("preprocessing dataset...")
            processed_data: list[tuple[torch.Tensor, torch.Tensor]] = []

            for idx in range(len(raw_data)):
                # print(idx, type(idx),idx % 10 == 0)
                if idx % 10 == 0:
                    print("\rloading the data", str(idx / len(raw_data) * 100) + "%")
                row: pandas.Series = raw_data.iloc[idx % len(raw_data)]
                processed_data.append(self.process_raw_row(row))
            self.data = processed_data

            print("preprocessing dataset done")
        else:
            print("no preprocessing the dataset")
            self.data = raw_data

        self.len = len(self.data)

    def process_raw_row(self, row: pandas.Series) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Processes a raw row into input and target tensors.

        Args:
        - row (pandas.Series): The raw row from the dataset.

        Returns:
        - tuple[torch.Tensor, torch.Tensor]: The input and target tensors.
        """
        raise Exception("should not be called")

    def __len__(self) -> int:
        """
        Returns the length of the dataset.

        Returns:
        - int: The length of the dataset.
        """
        assert self.data is not None
        return len(self.data)

    def __getitem__(
        self, idx: int
    ) -> tuple[torch.Tensor, torch.Tensor] | pandas.Series:
        """
        Returns the item at the given index.

        Args:
        - idx (int): The index of the item.

        Returns:
        - tuple[torch.Tensor, torch.Tensor] | pandas.Series: The input and target tensors, or the raw row.
        """
        assert self.data is not None

        if self.preprocessing:
            assert self.len is not None
            return self.data[idx % self.len]
        else:
            assert isinstance(self.data, pandas.DataFrame)
            assert self.len is not None

            raw_row = self.data.iloc[idx % self.len]
            return self.process_raw_row(raw_row)  # to be coded!


def process_stockfish_value(board: BoardChi, row: pandas.Series) -> torch.Tensor:
    """
    Processes the stockfish value for a given board and row.

    Args:
    - board (BoardChi): The chess board.
    - row (pandas.Series): The row from the dataset.

    Returns:
    - torch.Tensor: The processed target value tensor.
    """
    if board.turn == chess.BLACK:
        target_value = -np.tanh(row["stockfish_value"] / 500.0)
    else:
        target_value = np.tanh(row["stockfish_value"] / 500.0)
    target_value_tensor: torch.Tensor = torch.tensor([target_value])
    return target_value_tensor


class FenAndValueDataSet(MyDataSet):
    """
    A subclass of MyDataSet that processes raw rows into input and target value tensors.

    Attributes:
    - transform_board_function (BoardToInputFunction): The function to transform the board into input tensor.
    - transform_value_function (callable): The function to transform the value for a given board and row.

    Methods:
    - process_raw_row(row: pandas.Series) -> tuple[torch.Tensor, torch.Tensor]: Processes a raw row into input and target tensors.
    - process_raw_rows(dataframe: pandas.DataFrame) -> list[tuple[torch.Tensor, torch.Tensor]]: Processes raw rows into input and target tensors.
    """

    transform_board_function: BoardToInputFunction

    def __init__(
        self,
        file_name: str,
        preprocessing: bool = False,
        transform_board_function: str | BoardToInputFunction = "identity",
        transform_value_function: str = "",
    ) -> None:
        """
        Initializes a new instance of the FenAndValueDataSet class.

        Args:
        - file_name (str): The file name of the dataset.
        - preprocessing (bool): Flag indicating whether to preprocess the dataset.
        - transform_board_function (str | BoardToInputFunction): The function to transform the board into input tensor.
        - transform_value_function (str): The function to transform the value for a given board and row.
        """
        super().__init__(file_name, preprocessing)
        # transform function
        if transform_board_function == "identity":
            raise Exception(f"tobe coded in {__name__}")
        else:
            assert isinstance(transform_board_function, BoardToInputFunction)
            self.transform_board_function = transform_board_function

        # transform function
        if transform_value_function == "stockfish":
            self.transform_value_function = process_stockfish_value

    def process_raw_row(self, row: pandas.Series) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Processes a raw row into input and target tensors.

        Args:
        - row (pandas.Series): The raw row from the dataset.

        Returns:
        - tuple[torch.Tensor, torch.Tensor]: The input and target tensors.
        """
        fen = row["fen"]
        board = create_board_chi(
            fen_with_history=FenPlusHistory(current_fen=fen),
            use_board_modification=True,
        )
        input_layer = self.transform_board_function(board)
        target_value = self.transform_value_function(board, row)
        return input_layer.float(), target_value.float()

    def process_raw_rows(
        self, dataframe: pandas.DataFrame
    ) -> list[tuple[torch.Tensor, torch.Tensor]]:
        """
        Processes raw rows into input and target tensors.

        Args:
        - dataframe (pandas.DataFrame): The raw rows from the dataset.

        Returns:
        - list[tuple[torch.Tensor, torch.Tensor]]: The processed input and target tensors.
        """
        processed_data: list[tuple[torch.Tensor, torch.Tensor]] = []
        row: pandas.Series
        for row in dataframe.iloc:
            processed_data.append(self.process_raw_row(row))

        return processed_data
