"""
Enrich2 tests utils module
==========================
Module consists of assorted utility functions.
"""


import os
import json
import pandas as pd

from ..base.config_constants import SCORER, SCORER_OPTIONS, SCORER_PATH
from ..base.config_constants import FORCE_RECALCULATE, COMPONENT_OUTLIERS
from ..base.config_constants import TSV_REQUESTED, OUTPUT_DIR_OVERRIDE
from ..base.utils import multi_index_tsv_to_dataframe


TOP_LEVEL = os.path.dirname(__file__)
DEFAULT_STORE_PARAMS = {
    FORCE_RECALCULATE: False,
    COMPONENT_OUTLIERS: False,
    TSV_REQUESTED: False,
    OUTPUT_DIR_OVERRIDE: False,
}


__all__ = [
    "TOP_LEVEL",
    "DEFAULT_STORE_PARAMS",
    "create_file_path",
    "load_config_data",
    "load_df_from_pkl",
    "load_df_from_txt",
    "dispatch_loader",
    "update_cfg_file",
    "save_result_to_pkl",
    "save_result_to_txt",
    "print_test_comparison",
    "SCORING_ATTRS",
    "SCORING_PATHS",
]


def create_file_path(fname, direc="data/result/"):
    """
    Utility function to create an absolute path to data in the tests directory.
    
    Parameters
    ----------
    fname : `str`
        The name of the file.
    direc : `str`
        The directory of the file in tests directory.

    Returns
    -------
    `str`
        Absolute file path.

    """
    path = os.path.join(TOP_LEVEL, direc, fname)
    return path


def load_config_data(fname, direc="data/config/"):
    """
    Utility function to load a configuration file.
    
    Parameters
    ----------
    fname : `str`
        Name of file in the directory `direc`.
    direc : `str`, optional
        Directory where the file is relative to :py:mod:`~enrich2.tests`.

    Returns
    -------
    `dict`
        Dictionary containing the loaded key-value pairs.

    """
    path = create_file_path(fname, direc)
    try:
        with open(path, "rt") as fp:
            return json.load(fp)
    except (IOError, ValueError):
        raise IOError("Failed to open '{}".format(path))


def load_df_from_txt(fname, direc="data/result/", sep="\t"):
    """
    Utility function to load a table stored as txt with an arbitrary separator.
    
    Parameters
    ----------
    fname : `str`
        Name of file in the directory ``direc``.
    direc : `str`
        Directory where the file is relative to :py:mod:`~enrich2.tests`
    sep : `str`
        Delimiter to use between columns.
        
    Returns
    -------
    :py:class:`~pandas.DataFrame`
        A Pandas DataFrame object parsed from the file.
    """
    path = create_file_path(fname, direc)
    try:
        return multi_index_tsv_to_dataframe(path, sep, header_rows=None)
    except IOError:
        raise IOError("Failed to open '{}".format(path))


def load_df_from_pkl(fname, direc="data/result/"):
    """
    Utility function to load a table stored in py:module:`pickle` format.
    
    Parameters
    ----------
    fname : `str`
        Name of file in the directory ``direc``.
    direc : `str`
        Directory where the file is relative to :py:mod:`~enrich2.tests`.

    Returns
    -------
    :py:class:`~pandas.DataFrame`
        A Pandas DataFrame object parsed from the file.
    """
    path = create_file_path(fname, direc)
    try:
        return pd.read_pickle(path)
    except IOError:
        raise IOError("Failed to open '{}".format(path))


def save_result_to_txt(test_obj, direc, sep="\t"):
    """
    Utility function to save a :py:class:`~pd.HDFStore` as a series of 
    delimited tsv. One file is created for each :py:class:`~pd.DataFrame` in
    the store.
    
    Parameters
    ----------
    test_obj : :py:class:`~pd.HDFStore`
        HDFStore object to save to delimited text files.
    direc : `str`
        Directory to save the file.
    sep : `str`
        Delimiter to use between columns.

    Returns
    -------
    None
        This function does not return anything.

    """
    for key in test_obj.store:
        name = "{}/{}.tsv".format(direc, key[1:].replace("/", "_"))
        path = create_file_path(name, direc="")
        print("saving {} to {}".format(key, path))
        test_obj.store[key].to_csv(path, sep=sep, index=True, na_rep="NaN")
    return


