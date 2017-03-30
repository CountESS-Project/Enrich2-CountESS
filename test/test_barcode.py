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
import pandas as pd
import numpy as np
import os.path

from test.utilities import load_config_data, load_result_df
from enrich2.libraries.barcode import BarcodeSeqLib


# --------------------------------------------------------------------------- #
#
#                           BARCODE COUNT TESTING
#
# --------------------------------------------------------------------------- #
class TestBarcodeSeqLibCounts(unittest.TestCase):
    """
    The purpose of this class is to test if Fastq reads from a file are
    being counted correctly.
    """

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("barcode/barcode.json")
        cls._obj = BarcodeSeqLib()

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

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    def test_multi_barcode_counts(self):
        # order in h5 matters
        expected = load_result_df("barcode/barcode_raw_count.tsv", sep='\t')
        expected = expected.astype(np.int32)
        result = self._obj.store['/raw/barcodes/counts']
        self.assertTrue(expected.equals(result))

        expected = load_result_df("barcode/barcode_main_count.tsv", sep='\t')
        expected = expected.astype(np.int32)
        result = self._obj.store['/main/barcodes/counts']
        self.assertTrue(expected.equals(result))

    def test_multi_barcode_counts_unsorted(self):
        # order in h5 doesn't matter
        result = self._obj.store['/raw/barcodes/counts'].sort_index()
        expected = load_result_df("barcode/barcode_raw_count.tsv", sep='\t')
        expected = expected.astype(np.int32)
        self.assertTrue(expected.equals(result))

        # order in h5 doesn't matter
        result = self._obj.store['/main/barcodes/counts'].sort_index()
        expected = load_result_df("barcode/barcode_main_count.tsv", sep='\t')
        expected = expected.astype(np.int32)
        self.assertTrue(expected.equals(result))

    def test_filter_stats(self):
        result = load_result_df("barcode/barcode_stats.tsv", sep=',')
        self.assertTrue(self._obj.store['/raw/filter'].equals(result))


# --------------------------------------------------------------------------- #
#
#                           BARCODE FILTER TESTING
#
# --------------------------------------------------------------------------- #
class TestBarcodeSeqLibFiltering(unittest.TestCase):
    """
    The purpose of this class is to test if Fastq reads from a file are
    being counted AND filtered correctly.
    """

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("barcode/barcode_filters.json")
        cls._obj = BarcodeSeqLib()

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

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    def test_multi_barcode_counts(self):
        # order in h5 matters
        expected = load_result_df(
            "barcode/barcode_filter_raw_count.tsv", sep='\t')
        expected = expected.astype(np.int32)
        result = self._obj.store['/raw/barcodes/counts']
        self.assertTrue(expected.equals(result))

        expected = load_result_df(
            "barcode/barcode_filter_main_count.tsv", sep='\t')
        expected = expected.astype(np.int32)
        result = self._obj.store['/main/barcodes/counts']
        self.assertTrue(expected.equals(result))

    def test_multi_barcode_counts_unsorted(self):
        # order in h5 doesn't matter
        result = self._obj.store['/raw/barcodes/counts'].sort_index()
        expected = load_result_df(
            "barcode/barcode_filter_raw_count.tsv", sep='\t')
        expected = expected.astype(np.int32)
        self.assertTrue(expected.equals(result))

        # order in h5 doesn't matter
        result = self._obj.store['/main/barcodes/counts'].sort_index()
        expected = load_result_df(
            "barcode/barcode_filter_main_count.tsv", sep='\t')
        expected = expected.astype(np.int32)
        self.assertTrue(expected.equals(result))

    def test_filter_stats(self):
        expected = load_result_df("barcode/barcode_filter_stats.tsv", sep=',')
        result = self._obj.store['/raw/filter']
        self.assertTrue(expected.equals(result))


# --------------------------------------------------------------------------- #
#
#                                   MAIN
#
# --------------------------------------------------------------------------- #
def suite():
    s = unittest.TestSuite()
    s.addTest(TestBarcodeSeqLibCounts)
    s.addTest(TestBarcodeSeqLibFiltering)
    return s

if __name__ == "__main__":
    unittest.main()
