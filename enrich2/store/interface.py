#  Copyright 2016-2017 Alan F Rubin, Daniel C Esposito
#
#  This file is part of Enrich2.
#
#  Enrich2 is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Enrich2 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Enrich2.  If not, see <http://www.gnu.org/licenses/>.

from abc import ABCMeta, abstractmethod
from typing import List, Sequence, Mapping, Dict, Any, Union
from os import PathLike
import pathlib
import numpy as np
import dask.dataframe as dd
import pandas as pd


class StoreInterface(metaclass=ABCMeta):
    file_extensions = None

    def __init__(self, path: Union[PathLike, str]) -> None:
        self._keys = list()
        if isinstance(path, str):
            self._path = pathlib.Path(path)
        elif isinstance(path, PathLike):
            self._path = path
        else:
            raise TypeError(f"invalid file path object for {self.__class__.__name__}")
        if self._path.suffix not in self.file_extensions:
            raise ValueError(f"invalid file extension for {self.__class__.__name__}")

    def keys(self) -> List[str]:
        return self._keys

    def is_empty(self) -> bool:
        return len(self._keys) == 0

    @property
    def path(self) -> str:
        return self._path

    @abstractmethod
    def put(self, key: str, value: Union[dd.DataFrame, pd.DataFrame]) -> None:
        pass

    @abstractmethod
    def drop(self, key: str) -> None:
        pass

    @abstractmethod
    def get(self, key: str) -> dd.DataFrame:
        pass

    @abstractmethod
    def get_column(self, key: str, column: str) -> np.ndarray:
        pass

    @abstractmethod
    def get_with_merge(self, keys: Sequence[str]) -> dd.DataFrame:
        pass

    @abstractmethod
    def set_metadata(
        self, key: str, metadata: Mapping[str, Any], update: bool = True
    ) -> None:
        pass

    @abstractmethod
    def get_metadata(self, key: str) -> Dict[str, Any]:
        pass
