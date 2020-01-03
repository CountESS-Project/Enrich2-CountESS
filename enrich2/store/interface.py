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


"""
Enrich2 base wrapper module
=================================

Contains an interface to abstractly represent store operations such as 
'put', 'append', 'select' etc. Provides classes that concretely implement
this interface.
"""

from abc import ABC, abstractmethod


class StoreInterface(ABC):
    @classmethod
    @abstractmethod
    def __getitem__(self, item):
        pass

    @classmethod
    @abstractmethod
    def __iter__(self):
        pass

    @classmethod
    @abstractmethod
    def __contains__(self, item):
        pass

    @classmethod
    @abstractmethod
    def put(self, key, value, data_columns=None, min_itemsize=None, append=False):
        pass

    @classmethod
    @abstractmethod
    def append(self, key, value, data_columns=None, min_itemsize=None):
        pass

    @classmethod
    @abstractmethod
    def clear(self):
        pass

    @classmethod
    @abstractmethod
    def remove(self, key, where=None):
        pass

    @classmethod
    @abstractmethod
    def select(self, key, where=None, columns=None, chunk=False):
        pass

    @classmethod
    @abstractmethod
    def get_column(self, key, column):
        pass

    @classmethod
    @abstractmethod
    def select_as_multiple(self, keys, where, columns=None, selector=None, chunk=False):
        pass

    @classmethod
    @abstractmethod
    def get(self, key):
        pass

    @classmethod
    @abstractmethod
    def check(self, key):
        pass

    @classmethod
    @abstractmethod
    def backend(self):
        pass

    @classmethod
    @abstractmethod
    def keys(self):
        pass

    @classmethod
    @abstractmethod
    def close(self):
        pass

    @classmethod
    @abstractmethod
    def open(self, path, mode="a"):
        pass

    @classmethod
    @abstractmethod
    def is_open(self):
        pass

    @classmethod
    @abstractmethod
    def set_metadata(self, key, data, update=True):
        pass

    @classmethod
    @abstractmethod
    def get_metadata(self, key):
        pass

    @classmethod
    @abstractmethod
    def check_metadata(self, key, data):
        pass

    @classmethod
    @abstractmethod
    def is_empty(self):
        pass

    @classmethod
    @abstractmethod
    def raise_if_not_open(self):
        pass
