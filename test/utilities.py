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

def create_file_path(fname, direc='data/result/'):
    path = os.path.join(os.path.dirname(__file__), direc, fname)
    return path


def load_config_data(fname, direc='data/config/'):
    path = create_file_path(fname, direc)
    try:
        with open(path, "rt") as fp:
            return json.load(fp)
    except (IOError, ValueError):
        raise IOError("Failed to open '{}".format(path))


def load_fastq_data(fname, direc='data/reads/'):
    path = create_file_path(fname, direc)
    try:
        with open(path, "rt") as fp:
            yield fp
    except IOError:
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


def single_column_df_equal(df1, df2):
    index_eq = [x for x in df1.index == df2.index]
    values_eq = [x[0] for x in df1.values == df2.values]
    return all(values_eq) and all(index_eq)


def save_result_to_txt(test_obj, direc, prefix, sep='\t'):
    for key in test_obj.store:
        name = "{}/{}_{}.tsv".format(
            direc,
            prefix,
            key[1:].replace("/", "_")
        )
        print("saving {} to {}".format(key, name))
        test_obj.store[key].to_csv(name, sep=sep, index=True)
    return


def save_result_to_pkl(test_obj, direc, prefix):
    for key in test_obj.store:
        name = "{}/{}_{}.pkl".format(
            direc,
            prefix,
            key[1:].replace("/", "_")
        )
        print("saving {} to {}".format(key, name))
        test_obj.store[key].to_pickle(name)
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


def print_test(test_name, expected, result):
    print("")
    print("-" * 60)
    print(test_name)
    print("-" * 60)
    print("-" * 26 + "EXPECTED" + "-" * 26)
    print(expected)
    print("-" * 28 + "END" + "-" * 29)
    print("-" * 27 + "RESULT" + "-" * 27)
    print(result)
    print("-" * 28 + "END" + "-" * 29)
    print("")
    return


DEFAULT_STORE_PARAMS = {
    'force_recalculate': False,
    'component_outliers': False,
    'scoring_method': 'counts',
    'logr_method': 'wt',
    'plots_requested': False,
    'tsv_requested': False,
    'output_dir_override': False
}