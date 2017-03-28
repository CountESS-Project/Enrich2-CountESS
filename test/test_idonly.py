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
import numpy as np

from test.utilities import load_result_df, load_config_data
from enrich2.libraries.idonly import IdOnlySeqLib

# --------------------------------------------------------------------------- #
#
#                        TEST THE CODING SELECTION
#
# --------------------------------------------------------------------------- #
class TestIdonlyCounts(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cfg = load_config_data("idonly_config.json")
        cls._obj = IdOnlySeqLib()

        # set analysis options
        cls._obj.force_recalculate = False
        cls._obj.component_outliers = False
        cls._obj.scoring_method = 'counts'
        cls._obj.logr_method = 'wt'
        cls._obj.plots_requested = False
        cls._obj.tsv_requested = False
        cls._obj.output_dir_override = False

        # perform the analysis
        cls._obj.configure(cfg)
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
        expected = load_result_df("idonly_counts.tsv", sep='\t')
        result = self._obj.store['/main/identifiers/counts']
        self.assertTrue(expected.equals(result))

        expected = load_result_df("multi_barcode_count.tsv", sep='\t')
        result = self._obj.store['/raw/identifiers/counts']
        self.assertTrue(expected.equals(result))

    def test_multi_barcode_counts_unsorted(self):
        # order in h5 doesn't matter
        result = self._obj.store['/main/identifiers/counts'].sort_index()
        expected = load_result_df("idonly_counts.tsv", sep='\t')
        self.assertTrue(expected.equals(result))

        expected = load_result_df("multi_barcode_count.tsv", sep='\t')
        result = self._obj.store['/raw/identifiers/counts'].sort_index()
        self.assertTrue(expected.equals(result))

    def test_serialize(self):
        cfg = load_config_data("idonly_config.json")
        result = self._obj.serialize()
        self.assertTrue(cfg == result)

# --------------------------------------------------------------------------- #
#
#                                   MAIN
#
# --------------------------------------------------------------------------- #
def suite():
    s = unittest.TestSuite()
    s.addTest(TestIdonlyCounts)
    return s

if __name__ == "__main__":
    unittest.main()
