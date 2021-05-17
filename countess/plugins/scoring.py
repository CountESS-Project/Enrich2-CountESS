# -*- coding: utf-8 -*-

"""
Enrich2 plugin scoring module
=============================

This module contains the an abstract class representing the functionality
required by enrich2 to compute scores from counts data.
"""


from abc import ABC, abstractclassmethod
from ..selection.selection import Selection


__all__ = ["BaseScorerPlugin"]


class BaseScorerPlugin(ABC):
    """
    Base class which outlines required functions that should be 
    overloaded by the user writing a new plugin. It provides a thin
    API that wraps over the :py:class:`enrich2.base.storemanager.StoreManager`
    and :py:class`pandas.HDFStore` classes.
        
    Parameters
    ----------
    store_manager : :py:class:`enrich2.base.storemanager.StoreManager`
    options : dict
        A dictionary of key, value mappings defined and expected by the
        plugin which subclasses this ABC. These are the options defined
        by the plugin author, where the key is the *varname* attribute defined
        in :py:class:`enrich2.plugins.options.Options`
    
    Methods
    -------
    compute_scores
    run
    validate
    _load_scoring_options
    store_get
    store_put
    store_remove
    store_append
    store_check
    store_select
    store_select_as_multiple
    store_root_parent
    store_labels
    store_keys
    store_key_roots
    store_timepoints
    store_timepoint_keys
    store_has_wt_sequence
    store_wt_sequence
    store_is_coding
    store_default_chunksize
    """

    _base_name = "BaseScorerPlugin"

    def __init__(self, store_manager, options):
        if not isinstance(store_manager, Selection):
            raise TypeError(
                "`store` parameter must be of type Selection"
                "[{}].".format(self.__class__.__name__)
            )
        self.name = self.__class__.__name__
        self._store_manager = store_manager
        self._load_scoring_options(options)

    @abstractclassmethod
    def compute_scores(self):
        """
        This method is to be overridden by the plugin author. It must
        take a the counts data and place them into a new table called 'scores'
        
        See Also
        --------
        :py:mod:`enrich2.base.constants` for table keys used by ``Enrich2``
        """
        pass

    def run(self):
        """
        Runs the function `compute_scores`. Used internally by ``Enrich2``
        """
        try:
            self.compute_scores()
        except BaseException as err:
            raise Exception(
                "The following error occured when trying to run "
                "plugin '{}': {}.".format(self.name, err)
            )

    @classmethod
    def validate(cls):
        """
        Validates the required detail fields.
        
        Raises
        ------
        AttributeError
            If *name*, *version* or *author* are not strings.
        """
        if not hasattr(cls, "name"):
            raise AttributeError("All plugins " "require 'name' to be specified.")
        if hasattr(cls, "version"):
            raise AttributeError("All plugins " "require 'version' to be specified.")
        if hasattr(cls, "author"):
            raise AttributeError("All plugins " "require 'author' to be specified.")

    def _load_scoring_options(self, options):
        """
        Internal function used to load an attribute dictionary into the class.
        
        Parameters
        ----------
        options : dict
            Attributes to set.

        Raises
        ------
        TypeError
            If *options* is not a `dict`
        """
        if not isinstance(options, dict):
            raise TypeError(
                "Options must be a dictionary [{}].".format(self.__class__.__name__)
            )
        for k, v in options.items():
            setattr(self, k, v)

    def store_get(self, key):
        """
        Wrapper over HDF manipulation. Returns the table located at *key*
        
        Parameters
        ----------
        key : str
            Table key in store.

        Returns
        -------
        :py:class:`pandas.DataFrame`
        
        See Also
        --------
        :py:class:`pandas.HDFStore`
        """
        return self._store_manager.store.get(key)

    def store_put(self, *args, **kwargs):
        """
        Wrapper for HDF manipulation. Puts the table into a 
        :py:class:`pandas.HDFStore`
        
        See Also
        --------
        :py:class:`pandas.HDFStore`
        """
        self._store_manager.store.put(*args, **kwargs)

    def store_remove(self, *args, **kwargs):
        """
        Wrapper for HDF manipulation. Removes a table from a 
        :py:class:`pandas.HDFStore`
        
        See Also
        --------
        :py:class:`pandas.HDFStore`
        """
        self._store_manager.store.remove(*args, **kwargs)

    def store_append(self, *args, **kwargs):
        """
        Wrapper for HDF manipulation. Appends a table to a 
        :py:class:`pandas.HDFStore`

        See Also
        --------
        :py:class:`pandas.HDFStore`
        """
        self._store_manager.store.append(*args, **kwargs)

    def store_check(self, key):
        """
        Checks to see if a table at *key* exists in ``Enrich2``
        
        Parameters
        ----------
        key : str
            String key used for store indexing.

        Returns
        -------
        bool
            True if the table exists.
        """
        return self._store_manager.check_store(key)

    def store_select(self, *args, **kwargs):
        """
        Wrapper for HDF manipulation. Selects data from a 
        :py:class:`pandas.HDFStore`

        See Also
        --------
        :py:class:`pandas.HDFStore`
        """
        return self._store_manager.store.select(*args, **kwargs)

    def store_select_as_multiple(self, *args, **kwargs):
        """
        Wrapper for HDF manipulation. Selects data from multiple  
        :py:class:`pandas.HDFStore` stores.

        See Also
        --------
        :py:class:`pandas.HDFStore`
        """
        return self._store_manager.store.select_as_multiple(*args, **kwargs)

    def store_labels(self):
        """
        Returns the labels used by the ``Enrich2`` store contained by
        this object. Often a selection of 'variants', 'barcodes', 
        'identifiers' and 'synonymous'.
        
        Returns
        -------
        list
            List of string labels.
        """
        return self._store_manager.labels

    def store_root_parent(self):
        """
        Returns the top most parent of this object's 
        :py:class:`enrich2.base.storemanager.StoreManager` store.
        
        Returns
        -------
        :py:class:`enrich2.base.storemanager.StoreManager`
        """
        return self._store_manager.get_root()

    def store_key_roots(self):
        """
        Left most index group being used by ``Enrich2``. Usually 'raw' and 
        'main', the latter indicating a filtered store state.
        
        Returns
        -------
        `set`
            A set of root group keys.
        """
        return set([k.split("/")[0] for k in self._store_manager.store])

    def store_keys(self):
        """
        Returns all keys currently being used in this object's
        :py:class:`enrich2.base.storemanager.StoreManager` store.
        
        Returns
        -------
        `list`
            List of store keys in string format.

        """
        return [k for k in self._store_manager.store]

    def store_timepoints(self):
        """
        Returns the timepoints of a 
        :py:class:`enrich2.base.storemanager.StoreManager` store. Returns and
        empty list if the store contains no timepoints attribute.
        
        Returns
        -------
        `list`
            List of timepoints defined in the experiment selection, defined
            at runtime in the provided configuration file.
        """
        if hasattr(self._store_manager, "timepoints"):
            return self._store_manager.timepoints
        else:
            return []

    def store_timepoint_keys(self):
        """
        Returns a list of timepoints keys in the format 'c_{}' used by the
        :py:class:`enrich2.base.storemanager.StoreManager` store. Returns and
        empty list if the store contains no timepoints attribute.

        Returns
        -------
        `list`
            List of timepoints keys defined as 'c_{}'
        """
        if hasattr(self._store_manager, "timepoints"):
            return ["c_{}".format(t) for t in self._store_manager.timepoints]
        else:
            return []

    def store_has_wt_sequence(self):
        """
        Returns a boolean if this object's 
        :py:class:`enrich2.base.storemanager.StoreManager` store contains
        a *wt_sequence* attribute.

        Returns
        -------
        bool
            True, if the store has a wild type sequence or False otherwise.
        """
        if isinstance(self._store_manager, Selection):
            return self._store_manager.has_wt_sequence()
        else:
            return False

    def store_wt_sequence(self):
        """
        Returns :py:class:`enrich2.sequence.WildType` if this obeject's
        :py:class:`enrich2.base.storemanager.StoreManager` store contains
        a *wt* attribute. Store must be 
        :py:class:`enrich2.selection.selection.Selection` in this case.

        Returns
        -------
        :py:class:`enrich2.sequence.WildType` or None.
        """
        if isinstance(self._store_manager, Selection):
            return self._store_manager.wt()
        else:
            return None

    def store_is_coding(self):
        """
        Returns a boolean if this object's 
        :py:class:`enrich2.base.storemanager.StoreManager` store contains
        an *is_coding* attribute.

        Returns
        -------
        bool
            True, if the store has a coding sequence or False otherwise.
        """
        if isinstance(self._store_manager, Selection):
            return self._store_manager.is_coding()
        else:
            return False

    def store_default_chunksize(self):
        """
        Returns the integer chunksize of the store being wrapped.
        
        Returns
        -------
        int
            Chunksize to be used for table manipulation.
        """
        return self._store_manager.chunksize
