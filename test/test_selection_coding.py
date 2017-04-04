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
import shutil
import unittest
import numpy as np
from itertools import product
from copy import deepcopy

from test.utilities import load_result_df, load_config_data, print_groups
from enrich2.stores.selection import Selection

CFG_PATH = "data/config/selection/"
READS_DIR = "data/reads/selection/"
RESULT_DIR = "data/result/selection/"

DEFAULT = {
    'force_recalculate': False,
    'component_outliers': False,
    'scoring_method': 'counts',
    'logr_method': 'wt',
    'plots_requested': False,
    'tsv_requested': False,
    'output_dir_override': False
}


# -------------------------------------------------------------------------- #
#
#                                   UTILITIES
#
# -------------------------------------------------------------------------- #
class GeneralTestCase(unittest.TestCase):

    def __init__(self, methodName, cfg, params,
                 coding_prefix=None, file_prefix=None):
        super(GeneralTestCase, self).__init__(methodName)
        self.coding_prefix = coding_prefix
        self.file_prefix = file_prefix
        self.cfg = cfg
        self.params = params

    def __str__(self):
        return "%s (%s)" % (self._testMethodName, self.__name__)

    def setUp(self):
        obj = Selection()
        obj.force_recalculate = self.params['force_recalculate']
        obj.component_outliers = self.params['component_outliers']
        obj.scoring_method = self.params['scoring_method']
        obj.logr_method = self.params['logr_method']
        obj.plots_requested = self.params['plots_requested']
        obj.tsv_requested = self.params['tsv_requested']
        obj.output_dir_override = self.params['output_dir_override']

        # perform the analysis
        obj.configure(self.cfg)
        obj.validate()
        obj.store_open(children=True)
        obj.calculate()
        self.obj = obj

    def tearDown(self):
        self.obj.store_close(children=True)
        os.remove(self.obj.store_path)
        shutil.rmtree(self.obj.output_dir)

    def runTest(self):
        # print_groups(self.obj.store)
        if self.coding_prefix == 'c':
            pass
            self.test_main_synonymous_counts()
            self.test_main_synonymous_counts_unfiltered()
            if self.obj.scoring_method not in set(['counts']):
                self.test_main_synonymous_scores()
            if self.obj.scoring_method in set(['WLS', 'OLS']):
                self.test_main_synonymous_log_ratios()
            if self.obj.scoring_method in set(['WLS']):
                self.test_main_synonymous_weights()

        self.test_main_variants_counts()
        self.test_main_variants_counts_unfiltered()
        if self.obj.scoring_method not in set(['counts']):
            self.test_main_variants_scores()
        if self.obj.scoring_method in set(['WLS', 'OLS']):
            self.test_main_variants_log_ratios()
        if self.obj.scoring_method in set(['WLS']):
            self.test_main_variants_weights()

    def test_main_synonymous_counts(self):
        expected = load_result_df(
            "{}_{}_main_synonymous_counts.tsv".format(
                self.coding_prefix, self.file_prefix),
            RESULT_DIR, sep='\t'
        ).astype(np.float32)
        result = self.obj.store[
            "/main/synonymous/counts"
        ].astype(np.float32)
        self.assertTrue(np.isclose(expected, result, equal_nan=True).all())

    def test_main_synonymous_counts_unfiltered(self):
        expected = load_result_df(
            "{}_{}_main_synonymous_counts_unfiltered.tsv".format(
                self.coding_prefix, self.file_prefix),
            RESULT_DIR, sep='\t'
        ).astype(np.float32)
        result = self.obj.store[
            "/main/synonymous/counts_unfiltered"
        ].astype(np.float32)
        self.assertTrue(np.isclose(expected, result, equal_nan=True).all())

    def test_main_synonymous_log_ratios(self):
        expected = load_result_df(
            "{}_{}_main_synonymous_log_ratios.tsv".format(
                self.coding_prefix, self.file_prefix),
            RESULT_DIR, sep='\t'
        ).astype(np.float32)
        result = self.obj.store[
            "/main/synonymous/log_ratios"
        ].astype(np.float32)
        self.assertTrue(np.isclose(expected, result, equal_nan=True).all())

    def test_main_synonymous_scores(self):
        expected = load_result_df(
            "{}_{}_main_synonymous_scores.tsv".format(
                self.coding_prefix, self.file_prefix),
            RESULT_DIR, sep='\t'
        ).astype(np.float32)
        result = self.obj.store[
            "/main/synonymous/scores"
        ].astype(np.float32)
        self.assertTrue(np.isclose(expected, result, equal_nan=True).all())

    def test_main_synonymous_weights(self):
        expected = load_result_df(
            "{}_{}_main_synonymous_weights.tsv".format(
                self.coding_prefix, self.file_prefix),
            RESULT_DIR, sep='\t'
        ).astype(np.float32)
        result = self.obj.store[
            "/main/synonymous/weights"
        ].astype(np.float32)
        self.assertTrue(np.isclose(expected, result, equal_nan=True).all())

    def test_main_variants_counts(self):
        expected = load_result_df(
            "{}_{}_main_variants_counts.tsv".format(
                self.coding_prefix, self.file_prefix),
            RESULT_DIR, sep='\t'
        ).astype(np.float32)
        result = self.obj.store[
            "/main/variants/counts"
        ].astype(np.float32)
        self.assertTrue(np.isclose(expected, result, equal_nan=True).all())

    def test_main_variants_counts_unfiltered(self):
        expected = load_result_df(
            "{}_{}_main_variants_counts_unfiltered.tsv".format(
                self.coding_prefix, self.file_prefix),
            RESULT_DIR, sep='\t'
        ).astype(np.float32)
        result = self.obj.store[
            "/main/variants/counts_unfiltered"
        ].astype(np.float32)
        self.assertTrue(np.isclose(expected, result, equal_nan=True).all())

    def test_main_variants_log_ratios(self):
        expected = load_result_df(
            "{}_{}_main_variants_log_ratios.tsv".format(
                self.coding_prefix, self.file_prefix),
            RESULT_DIR, sep='\t'
        ).astype(np.float32)
        result = self.obj.store[
            "/main/variants/log_ratios"
        ].astype(np.float32)
        self.assertTrue(np.isclose(expected, result, equal_nan=True).all())

    def test_main_variants_scores(self):
        expected = load_result_df(
            "{}_{}_main_variants_scores.tsv".format(
                self.coding_prefix, self.file_prefix),
            RESULT_DIR, sep='\t'
        ).astype(np.float32)
        result = self.obj.store[
            "/main/variants/scores"
        ].astype(np.float32)
        self.assertTrue(np.isclose(expected, result, equal_nan=True).all())

    def test_main_variants_weights(self):
        expected = load_result_df(
            "{}_{}_main_variants_weights.tsv".format(
                self.coding_prefix, self.file_prefix),
            RESULT_DIR, sep='\t'
        ).astype(np.float32)
        result = self.obj.store[
            "/main/variants/weights"
        ].astype(np.float32)
        self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


