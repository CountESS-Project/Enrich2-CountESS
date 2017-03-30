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
from enrich2.stores.selection import Selection

# --------------------------------------------------------------------------- #
#
#                           NONCODING SELECTION
#
# --------------------------------------------------------------------------- #
class TestCodingSelection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cfg = load_config_data("selection/polyA_coding.json")
        cls._obj = Selection()

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


    def test_variant_counts_sorted(self):
        # order in h5 matters
        expected = load_result_df(
            "selection/polyA_coding_variant_counts.tsv",
            sep='\t'
        ).astype(np.float64)
        result = self._obj.store['/main/variants/counts']
        self.assertTrue(expected.equals(result))

    def test_variant_counts_unsorted(self):
        expected = load_result_df(
            "selection/polyA_coding_variant_counts.tsv",
            sep='\t'
        ).astype(np.float64)
        result = self._obj.store['/main/variants/counts'].sort_index()
        self.assertTrue(expected.equals(result))

    def test_synonymous_counts_sorted(self):
        expected = load_result_df(
            "selection/polyA_coding_synonymous_counts.tsv",
            sep='\t'
        ).astype(np.float64)
        result = self._obj.store['/main/synonymous/counts']
        self.assertTrue(expected.equals(result))


    def test_synonymous_counts_unsorted(self):
        expected = load_result_df(
            "selection/polyA_coding_synonymous_counts.tsv",
            sep='\t'
        ).astype(np.float64)
        result = self._obj.store['/main/synonymous/counts'].sort_index()
        self.assertTrue(expected.equals(result))


# -------------------------------------------------------------------------- #
#
#                                   MAIN
#
# -------------------------------------------------------------------------- #
def suite():
    s = unittest.TestSuite()
    s.addTest(TestCodingSelection)
    return s

if __name__ == "__main__":
    unittest.main()
