#  Copyright 2016-2017 Alan F Rubin
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

# -*- coding: utf-8 -*-

"""
This module contains the an abstract class representing the functionality
required by enrich2 to compute scores from counts data.

Example
-------


Notes
-----


Attributes
----------


"""


from abc import ABC, abstractclassmethod
from ..base.storemanager import StoreManager


class BaseScorerPlugin(ABC):
    """
    Base class which outlines required functions that should be 
    overloaded by the user writing a new plugin. It provides a thin
    API that wraps over the StoreManager class and HDF5 class.
    """

    def __init__(self, store_manager, options):
        """
        
        Parameters
        ----------
        store_manager : 
        options : 
        """
        if not isinstance(store_manager, StoreManager):
            raise TypeError("`store` parameter must be of type StoreManager"
                            "[{}].".format(self.__class__.__name__))
        self.name = self.__class__.__name__
        self._store_manager = store_manager
        self._load_scoring_options(options)

    @abstractclassmethod
    def compute_scores(self):
        """
        """
        pass

    @abstractclassmethod
    def row_apply_function(self, *args, **kwargs):
        """
        """
        pass

    def _load_scoring_options(self, options):
        """
        
        Parameters
        ----------
        options : 

        Returns
        -------

        """
        if not isinstance(options, dict):
            raise TypeError("Options must be a dictionary [{}].".format(
                self.__class__.__name__
            ))
        for k, v in options.items():
            setattr(self, k, v)

    def store_get(self, key):
        """
        
        Parameters
        ----------
        key : 

        Returns
        -------

        """
        if not self._store_manager.check_store(key):
            raise ValueError("Store {} does not exist [{}]".format(
                key, self.name
            ))
        else:
            return self._store_manager.store[key]

    def store_put(self, *args, **kwargs):
        """
        
        Parameters
        ----------
        key : 
        data : 
        columns : 
        kwargs : 

        Returns
        -------

        """
        return self._store_manager.store.put(*args, **kwargs)

    def store_remove(self, *args, **kwargs):
        """
        
        Parameters
        ----------
        key : 
        kwargs : 

        Returns
        -------

        """
        self._store_manager.store.remove(*args, **kwargs)
        return self

    def store_append(self, *args, **kwargs):
        """
        
        Parameters
        ----------
        key : 
        data : 
        kwargs : 

        Returns
        -------

        """
        return self._store_manager.store.append(*args, **kwargs)

    def store_check(self, key):
        """
        
        Parameters
        ----------
        key : 

        Returns
        -------

        """
        return self._store_manager.check_store(key)

    def store_select(self, *args, **kwargs):
        """
        
        Parameters
        ----------
        key : 
        kwargs : 

        Returns
        -------

        """
        return self._store_manager.store.select(*args, **kwargs)

    def store_select_as_multiple(self, *args, **kwargs):
        """
        
        Parameters
        ----------
        keys : 
        kwargs : 

        Returns
        -------

        """
        return self._store_manager.store.select_as_multiple(*args, **kwargs)

    def store_labels(self):
        """
        
        Returns
        -------

        """
        return self._store_manager.labels

    def store_roots(self):
        """
        
        Returns
        -------

        """
        return set([k.split('/')[0] for k in self._store_manager.store])

    def store_keys(self):
        """
        
        Returns
        -------

        """
        return [k for k in self._store_manager.store]

    def store_timepoints(self):
        """
        
        Returns
        -------

        """
        if hasattr(self._store_manager, 'timepoints'):
            return self._store_manager.timepoints
        else:
            return []

    def store_timepoint_keys(self):
        """
        
        Returns
        -------

        """
        if hasattr(self._store_manager, 'timepoints'):
            return ['c_{}'.format(t) for t in self._store_manager.timepoints]
        else:
            return []

    def store_default_chunksize(self):
        """
        
        Returns
        -------

        """
        return self._store_manager.chunksize


class Option(object):
    """
    Utility class to represent a user defined option. Mainly used by the 
    GUI to render to a dialogue box.
    """

    def __init__(self, name, varname, dtype, default,
                 choices=None, tooltip="No information"):
        """
        
        Parameters
        ----------
        name : 
        varname : 
        dtype : 
        default : 
        choices : 
        tooltip : 
        """
        self.name = name
        self.varname = varname
        self.dtype = dtype
        self.default = default
        self.choices = [] if choices is None else choices
        self.tooltip = tooltip


class ScoringOptions(object):
    """
    Utility class that is to be used by a plugin developer to add options
    to their scoring script.
    """

    def __init__(self):
        """
        
        """
        self.options = []

    def add_option(self, name, varname, dtype,
                   default, choices=None, tooltip=""):
        """
        
        Parameters
        ----------
        name : 
        varname : 
        dtype : 
        default : 
        choices : 
        tooltip : 

        Returns
        -------

        """
        self.options.append(
            Option(name, varname, dtype, default, choices, tooltip)
        )
        return self