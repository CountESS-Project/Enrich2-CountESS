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

import os
import json
import pandas as pd

TOP_LEVEL = os.path.dirname(__file__)


def create_file_path(fname, direc='data/result/'):
    path = os.path.join(TOP_LEVEL, direc, fname)
    return path


def load_config_data(fname, direc='data/config/'):
    path = create_file_path(fname, direc)
    try:
        with open(path, "rt") as fp:
            return json.load(fp)
    except (IOError, ValueError):
        raise IOError("Failed to open '{}".format(path))


def load_df_from_txt(fname, direc='data/result/', sep='\t'):
    path = create_file_path(fname, direc)
    try:
        return pd.DataFrame.from_csv(path, sep=sep)
    except IOError:
        raise IOError("Failed to open '{}".format(path))


def load_df_from_pkl(fname, direc='data/result/'):
    path = create_file_path(fname, direc)
    try:
        return pd.read_pickle(path)
    except IOError:
        raise IOError("Failed to open '{}".format(path))


def save_result_to_txt(test_obj, direc, prefix, sep='\t'):
    for key in test_obj.store:
        name = "{}/{}_{}.tsv".format(
            direc,
            prefix,
            key[1:].replace("/", "_")
        )
        path = create_file_path(name, direc="")
        print("saving {} to {}".format(key, path))
        test_obj.store[key].to_csv(path, sep=sep, index=True)
    return


def save_result_to_pkl(test_obj, direc, prefix):
    for key in test_obj.store:
        name = "{}/{}_{}.pkl".format(
            direc,
            prefix,
            key[1:].replace("/", "_")
        )
        path = create_file_path(name, direc="")
        print("saving {} to {}".format(key, path))
        test_obj.store[key].to_pickle(path)
    return


def print_groups(store):
    for key in store:
        print("")
        print("-" * 60)
        print(' '*20 + key + ' '*40)
        print("-" * 60)
        print(store[key])
        print("-"*60)
        print("")
    return


def dispatch_loader(fname, direc, sep='\t'):
    ext = fname.split('.')[-1]
    if ext in ('tsv' or 'txt'):
        return load_df_from_txt(fname, direc, sep)
    elif ext == 'pkl':
        return load_df_from_pkl(fname, direc)
    else:
        raise ValueError("Unexpected file extension {}.".format(ext))


def str_test(test_name, expected, result):
    line = '\n'
    line += "-" * 60 + '\n'
    line += "{}\n".format(test_name)
    line += "-" * 60 + '\n'
    line += "-" * 26 + "EXPECTED" + "-" * 26 + '\n'
    line += "{}\n".format(expected)
    line += "-" * 28 + "END" + "-" * 29 + '\n'
    line += "-" * 27 + "RESULT" + "-" * 27 + '\n'
    line += "{}\n".format(result)
    line += "-" * 28 + "END" + "-" * 29 + '\n'
    line += '\n'
    return line


DEFAULT_STORE_PARAMS = {
    'force_recalculate': False,
    'component_outliers': False,
    'plots_requested': False,
    'tsv_requested': False,
    'output_dir_override': False,
    'scoring_class': '',
    'scoring_class_attrs': ''
}