def save_result_to_pkl(test_obj, direc):
    """
    Utility function to save a :py:class:`~pd.HDFStore` as a series of 
    pickle files. One file is created for each :py:class:`~pd.DataFrame` in
    the store. Each file has the extension 'pkl'.

    Parameters
    ----------
    test_obj : :py:class:`~pandas.DataFrame`
        HDFStore object to save to pickle files.
    direc : `str`
        Directory to save the file.

    Returns
    -------
    None
        This function does not return anything.

    """
    for key in test_obj.store:
        name = "{}/{}.pkl".format(direc, key[1:].replace("/", "_"))
        path = create_file_path(name, direc="")
        print("saving {} to {}".format(key, path))
        test_obj.store[key].to_pickle(path)
    return


def dispatch_loader(fname, direc, sep="\t"):
    """
    Utility function to load a filename based on the extension it has.
    
    Parameters
    ----------
    fname : `str` {'pkl', 'tsv', 'txt'}
        Filename with extension
    direc : `str`
        Directory to save the file.
    sep : `str`
        Delimiter to use between columns.

    Returns
    -------
    :py:class:`~pandas.DataFrame`
        DataFrame parsed from the file.
    """
    ext = fname.split(".")[-1]
    # print('Loading from: {}/{}'.format(direc, fname))
    if ext in ("tsv" or "txt"):
        return load_df_from_txt(fname, direc, sep)
    elif ext == "pkl":
        return load_df_from_pkl(fname, direc)
    else:
        raise IOError("Unexpected file extension {}.".format(ext))


def print_test_comparison(test_name, expected, result):
    """
    Utility function to nicely format the a test comparison as a string.
    
    Parameters
    ----------
    test_name : `str`
        Name of the test.
    expected : :py:class:`~pandas.DataFrame`
        Expected test result that can be represented as text
    result : :py:class:`~pandas.DataFrame`
        Expected test result that can be represented as text

    Returns
    -------
    `str`
        String object represeting a test.
    """
    line = "\n"
    line += "-" * 60 + "\n"
    line += "{}\n".format(test_name)
    line += "-" * 60 + "\n"
    line += "-" * 26 + "EXPECTED" + "-" * 26 + "\n"
    line += "{}\n".format(expected)
    line += "-" * 28 + "END" + "-" * 29 + "\n"
    line += "-" * 27 + "RESULT" + "-" * 27 + "\n"
    line += "{}\n".format(result)
    line += "-" * 28 + "END" + "-" * 29 + "\n"
    line += "\n"
    return line


def update_cfg_file(cfg, scoring, logr):
    """
    Utility function that takes a configuration dictionary and updates the
    scorer fields.
    
    Parameters
    ----------
    cfg : `dict`
        Dictionary that can initialize a 
        :py:class:`~enrich2.base.store.StoreManager` object.
    scoring : {'WLS', 'OLS', 'counts', 'ratios', 'simple'}
        Choice of scoring option
    logr : {'complete', 'full', 'wt'}
        Choice of scoring normalization method

    Returns
    -------
    `dict`
        Modified dictionary (in-place)

    """
    cfg[SCORER][SCORER_PATH] = SCORING_PATHS.get(scoring)
    cfg[SCORER][SCORER_OPTIONS] = SCORING_ATTRS.get(scoring).get(logr)
    return cfg


SCORING_PATHS = {
    "counts": create_file_path("counts_scorer.py", "data/plugins"),
    "ratios": create_file_path("ratios_scorer.py", "data/plugins"),
    "simple": create_file_path("simple_scorer.py", "data/plugins"),
    "WLS": create_file_path("regression_scorer.py", "data/plugins"),
    "OLS": create_file_path("regression_scorer.py", "data/plugins"),
}


SCORING_ATTRS = {
    "WLS": {
        "full": {"logr_method": "full", "weighted": True},
        "complete": {"logr_method": "complete", "weighted": True},
        "wt": {"logr_method": "wt", "weighted": True},
    },
    "OLS": {
        "full": {"logr_method": "full", "weighted": False},
        "complete": {"logr_method": "complete", "weighted": False},
        "wt": {"logr_method": "wt", "weighted": False},
    },
    "ratios": {
        "full": {"logr_method": "full"},
        "complete": {"logr_method": "complete"},
        "wt": {"logr_method": "wt"},
    },
    "counts": {"full": {}, "complete": {}, "wt": {}},
    "simple": {"full": {}, "complete": {}, "wt": {}},
}
