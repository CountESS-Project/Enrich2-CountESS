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

from types import MethodType

from .utilities import DEFAULT_STORE_PARAMS, save_result_to_txt
from .utilities import dispatch_loader, save_result_to_pkl, str_test


# -------------------------------------------------------------------------- #
#
#                             TEST CLASS
#
# -------------------------------------------------------------------------- #

@unittest.skip("GenerealTestCase should not be run directly.")
class HDF5TestComponent(unittest.TestCase):
    """
    Utility class that builds a parameterized set of common tests. Allows
    customisation of the store manager class, coding/noncoding tests, and
    where to find the correct result files.

    Parameters
    ----------
    methodName : Test driver function. Should be 'runTest'.
    store_constructor: Constructor for a StoreManager subclass.
    cfg : Config dictionary.
    params : Parameter dictionary for StoreManager.
    file_prefix : Unique part of file name.

    """

    def __init__(self, methodName="runTest",
                 store_constructor=None, cfg=None, file_prefix="",
                 result_dir="", file_ext="", file_sep='\t', save=False,
                 params=DEFAULT_STORE_PARAMS, verbose=False):
        super(HDF5TestComponent, self).__init__(methodName)
        self.file_prefix = file_prefix
        self.result_dir = result_dir
        self.file_ext = file_ext
        self.file_sep = file_sep
        self.cfg = cfg
        self.params = params
        self.store_constructor = store_constructor
        self.tests = []
        self.verbose = verbose
        self.save = save

    def __str__(self):
        return "%s (%s)" % (self._testMethodName, self.__name__)

    def setUp(self):
        obj = self.store_constructor()
        obj.force_recalculate = self.params['force_recalculate']
        obj.component_outliers = self.params['component_outliers']
        obj.scoring_method = self.params['scoring_method']
        obj.logr_method = self.params['logr_method']
        obj.plots_requested = self.params['plots_requested']
        obj.tsv_requested = self.params['tsv_requested']
        obj.output_dir_override = self.params['output_dir_override']
        obj.scoring_class = self.params['scoring_class']
        obj.scoring_class_attrs = self.params['scoring_class_attrs']

        # perform the analysis
        obj.configure(self.cfg)
        obj.validate()
        obj.store_open(children=True)
        obj.calculate()
        self.obj = obj
        if self.save:
            self.saveToResult()
        self.makeTests()

    def makeTests(self):
        for key in self.obj.store:
            test_func = TEST_METHODS[key]
            test_name = "test_{}".format(key.replace("/", "_")[1:])
            setattr(self, test_name, MethodType(test_func, self))
            self.tests.append(test_name)

    def tearDown(self):
        self.obj.store_close(children=True)
        os.remove(self.obj.store_path)
        shutil.rmtree(self.obj.output_dir)

    def runTest(self):
        for test_func_name in self.tests:
            getattr(self, test_func_name)()

    def saveToResult(self):
        if self.file_ext == 'pkl':
            save_result_to_pkl(self.obj, self.result_dir, self.file_prefix)
        else:
            save_result_to_txt(self.obj, self.result_dir,
                               self.file_prefix, self.file_sep)


# -------------------------------------------------------------------------- #
#
#                               VARIANTS
#
# -------------------------------------------------------------------------- #
def test_main_variants_scores_shared_full(self):
    key = "/main/variants/scores_shared_full"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_variants_scores_shared(self):
    key = "/main/variants/scores_shared"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_variants_scores_pvalues_wt(self):
    key = "/main/variants/scores_pvalues_wt"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_variants_scores(self):
    key = "/main/variants/scores"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_variants_weights(self):
    key = "/main/variants/weights"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_variants_log_ratios(self):
    key = "/main/variants/log_ratios"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_variants_counts(self):
    key = "/main/variants/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_variants_counts_unfiltered(self):
    key = "/main/variants/counts_unfiltered"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_raw_variants_counts(self):
    key = "/raw/variants/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


# -------------------------------------------------------------------------- #
#
#                            SYNONYMOUS
#
# -------------------------------------------------------------------------- #
def test_main_synonymous_scores_shared_full(self):
    key = "/main/synonymous/scores_shared_full"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_synonymous_scores_shared(self):
    key = "/main/synonymous/scores_shared"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_synonymous_scores_pvalues_wt(self):
    key = "/main/synonymous/scores_pvalues_wt"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_synonymous_scores(self):
    key = "/main/synonymous/scores"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_synonymous_weights(self):
    key = "/main/synonymous/weights"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_synonymous_log_ratios(self):
    key = "/main/synonymous/log_ratios"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_synonymous_counts(self):
    key = "/main/synonymous/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_synonymous_counts_unfiltered(self):
    key = "/main/synonymous/counts_unfiltered"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_raw_synonymous_counts(self):
    key = "/raw/synonymous/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


# -------------------------------------------------------------------------- #
#
#                               BARCODES
#
# -------------------------------------------------------------------------- #
def test_main_barcodes_scores_shared_full(self):
    key = "/main/barcodes/scores_shared_full"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_barcodes_scores_shared(self):
    key = "/main/barcodes/scores_shared"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_barcodes_scores_pvalues_wt(self):
    key = "/main/barcodes/scores_pvalues_wt"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_barcodes_scores(self):
    key = "/main/barcodes/scores"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_barcodes_weights(self):
    key = "/main/barcodes/weights"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_barcodes_log_ratios(self):
    key = "/main/barcodes/log_ratios"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_barcodes_counts(self):
    key = "/main/barcodes/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(expected.equals(result))