# -------------------------------------------------------------------------- #
#
#                                   MAIN
#
# -------------------------------------------------------------------------- #
if __name__ == "__main__":

    suite = unittest.TestSuite()
    scoring_methods = ['WLS', 'OLS', 'ratios', 'counts', 'simple']
    logr_methods = ['wt', 'complete', 'full']
    coding_prefixes = ['c', 'n']
    cfg_map = {'c': 'polyA_coding.json', 'n':'polyA_noncoding.json'}

    # Add combinations of scoring methods with normalization methods
    for (s, l, p) in product(scoring_methods, logr_methods, coding_prefixes):
        params = deepcopy(DEFAULT)
        params['scoring_method'] = s
        params['logr_method'] = l
        cfg = load_config_data(cfg_map[p], CFG_PATH)
        driver_name = "runTest"
        class_name = "TestSelection{}{}{}".format(s, l, p.upper())
        test_case = GeneralTestCase(
            methodName=driver_name,
            cfg=cfg,
            params=params,
            coding_prefix=p,
            file_prefix='{}_{}'.format(s, l)
        )
        test_case.__name__ = class_name
        suite.addTest(test_case)

    # Add timpoint merging tests
    for p in coding_prefixes:
        params = deepcopy(DEFAULT)
        params['scoring_method'] = 'counts'
        params['logr_method'] = 'wt'
        cfg = load_config_data(cfg_map[p].replace('.', '_merge.'), CFG_PATH)
        driver_name = "runTest"
        class_name = "TestSelectionMergeTimepoints{}".format(p.upper())
        test_case = GeneralTestCase(
            methodName=driver_name,
            cfg=cfg,
            params=params,
            coding_prefix=p,
            file_prefix='merge_timepoints'
        )
        test_case.__name__ = class_name
        suite.addTest(test_case)

    # Run suite
    runner = unittest.TextTestRunner()
    runner.run(suite)
