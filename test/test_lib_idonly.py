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
import unittest
import os.path

from test.utilities import load_config_data, load_df_from_txt
from test.utilities import print_groups, single_column_df_equal
from enrich2.libraries.idonly import IdOnlySeqLib


# -------------------------------------------------------------------------- #
#
#                           UTILTIES
#
# -------------------------------------------------------------------------- #
CFG_PATH = "idonly/idonly.json"
READS_DIR = "data/reads/idonly"
RESULT_DIR = "idonly/"


def make_libarary(cfg, **kwargs):
    obj = IdOnlySeqLib()
    obj.force_recalculate = False
    obj.component_outliers = False
    obj.scoring_method = 'counts'
    obj.logr_method = 'wt'
    obj.plots_requested = False
    obj.tsv_requested = False
    obj.output_dir_override = False

    # perform the analysis
    obj.configure(cfg)
    obj.validate()
    obj.store_open(children=True)
    obj.calculate()

    for k, v in kwargs.items():
        setattr(obj, k, v)
    return obj


class HDF5Verifier(object):

    def __call__(self, test_class, file_prefix, sep=';'):
        self.test_class = test_class
        self.prefix = file_prefix
        self.sep = sep
        self.test_serialize()
        self.test_main_identifiers_counts()
        self.test_raw_identifiers_counts()

    def test_main_identifiers_counts(self):
        expected = load_df_from_txt(
            '{}/{}_main_identifiers_counts.tsv'.format(
                RESULT_DIR, self.prefix), sep=self.sep
        )
        result = self.test_class.store['/main/identifiers/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_raw_identifiers_counts(self):
        expected = load_df_from_txt(
            '{}/{}_raw_identifiers_counts.tsv'.format(
                RESULT_DIR, self.prefix), sep=self.sep
        )
        result = self.test_class.store['/raw/identifiers/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_serialize(self):
        cfg = self.test_class._obj.serialize()
        self.test_class.assertTrue(self.test_class._cfg == cfg)


# -------------------------------------------------------------------------- #
#
#                          Counts Only Mode No Filter
#
# -------------------------------------------------------------------------- #
class TestIdonlySeqLibCountsOnlyModeNoFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'counts_only'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['counts file'] = "{}/{}".format(
            READS_DIR ,'{}.tsv'.format(cls._prefix))
        cls._obj = make_libarary(cls._cfg)

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    @property
    def store(self):
        return self._obj.store

    def test_main(self):
        driver = HDF5Verifier()
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                      Barcode Min Count Filter
#
# -------------------------------------------------------------------------- #
class TestIdonlySeqLibCountsWithIdentifiersMinCountSetting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'identifiers_mincount'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['counts file'] = "{}/{}".format(
            READS_DIR , '{}.tsv'.format(cls._prefix))
        cls._cfg['identifiers']['min count'] = 2
        cls._obj = make_libarary(cls._cfg)

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    @property
    def store(self):
        return self._obj.store

    def test_main(self):
        driver = HDF5Verifier()
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                                   MAIN
#
# -------------------------------------------------------------------------- #
if __name__ == "__main__":
    unittest.main()
