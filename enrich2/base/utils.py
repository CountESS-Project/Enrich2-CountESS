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


import numpy as np
import pandas as pd


def nested_format(data, default, tab_level=1):
    """
    Print a human readable nested dictionary or nested list.
    
    Parameters
    ----------
    data : object
        Data to print.
    default: bool
        Indicator indicating if a value is a default. 
    tab_level : int
        Number of tabs to indent with.  

    Returns
    -------
    str
        A formatted string.
    """
    msg = ""
    if isinstance(data, list) or isinstance(data, tuple):
        if not data:
            msg += 'Empty Iterable'
        else:
            msg += "-> Iterable"
            if default:
                msg += "-> Iterable [Default]"
            try:
                for i, (value, default) in enumerate(data):
                    msg += '\n' + '\t' * tab_level + '@index {}: '.format(i)
                    msg += nested_format(value, default, tab_level)
            except (TypeError, ValueError):
                for i, value in enumerate(data):
                    msg += '\n' + '\t' * tab_level + '@index {}: '.format(i)
                    msg += nested_format(value, False, tab_level)
            msg += '\n' + '\t' * tab_level + '@end of list'
    elif isinstance(data, dict):
        if not data:
            msg += 'Empty Dictionary'
        else:
            msg += "-> Dictionary"
            if default:
                msg += "-> Dictionary [Default]"
            try:
                for key, (value, default) in data.items():
                    msg += '\n' + "\t" * tab_level + "{}: ".format(key)
                    msg += nested_format(value, default, tab_level + 1)
            except (TypeError, ValueError):
                for key, value in data.items():
                    msg += '\n' + "\t" * tab_level + "{}: ".format(key)
                    msg += nested_format(value, False, tab_level + 1)
    else:
        if isinstance(data, str):
            data = "'{}'".format(data)
        dtype = type(data).__name__
        if default:
            msg += "({} [Default], {})".format(data, dtype)
        else:
            msg += "({}, {})".format(data, dtype)
    return msg


def count_nans(data, axis):
    """
    Sums the number of NaN values along an axis of data.

    Parameters
    ----------
    data : :py:class:`np.ndarray`
        The data to count NaNs along *axis*
    axis : int {0, 1}
        1 for row-wise sum and 0 for column-wise sum

    Returns
    -------
    :py:class:`np.ndarray`
        The number of NaN appearing in each column
    """
    return np.sum(np.isnan(data), axis=axis)


def generate_selector(data, threshold):
    """
    Generates a truthy selector array for elements in data greater than
    *threshold*
    
    Parameters
    ----------
    data : :py:class:`np.ndarray`
        The numpy array to turn into a boolean numpy array.
    threshold : int or float
        An integer or floating point value to compare each element
        in *data* to.
        
    Returns
    -------
    :py:class:`np.ndarray`
        A boolean numpy array for each element greater than *threshold*
    """
    return data > threshold


def multi_index_tsv_to_dataframe(filepath, header_rows):
    """
    Loads a multi-header tsv file into a :py:class:`pd.DataFrame`.
    
    Parameters
    ----------
    filepath : str
        Path pointing to the tsv file.
    header_rows : list
        0-based indicies corresponding to the row locations to use as the 
        multi-index column names in the dataframe. Example:
        
        condition	E3	E3
        value	pvalue_raw	z
        _sy	8.6e-05	3.92
        p.Ala16Arg	0.0	3.76
        
        The *header_rows* for this instance will be [0, 1]

    Returns
    -------
    :py:class:`pd.DataFrame`
        A :py:class:`pd.MultiIndex` dataframe.
    """
    return pd.read_table(filepath, index_col=0, header=header_rows)

    