def test_main_barcodes_counts_unfiltered(self):
    key = "/main/barcodes/counts_unfiltered"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(expected.equals(result))


def test_raw_barcodes_counts(self):
    key = "/raw/barcodes/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(expected.equals(result))


def test_main_barcodemap(self):
    key = "/main/barcodemap"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep)
    result = self.obj.store[key]
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(expected.equals(result))


def test_raw_barcodemap(self):
    key = "/raw/barcodemap"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep)
    result = self.obj.store[key]
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(expected.equals(result))


# -------------------------------------------------------------------------- #
#
#                               IDENTIFIERS
#
# -------------------------------------------------------------------------- #
def test_main_identifiers_scores_shared_full(self):
    key = "/main/identifiers/scores_shared_full"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_identifiers_scores_shared(self):
    key = "/main/identifiers/scores_shared"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_identifiers_scores_pvalues_wt(self):
    key = "/main/identifiers/scores_pvalues_wt"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_identifiers_scores(self):
    key = "/main/identifiers/scores"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_identifiers_weights(self):
    key = "/main/identifiers/weights"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_identifiers_log_ratios(self):
    key = "/main/identifiers/log_ratios"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_identifiers_counts(self):
    key = "/main/identifiers/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_main_identifiers_counts_unfiltered(self):
    key = "/main/identifiers/counts_unfiltered"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


def test_raw_identifiers_counts(self):
    key = "/raw/identifiers/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(np.isclose(expected, result, equal_nan=True).all())


# -------------------------------------------------------------------------- #
#
#                               FILTER
#
# -------------------------------------------------------------------------- #
def test_raw_filter(self):
    key = "/raw/filter"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}_{}.{}".format(
        self.file_prefix, file_suffix, self.file_ext)
    expected = dispatch_loader(
        fname, self.result_dir, self.file_sep)
    result = self.obj.store[key]
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(str_test(test_name, expected, result))
    self.assertTrue(expected.equals(result))


# -------------------------------------------------------------------------- #
#
#                               AVAILABLE
#
# -------------------------------------------------------------------------- #
TEST_METHODS = {
    "/main/variants/scores_shared_full": test_main_variants_scores_shared_full,
    "/main/variants/scores_shared": test_main_variants_scores_shared,
    "/main/variants/scores_pvalues_wt": test_main_variants_scores_pvalues_wt,
    "/main/variants/scores": test_main_variants_scores,
    "/main/variants/weights": test_main_variants_weights,
    "/main/variants/log_ratios": test_main_variants_log_ratios,
    "/main/variants/counts": test_main_variants_counts,
    "/main/variants/counts_unfiltered": test_main_variants_counts_unfiltered,
    "/raw/variants/counts": test_raw_variants_counts,

    "/main/synonymous/scores_shared_full": test_main_synonymous_scores_shared_full,
    "/main/synonymous/scores_shared": test_main_synonymous_scores_shared,
    "/main/synonymous/scores_pvalues_wt": test_main_synonymous_scores_pvalues_wt,
    "/main/synonymous/scores": test_main_synonymous_scores,
    "/main/synonymous/weights": test_main_synonymous_weights,
    "/main/synonymous/log_ratios": test_main_synonymous_log_ratios,
    "/main/synonymous/counts": test_main_synonymous_counts,
    "/main/synonymous/counts_unfiltered": test_main_synonymous_counts_unfiltered,
    "/raw/synonymous/counts": test_raw_synonymous_counts,

    "/main/barcodes/scores_shared_full": test_main_barcodes_scores_shared_full,
    "/main/barcodes/scores_shared": test_main_barcodes_scores_shared,
    "/main/barcodes/scores_pvalues_wt": test_main_barcodes_scores_pvalues_wt,
    "/main/barcodes/scores": test_main_barcodes_scores,
    "/main/barcodes/weights": test_main_barcodes_weights,
    "/main/barcodes/log_ratios": test_main_barcodes_log_ratios,
    "/main/barcodes/counts": test_main_barcodes_counts,
    "/main/barcodes/counts_unfiltered": test_main_barcodes_counts_unfiltered,
    "/main/barcodemap": test_main_barcodemap,
    "/raw/barcodemap": test_raw_barcodemap,
    "/raw/barcodes/counts": test_raw_barcodes_counts,

    "/main/identifiers/scores_shared_full": test_main_identifiers_scores_shared_full,
    "/main/identifiers/scores_shared": test_main_identifiers_scores_shared,
    "/main/identifiers/scores_pvalues_wt": test_main_identifiers_scores_pvalues_wt,
    "/main/identifiers/scores": test_main_identifiers_scores,
    "/main/identifiers/weights": test_main_identifiers_weights,
    "/main/identifiers/log_ratios": test_main_identifiers_log_ratios,
    "/main/identifiers/counts": test_main_identifiers_counts,
    "/main/identifiers/counts_unfiltered": test_main_identifiers_counts_unfiltered,
    "/raw/identifiers/counts": test_raw_identifiers_counts,

    "/raw/filter": test_raw_filter,
}