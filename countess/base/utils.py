"""
Enrich2 base utility module
===========================

Contains various utility functions used through-out enrich2
"""


import pandas as pd
from queue import Queue
import hashlib
import os
import logging
import traceback

from ..base.constants import CALLBACK, MESSAGE, KWARGS


__all__ = [
    "nested_format",
    "fix_filename",
    "multi_index_tsv_to_dataframe",
    "infer_multiindex_header_rows",
    "is_number",
    "compute_md5",
    "init_logging_queue",
    "get_logging_queue",
    "log_message",
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
            "Logging Queue has been initialized.",
            extra={"oname": "Utilities"},
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
    msg : `str` or `Exception`
        The message to log.
    kwargs : `dict`
        Keyword arguments for logging module.
    """
    log = {CALLBACK: logging_callback, MESSAGE: msg, KWARGS: kwargs}
    queue = get_logging_queue(init=False)
    if queue is None:
        logging_callback(msg, **kwargs)
        if isinstance(msg, Exception):
            tb = msg.__traceback__
            logging.exception("".join(traceback.format_tb(tb)), **kwargs)
    else:
        queue.put(log)
        if isinstance(msg, Exception):
            tb = msg.__traceback__
            error = {
                CALLBACK: logging.exception,
                MESSAGE: "".join(traceback.format_tb(tb)),
                KWARGS: kwargs,
            }
            queue.put(error)


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
            msg += "Empty Iterable"
        else:
            msg += "-> Iterable"
            if default:
                msg += "-> Iterable [Default]"
            try:
                for i, (value, default) in enumerate(data):
                    msg += "\n" + "\t" * tab_level + "@index {}: ".format(i)
                    msg += nested_format(value, default, tab_level)
            except (TypeError, ValueError):
                for i, value in enumerate(data):
                    msg += "\n" + "\t" * tab_level + "@index {}: ".format(i)
                    msg += nested_format(value, False, tab_level)
            msg += "\n" + "\t" * tab_level + "@end of list"
    elif isinstance(data, dict):
        if not data:
            msg += "Empty Dictionary"
        else:
            msg += "-> Dictionary"
            if default:
                msg += "-> Dictionary [Default]"
            try:
                for key, (value, default) in data.items():
                    msg += "\n" + "\t" * tab_level + "{}: ".format(key)
                    msg += nested_format(value, default, tab_level + 1)
            except (TypeError, ValueError):
                for key, value in data.items():
                    msg += "\n" + "\t" * tab_level + "{}: ".format(key)
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


def multi_index_tsv_to_dataframe(filepath, sep="\t", header_rows=None):
    """
    Loads a multi-header tsv file into a :py:class:`pd.DataFrame`.
    
    Parameters
    ----------
    filepath : `str`
        Path pointing to the tsv file.
    sep : `str`, optional, default: '\t'
        Character to use as the delimiter. 
    header_rows : `list`, optional, default: None
        0-based indicies corresponding to the row locations to use as the 
        multi-index column names in the dataframe. Example:
        
        condition	E3	E3
        value	pvalue_raw	z
        _sy	8.6e-05	3.92
        p.Ala16Arg	0.0	3.76raw_barcodes_counts.tsv
        
        The *header_rows* for this instance will be [0, 1]
        
        If not supplied, `header_rows` will be inferred from the file.

    Returns
    ------- 
    :py:class:`~pd.DataFrame`
        A :py:class:`pd.MultiIndex` dataframe.
    """
    if header_rows is None:
        header_rows = infer_multiindex_header_rows(filepath)

    if header_rows == [0] or not header_rows:
        return pd.read_table(filepath, index_col=0, sep=sep)
    else:
        try:
            return pd.read_table(filepath, index_col=0, sep=sep, header=header_rows)
        except IndexError:
            return pd.read_table(filepath, index_col=0, sep=sep)


def infer_multiindex_header_rows(filepath):
    """
    Infers which columns from a tsv file should be used as a header when
    loading a multi-index or single-index tsv. NaN values in the tsv
    must be encoded with the string 'NaN' for this function to correctly
    infer header columns.

    Parameters
    ----------
    filepath : `str`
        Path pointing to the tsv file.

    Returns
    -------
    `list`
        0-based indicies corresponding to the row locations to use as the 
        multi-index column names in the dataframe. Example:

        condition	E3	E3
        value	pvalue_raw	z
        _sy	8.6e-05	3.92
        p.Ala16Arg	0.0	3.76

        The *header_rows* for this instance will be [0, 1]
    """
    header_rows = []
    with open(filepath, "rt") as fp:
        for i, line in enumerate(fp):
            xs = [x.strip() for x in line.split("\t") if x.strip()]
            skip_line = (not xs) or any([is_number(s) for s in xs])
            if skip_line:
                break
            else:
                header_rows.append(i)
    return header_rows


def is_number(s):
    """
    Check if a string s represents a number

    Parameters
    ----------
    s : `str`
        String to check
        
    Returns
    -------
    `bool`
        ``True`` if a string represents an integer or floating point number
    """
    try:
        int(s)
        is_int = True
    except ValueError:
        is_int = False

    try:
        float(s)
        is_float = True
    except ValueError:
        is_float = False

    return is_float | is_int


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
    fname = "".join(c for c in s if c.isalnum() or c in (" ._~"))
    fname = fname.replace(" ", "_")
    return fname


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
        fp = open(fname, "rb")
        md5 = hashlib.md5(fp.read()).hexdigest()
        fp.close()
    return md5
