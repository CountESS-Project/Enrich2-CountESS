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

import pandas as pd
from abc import ABC, abstractclassmethod

import logging
from ..base.utils import log_message


class StoreInterface(ABC):

    @abstractclassmethod
    def __getitem__(self, item):
        pass

    @abstractclassmethod
    def __iter__(self):
        pass

    @abstractclassmethod
    def __contains__(self, item):
        pass

    @abstractclassmethod
    def put(self, key, value, append=False):
        pass

    @abstractclassmethod
    def append(self, key, value, data_columns=None, min_itemsize=None):
        pass

    @abstractclassmethod
    def clear(self):
        pass

    @abstractclassmethod
    def remove(self, key, where=None):
        pass

    @abstractclassmethod
    def select(self, key, where=None, columns=None, chunk=False):
        pass

    @abstractclassmethod
    def select_column(self, key, column):
        pass

    @abstractclassmethod
    def select_as_multiple(self, keys, where, columns=None, selector=None,
                           chunk=False):
        pass

    @abstractclassmethod
    def get(self, key):
        pass

    @abstractclassmethod
    def check(self, key):
        pass

    @abstractclassmethod
    def backend(self):
        pass

    @abstractclassmethod
    def keys(self):
        pass

    @abstractclassmethod
    def close(self, fsync=False):
        pass

    @abstractclassmethod
    def open(self, path, mode='a'):
        pass

    @abstractclassmethod
    def is_open(self):
        pass

    @abstractclassmethod
    def set_metadata(self, key, data, update=True):
        pass

    @abstractclassmethod
    def get_metadata(self, key):
        pass

    @abstractclassmethod
    def check_metadata(self, key, data):
        pass

    @abstractclassmethod
    def is_empty(self):
        pass

    @abstractclassmethod
    def ensure_open(self):
        pass

    @abstractclassmethod
    def flush(self, fsync=False):
        pass

    @abstractclassmethod
    def ensure_has_key(self, key):
        pass


