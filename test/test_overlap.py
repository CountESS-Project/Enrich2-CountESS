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

from test.utilities import load_config_data, load_result_df
from test.utilities import single_column_df_equal, print_groups
from enrich2.libraries.overlap import OverlapSeqLib


# -------------------------------------------------------------------------- #
#
#                           GENERAIC TEST DRIVER
#
# -------------------------------------------------------------------------- #
class HDF5Verifier(object):

    def __call__(self, test_class, file_prefix, coding_prefix, sep=';'):
        self.test_class = test_class
        self.file_prefix = file_prefix
        self.coding_prefix = coding_prefix
        self.prefix = "{}_{}".format(coding_prefix, file_prefix)
        self.sep = sep
        self.test_filter_stats()
        if coding_prefix == 'c':
            self.test_main_syn_count()
        self.test_main_variant_count()
        self.test_raw_variant_count()

    def test_main_variant_count(self):
        expected = load_result_df(
            'overlap/{}_main_variants_count.tsv'.format(self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/main/variants/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_raw_variant_count(self):
        expected = load_result_df(
            'overlap/{}_raw_variants_count.tsv'.format(self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/raw/variants/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_filter_stats(self):
        expected = load_result_df(
            'overlap/{}_stats.tsv'.format(self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/raw/filter']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_main_syn_count(self):
        expected = load_result_df(
            'overlap/{}_main_syn_count.tsv'.format(self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/main/synonymous/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))


# -------------------------------------------------------------------------- #
#
#                           INTEGRATION COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestOverlapSeqLibCountsIntegrated(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("overlap/overlap_coding.json")
        cls._cfg['fastq']['forward reads'] = 'data/reads/overlap/fwd_test.fq'
        cls._cfg['fastq']['reverse reads'] = 'data/reads/overlap/rev_test.fq'

        cls._obj = OverlapSeqLib()

        # set analysis options
        cls._obj.force_recalculate = False
        cls._obj.component_outliers = False
        cls._obj.scoring_method = 'counts'
        cls._obj.logr_method = 'wt'
        cls._obj.plots_requested = False
        cls._obj.tsv_requested = False
        cls._obj.output_dir_override = False

        # perform the analysis
        cls._obj.configure(cls._cfg)
        cls._obj.validate()
        cls._obj.store_open(children=True)
        cls._obj.calculate()

        print_groups(cls._obj.store)

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
        # driver(self, coding_prefix='c', file_prefix='integrated', sep=';')


# -------------------------------------------------------------------------- #
#
#                                   MAIN
#
# -------------------------------------------------------------------------- #
if __name__ == "__main__":
    unittest.main()