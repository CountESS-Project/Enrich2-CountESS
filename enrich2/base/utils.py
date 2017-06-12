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
Enrich2 base utility module
===========================

Contains various utility functions used through-out enrich2
"""


import numpy as np
import pandas as pd
from queue import Queue
import hashlib
import os
import logging

from .config_constants import BARCODE_MAP_FILE, READS, COUNTS_FILE, SCORER_PATH
from ..base.constants import CALLBACK, MESSAGE, KWARGS

__all__ = [
    "nested_format",
    "count_nans",
    "generate_selector",
    "fix_filename",
    "multi_index_tsv_to_dataframe",
    "file_md5s_equal",
    "recursive_dict_equal",
    'compute_md5',
    'init_logging_queue',
    'get_logging_queue',
    'log_message'
]


LOG_QUEUE = None


def init_logging_queue():
    """
    Inits the logging queue if it is ``None``.
    """
    global LOG_QUEUE
    if LOG_QUEUE is None:
        LOG_QUEUE = Queue()
        log_message(
            logging.info,
            'Logging Queue has been initialized.',
            extra={'oname': 'Utilities'}
        )


def get_logging_queue(init=False):
    """
    Gets the current active queue instance.
    
    Parameters
    ----------
    init : `bool`
        Init the queue before returning it.
    
    Returns
    -------
    :py:class:`Queue`
    """
    if init:
        init_logging_queue()
    return LOG_QUEUE


def log_message(logging_callback, msg, **kwargs):
    """
    Places a logging message into the active queue.
    
    Parameters
    ----------
    logging_callback : `Callable`
        The logging function to use from the logging module.
    msg : `str`
        The message to log.
    kwargs : `dict`
        Keyword arguments for logging module.
    """
    log = {CALLBACK: logging_callback, MESSAGE: msg, KWARGS: kwargs}
    # if 'extra' in kwargs:
    #     if 'oname' not in kwargs:
    #         kwargs['oname'] = 'OnameNotSupplied'
    queue = get_logging_queue(init=False)
    if queue is None:
        logging_callback(msg, **kwargs)
    else:
        queue.put(log)


def nested_format(data, default, tab_level=1):
    """
    Print a human readable nested dictionary or nested list.
    
    Parameters
    ----------
    data : `object`
        Data to print.
    default: `bool`
        Indicator indicating if a value is a default. 
    tab_level : `int`
        Number of tabs to indent with.  

    Returns
    -------
    `str`
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
    data : :py:class:`~np.ndarray`
        The data to count NaNs along *axis*
    axis : `int` {0, 1}
        1 for row-wise sum and 0 for column-wise sum

    Returns
    -------
    :py:class:`~np.ndarray`
        The number of NaN appearing in each column
    """
    return np.sum(np.isnan(data), axis=axis)


def generate_selector(data, threshold):
    """
    Generates a truthy selector array for elements in data greater than
    *threshold*
    
    Parameters
    ----------
    data : :py:class:`~np.ndarray`
        The numpy array to turn into a boolean numpy array.
    threshold : `int` or `float`
        An integer or floating point value to compare each element
        in *data* to.
        
    Returns
    -------
    :py:class:`~np.ndarray`
        A boolean numpy array for each element greater than *threshold*
    """
    return data > threshold


def multi_index_tsv_to_dataframe(filepath, header_rows):
    """
    Loads a multi-header tsv file into a :py:class:`pd.DataFrame`.
    
    Parameters
    ----------
    filepath : `str`
        Path pointing to the tsv file.
    header_rows : `list`
        0-based indicies corresponding to the row locations to use as the 
        multi-index column names in the dataframe. Example:
        
        condition	E3	E3
        value	pvalue_raw	z
        _sy	8.6e-05	3.92
        p.Ala16Arg	0.0	3.76
        
        The *header_rows* for this instance will be [0, 1]

    Returns
    -------
    :py:class:`~pd.DataFrame`
        A :py:class:`pd.MultiIndex` dataframe.
    """
    return pd.read_table(filepath, index_col=0, header=header_rows)


def fix_filename(s):
    """
    Clean up a file name by removing invalid characters and converting 
    spaces to underscores.
    
    Parameters
    ----------
    s : `str`
        File name
    
    Returns
    -------
    `str`
        Cleaned file name
    """
    fname = "".join(c for c in s if c.isalnum() or c in (' ._~'))
    fname = fname.replace(' ', '_')
    return fname


def file_md5s_equal(f1, f2):
    """
    Compared the MD5 hashes of two files.
    
    Parameters
    ----------
    f1 : `str`
        File path for the first file.
    f2 : `str`
        File path for the second file.

    Returns
    -------
    `bool`
        ``True`` if both files have the same MD5 sum. 
    """
    with open(f1, 'rb') as fp:
        f1_md5 = hashlib.md5(fp.read()).hexdigest()
    with open(f2, 'rb') as fp:
        f2_md5 = hashlib.md5(fp.read()).hexdigest()
    return f1_md5 == f2_md5


def compute_md5(fname):
    """
    Returns the MD5 sum of a file at some path, or an empty string
    if the file does not exist.
    
    Parameters
    ----------
    fname : `str`
        Path to file.

    Returns
    -------
    `str`
        MD5 string of the hashed file.
    """
    md5 = ""
    if fname is None:
        return md5
    if os.path.isfile(fname):
        fp = open(fname, 'rb')
        md5 = hashlib.md5(fp.read()).hexdigest()
        fp.close()
    return md5


def recursive_dict_equal(d1, d2, md5_on_file=True):
    """
    Compares two Enrich2 configuration files recursively. Will check
    md5s for keys that point to files if requested, other wise a basic 
    string comparison on filenames is performed.
    
    Parameters
    ----------
    d1 : `dict`
        Configuraion dictionary A.
    d2 : `dict`
        Configuraion dictionary B.
    md5_on_file : `bool`
        Use MD5 sum comparison for filenames.

    Returns
    -------
    `bool`
        ``True`` if all elements in the configuration are equal.
    """
    for key, value in d1.items():
        other_value = d2.get(key, None)
        if other_value is None:
            return False
        if type(value) != type(other_value):
            return False
        if isinstance(value, dict):
            return recursive_dict_equal(value, other_value)
        if isinstance(value, list):
            if len(value) != len(other_value):
                return False
            else:
                for ls_value, other_ls_value in zip(value, other_value):
                    return recursive_dict_equal(ls_value, other_ls_value)

        # Compare md5 of the files for relevant keys.
        file_path_keys = {BARCODE_MAP_FILE, COUNTS_FILE, SCORER_PATH, READS}
        file_path_md5_keys = ["{} md5".format(k) for k in file_path_keys]

        if key in file_path_md5_keys and md5_on_file:
            same_md5 = (value == other_value)
            if not same_md5:
                d1_file_name = d1[key[:-5]]
                d2_file_name = d1[key[:-5]]
                if d1_file_name == d2_file_name:
                    log_message(
                        logging_callback=logging.warning,
                        msg="File '{}' found in both configurations was "
                        "found to have the MD5 sum {} for this configuration "
                        "but MD5 sum {} for the previous configuration."
                        "".format(d1_file_name, value, other_value),
                        extra={'oname': 'Utilities'}
                    )
                return same_md5
        else:
            return value == other_value