class HDFStore(StoreInterface):
    """
    A wrapper to the the :py:class:`~pandas.HDFStore` class that implements
    the Enrich2 standard store interface.
    
    Parameters
    ----------
    path : `str`, default: ''
        Path to a h5 file, either existing or not.
    mode : `str`, default: 'a'
        Mode to open file.
    chunksize : `int`
        Size to chunk the writing
    format : `str`, default: 'table'
        fixed(f) : Fixed format
                   Fast writing/reading. Not-appendable, nor searchable
        table(t) : Table format
                   Write as a PyTables Table structure which may perform
                   worse but allow more flexible operations like searching
                   / selecting subsets of the data
        
    Attributes
    ----------
    _store : :py:class:`~pandas.HDFStore`
        The HDFStore that this interface provides a wrapper for. Initializes
        to `None` by default.
    _chunksize : `int`
        Size to chunk the writing.
    _format : `str`
        Format specified during initialization. Do not modify once set.
        
    See Also
    --------
    :py:class:`~pandas.HDFStore`
    
    """

    def __init__(self, path='', mode='a', chunksize=10000, format='table'):
        if not isinstance(path, str):
            raise TypeError("`path` must be a string.")
        if not isinstance(mode, str):
            raise TypeError("`mode` must be a string.")
        if not isinstance(chunksize, int):
            raise TypeError("`chunksize` must be an int.")
        if not isinstance(format, str):
            raise TypeError("`format` must be an string.")

        self._store = None
        self._chunksize = chunksize
        self._format = format
        if path:
            self.open(path, mode)

    def __getitem__(self, item):
        return self.get(item)

    def __iter__(self):
        return iter(self.keys())

    def __contains__(self, item):
        return item in self._store

    @property
    def chunksize(self):
        """
        Property for chunksize access.
        """
        return self._chunksize

    @chunksize.setter
    def chunksize(self, value):
        """
        Property for chunksize access.
        
        Parameters
        ----------
        value : `int`
            Value to set chunksize with.
        """
        if not isinstance(value, int):
            raise TypeError("Chunksize must be an int.")
        else:
            self._chunksize = value

    @property
    def filename(self):
        """
        Property for store filename access.
        """
        if self._store is not None:
            return self._store.filename
        return ""

    def is_open(self):
        """
        Returns the open status of the current store.
        
        Returns
        -------
        `bool`
            ``True`` if the store is currently open. ``False`` if _store is
            currently ``None``.
        """
        if self._store is not None and self._store.is_open:
            return True
        return False

    def is_empty(self):
        """
        Returns the empty status of the current store.

        Returns
        -------
        `bool`
            ``True`` if the store has not data in it. ``False`` if otherwise.
        """
        self.ensure_open()
        return not bool(self._store.keys())

    def backend(self):
        """
        Returns the backend being used by this implementation.
        
        Returns
        -------
        `str`
            The backend being used by this StoreInterface.
        """
        return 'pandas.HDFStore'

    def keys(self):
        """
        Returns keys currently stored within the store.

        Returns
        -------
        `list`
            List of keys in the store.
        """
        self.ensure_open()
        return self._store.keys()

    def close(self, fsync=False):
        """
        Closes the currently opened store. Flushes changes to disk by default,
        then sets the current store to ``None``.
        
        Parameters
        ----------
        fsync : `bool`, default: ``False``
          call ``os.fsync()`` on the file handle to force writing to disk.
        """
        if self.is_open():
            self.flush(fsync)
            self._store.close()
        self._store = None

    def flush(self, fsync=False):
        """
        Flushes changes to disk. Not always guranteed to be written
        immediately.

        Parameters
        ----------
        fsync : `bool`, default: ``False``
          call ``os.fsync()`` on the file handle to force writing to disk.
        """
        if self.is_open():
            self._store.flush(fsync)

    def open(self, path, mode='a'):
        """
        Opens the store pointed at by `path`. Closes the current store first 
        if there is one before opening the new store.
        
        Parameters
        ----------
        path : `str`
            The path pointing towards the store.
        mode : `str`, default: 'a'
            File mode to open store with. 
        """
        if self.is_open():
            self.close()
        try:
            self._store = pd.HDFStore(path, mode)
        except ValueError:
            pd.HDFStore(path, mode='a').close()
            self._store = pd.HDFStore(path, mode)
        for key in self.keys():
            if not self.get_metadata(key):
                self.set_metadata(key, {})

    def select(self, key, where=None, columns=None, chunk=False):
        """
        Retrieve pandas object stored at key the current store, optionally 
        based on the `where` criteria.
        
        Creates an index filter based on the ``where`` predicate, then filters 
        the table at ``key`` based on this index filter. The returned 
        dataframe will have columns specified by ``columns``, but only those
        that are found in the table at ``key``.
        
        No errors will be thrown for non-existant columns. An empty dataframe 
        will be returned if no ``columns`` could be matched.

        Parameters
        ----------
        key : `str`
            The table to select from.
        where: `str`
            A predicate string.
        columns : `list`
            List of columns to keep in the returned pandas object.
        chunk : `bool`
            ``True`` to return an iterator of type 
            :py:class:`~pandas.io.pytables.TableIterator` containing 
            selection results of type :py:class:`~pandas.DataFrame`.
            
        Returns
        -------
        :py:class:`~pandas.DataFrame` or 
            :py:class:`~pandas.io.pytables.TableIterator`
        """
        self.ensure_open()
        self.ensure_has_key(key)
        if where is not None and not isinstance(where, str):
            raise TypeError("`where` must be a string.")
        if columns is not None and not isinstance(columns, list):
            raise TypeError("`columns` must be a list.")

        has_columns = False
        if where is not None:
            has_columns = (where.find('columns=') >= 0) or \
                          (where.find('columns =') >= 0) or \
                          (where.find('column=') >= 0) or \
                          (where.find('column =') >= 0) or \
                          (where.find('columns in') >= 0) or \
                          (where.find('column in') >= 0)
        if has_columns:
            raise ValueError("Cannot use keyword 'column(s)' in 'where' when "
                             "using select_as_multiple. Use 'columns' to "
                             "specify the columns to return and "
                             "'where' to specify selection criteria.")
        if has_columns and chunk:
            raise ValueError("Cannot select columns in 'where' and chunk "
                             "simultaneously. This is not supported "
                             "behviour in Pandas. When chunking, use "
                             "'columns' to specify the columns to return and"
                             "'where' to specify selection criteria.")

        result = self._store.select(
            key=key,
            where=where,
            columns=columns,
            chunksize=self.chunksize if chunk else None
        )
        if where is None and columns == ['index']:
            pass
        else:
            if not chunk and result.empty:
                log_message(
                    logging_callback=logging.warning,
                    msg="`select` with the following attributes: "
                        "key='{}', where='{}', columns={}, chunk={} "
                        "returned an empty DataFrame.".format(
                            key, where, columns, chunk),
                    extra={'oname': self.__class__.__name__}
                )
        return result

    def select_column(self, key, column):
        """
        Return a series with integer index from column. An empty series will
        be returned if ``column`` is not a valid column in the table 
        at ``key``.

        Parameters
        ----------
        key : `str`
            The string of the table to subset columns on.
        column: `str`
            Column name of interest.
        
        Returns
        -------
        :py:class:`~pandas.Series`
        """
        self.ensure_open()
        self.ensure_has_key(key)
        if not isinstance(column, str):
            raise TypeError("`column` must be a string.")

        result = self._store.select_column(
            key=key,
            column=column
        )
        if result.empty:
            log_message(
                logging_callback=logging.warning,
                msg="`select_column` with the following attributes: "
                    "key='{}', column='{}' returned an empty "
                    "DataFrame.".format(key, column),
                extra={'oname': self.__class__.__name__}
            )
        return result

    def select_as_multiple(self, keys, where=None,
                           columns=None, selector=None, chunk=False):
        """
        Retrieve pandas objects stored at keys the current store, and 
        optionally apply filtering to each based on the `where` criteria.
        
        Creates an index filter based on the ``where`` predicate applied to 
        keys[0] or a specified ``selector`` table, then filters all tables 
        based on this index filter. The returned dataframe will have combined 
        columns specified by ``columns``. 
        
        No errors will be thrown for non-existant columns. An empty dataframe 
        will be returned if no ``columns`` could be matched to at least one 
        table.

        Parameters
        ----------
        keys : `list`
            list of table keys to select from.
        where: `str`
            A predicate string.
        columns : `list`
            List of columns to keep in the returned pandas object.
        selector : `str`
            the table to apply the where criteria (defaults to keys[0]
            if not supplied)
        chunk : `bool`
            ``True`` to return an iterator of type 
            :py:class:`~pandas.io.pytables.TableIterator` containing 
            selection results of type :py:class:`~pandas.DataFrame`.

        Returns
        -------
        :py:class:`~pandas.DataFrame` or 
            :py:class:`~pandas.io.pytables.TableIterator`
        """
        self.ensure_open()

        keys = list(keys)
        for key in keys:
            self.ensure_has_key(key)

        if where is not None and not isinstance(where, str):
            raise TypeError("`where` must be a string.")
        if columns is not None and not isinstance(columns, list):
            raise TypeError("`columns` must be a list.")
        if selector is not None and not isinstance(selector, str):
            raise TypeError("`selector` must be a string.")

        has_columns = False
        if where is not None:
            has_columns = (where.find('columns=') >= 0) or \
                          (where.find('columns =') >= 0) or \
                          (where.find('column=') >= 0) or \
                          (where.find('column =') >= 0) or \
                          (where.find('columns in') >= 0) or \
                          (where.find('column in') >= 0)
        if has_columns:
            raise ValueError("Cannot use keyword 'column(s)' in 'where' when "
                             "using select_as_multiple. Use 'columns' to "
                             "specify the columns to return and "
                             "'where' to specify selection criteria.")
        if has_columns and chunk:
            raise ValueError("Cannot select columns in 'where' and chunk "
                             "simultaneously. This is not supported "
                             "behviour in Pandas. When chunking, use "
                             "'columns' to specify the columns to return and"
                             "'where' to specify selection criteria.")

        result = self._store.select_as_multiple(
            keys=keys,
            where=where,
            columns=columns,
            selector=selector,
            chunksize=self.chunksize if chunk else None
        )
        if where is None and columns == ['index']:
            pass
        else:
            if not chunk and result.empty:
                log_message(
                    logging_callback=logging.warning,
                    msg="`select_as_multiple` with the following attributes: "
                        "keys={}, where='{}', columns={}, selector='{}', "
                        "chunk={} returned an empty DataFrame.".format(
                            keys, where, columns, selector, chunk),
                    extra={'oname': self.__class__.__name__}
                )
        return result

    def remove(self, key, where=None):
        """
        Remove a table from the store.
        
        Parameters
        ----------
        key : `str`
            Table or node to remove from.
        where: `str`
            A predicate string.

        Returns
        -------
        `int`
            Number of rows removed (or None if not a Table)
        """
        self.ensure_open()
        return self._store.remove(key, where)

    def append(self, key, value, data_columns=None, min_itemsize=None):
        """
        Puts *value* into group *key*. Will append to an existing dataframe
        if *key* is already populated and *append* is ``True``, otherwise
        it will replace any existing data.

        Parameters
        ----------
        key : `str`
            String key pointing to a table in the store.
        value : :py:class:`~pandas.DataFrame`
            The dataframe object to store.
        data_columns : `list`
            List of columns to create as indexed data columns for on-disk
            queries, or True to use all columns. By default only the axes
            of the object are indexed. 
            See `here <http://pandas.pydata.org/pandas-docs/stable/io.html#query-via-data-columns>`
        min_itemsize : `int`:
            The size of the largest index in *value*
        """
        self.ensure_open()
        if self.check(key):
            if set(value.index) & set(self.get(key).index):
                log_message(
                    logging_callback=logging.warning,
                    msg="Appending data with overlapping index. This will "
                        "duplicate entries.",
                    extra={'oname': self.__class__.__name__}
                )

        if isinstance(value.columns, pd.MultiIndex):
            self._store.append(key=key, value=value)
        else:
            if min_itemsize is None:
                max_index_length = max(len(x) for x in value.index)
                min_itemsize = {'index': max_index_length}

            self._store.append(
                key=key,
                value=value,
                min_itemsize=min_itemsize,
                data_columns=data_columns or True
            )

    def put(self, key, value, append=False):
        """
        Puts *value* into group *key*. Will append to an existing dataframe
        if *key* is already populated and *append* is ``True``, otherwise
        it will replace any existing data.
        
        Parameters
        ----------
        key : `str`
            String key pointing to a table in the store.
        value : :py:class:`~pandas.DataFrame`
            The dataframe object to store.
        append : `bool`
            ``True`` to append to an existing dataframe.
        """
        self.ensure_open()
        if append:
            if set(value.index) & set(self.get(key).index):
                log_message(
                    logging_callback=logging.warning,
                    msg="Appending data with overlapping index. This will "
                        "duplicate entries.",
                    extra={'oname': self.__class__.__name__}
                )

        if isinstance(value.columns, pd.MultiIndex):
            self._store.put(key, value, format='table', append=append)
        else:
            self._store.put(
                key, value, format='table',
                append=append, data_columns=True
            )

    def clear(self):
        """
        Clears all data in the store by closing and re-opening in write mode.
        """
        self.ensure_open()
        self.open(self.filename, mode='w')

    def check(self, key):
        """
        Checks if the current store contains the table specified by *key*.
        
        Parameters
        ----------
        key : `str`
            The key to search for.

        Returns
        -------
        `bool`
            ``True`` if *key* specifies a valid table.
        """
        self.ensure_open()
        return key in self.keys()

    def get(self, key):
        """
        Returns the object at *key* or raises a `KeyError`.

        Parameters
        ----------
        key : `str`
            The key to search for.

        Returns
        -------
        :py:class:`~pandas.DataFrame`
            DataFrame at *key*
        """
        self.ensure_open()
        self.ensure_has_key(key)
        if not self.check(key):
            raise KeyError("Key '{}' not found in store.".format(key))
        else:
            return self._store[key]

    def set_metadata(self, key, data, update=False):
        """
        Sets the metadata of the table located at *key* with the supplied
        *data*.

        Parameters
        ----------
        key : `str`
            String key pointing to a table in the store.
        data : `dict`
            The metadata to store.
        update : `bool`
            Dictionary update the metadata instead of replacing it.
        """
        self.ensure_has_key(key)
        if not isinstance(data, dict):
            raise TypeError("Enrich2 metadata must be a `dict`.")
        if update:
            try:
                metadata = self.get_metadata(key)
                metadata.update(data)
            except AttributeError:
                self._store.get_storer(key).attrs.metadata = data
        else:
            self._store.get_storer(key).attrs.metadata = data

    def get_metadata(self, key):
        """
        Returns the metadata stored inside the table at *key*
        
        Parameters
        ----------
        key : `str`
            String key pointing to a table in the store.

        Returns
        -------
        `dict`
            The metadata stored.
        """
        self.ensure_open()
        self.ensure_has_key(key)
        if not self.check(key):
            raise KeyError("Key '{}' does not exist in store.".format(key))
        try:
            return self._store.get_storer(key).attrs.metadata
        except AttributeError:
            return {}

    def check_metadata(self, key, data):
        """
        Checks if the metadata stored at *key* is equal to *data*
        
        Parameters
        ----------
        key : `str`
            String key pointing to a table in the store.
        data : `dict`
            The metadata to check.
            
        Returns
        -------
        `bool`
            ``True`` if stored metadata and supplied metadata are equal
            according to the `==` operator.
        """
        self.ensure_has_key(key)
        if not isinstance(data, dict):
            raise TypeError("Metadata must be a dictionary.")
        this_metadata = self.get_metadata(key)
        return this_metadata == data

    def ensure_open(self):
        """
        Raises a ValueError if there is no open store.
        """
        if not self.is_open():
            raise ValueError("Cannot perform store operation if no store has"
                             " been opened.")

    def ensure_has_key(self, key):
        """
        Throws a KeyError if the key is not found in the store.

        Parameters
        ----------
        key : `str`
            String key pointing to a table in the store.
        """
        self.ensure_open()
        if not self.check(key):
            raise KeyError("Key '{}' not found in store.".format(key))
