"""
Enrich2 tests methods module
============================
Module consists of a class that automates HDF5 testing.
"""


import os
import shutil
import unittest
import numpy as np
import pandas as pd
import logging
import tempfile

from types import MethodType

from .utilities import DEFAULT_STORE_PARAMS, save_result_to_txt
from .utilities import dispatch_loader, save_result_to_pkl
from .utilities import print_test_comparison, create_file_path


__all__ = ["HDF5TestComponent", "TEST_METHODS"]


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
    store_constructor: :py:class:`~enrich2.base.StoreManager`
        Constructor for a StoreManager subclass.
    cfg : `dict`
        Config dictionary.
    params : `dict`
        Parameter dictionary for StoreManager.
    file_prefix : `str`
        Unique part of file that will be loaded during comparison.
    file_ext : `str`
        Extension of the result files that will be loaded during comparison.
    file_sep: `str`
        Delimited to use in the case of loading from text.
    save: `bool`
        Save computation results and do not perform any tests. Will override
        any previously saved results. Should only be used when tests must
        be updated to reflect core changes to computations rendering previous
        tests incorrect.
    verbose: bool
        True to print the test to terminal.
        
    Methods
    -------
    setUp
        Overrides :py:func:`unittest.TestCase.setUp`
    tearDown
        Overrides :py:func:`unittest.TestCase.tearDown`
    makeTests
        Initialize the test fixture with the appropriate test functions.
    runTests
        Runs the test class with dynamically loaded test functions.
    saveTests
        Save computation results and do not perform any tests. Will override
        any previously saved results. Should only be used when tests must
        be updated to reflect core changes to computations rendering previous
        tests incorrect.
    """

    def __init__(
        self,
        store_constructor=None,
        cfg=None,
        result_dir="",
        file_ext="",
        file_sep="\t",
        save=False,
        params=DEFAULT_STORE_PARAMS,
        verbose=False,
        libtype="",
        scoring_method="",
        logr_method="",
        coding="",
    ):
        super(HDF5TestComponent, self).__init__("runTest")

        self.file_ext = file_ext
        self.file_sep = file_sep
        self.cfg = cfg
        self.params = params
        self.store_constructor = store_constructor
        self.tests = []
        self.verbose = verbose
        self.save = save

        self.result_dir = result_dir
        if libtype:
            self.result_dir += "/{}/".format(libtype)
        if scoring_method:
            self.result_dir += "/{}/".format(scoring_method)
        if logr_method:
            self.result_dir += "/{}/".format(logr_method)
        if coding:
            self.result_dir += "/{}/".format(coding)

        if verbose:
            print("Working directory is: {}".format(self.result_dir))
            logging.getLogger().setLevel(logging.INFO)
            logging.captureWarnings(True)
        else:
            logging.getLogger().setLevel(logging.ERROR)
            logging.captureWarnings(False)

    def __str__(self):
        return "%s (%s)" % (self._testMethodName, self.__name__)

    def setUp(self):
        """
        Overrides :py:func:`unittest.TestCase.setUp`

        Returns
        -------
        None
        """
        obj = self.store_constructor()
        obj.force_recalculate = self.params["force_recalculate"]
        obj.component_outliers = self.params["component_outliers"]
        obj.tsv_requested = self.params["tsv_requested"]
        obj.output_dir_override = self.params["output_dir_override"]

        self.temp_dir = tempfile.mkdtemp()  # requires manual cleanup
        self.cfg["output directory"] = self.temp_dir

        obj.configure(self.cfg)
        obj.validate()

        # perform the analysis
        obj.store_open(children=True)
        obj.calculate()
        self.obj = obj

        if self.save:
            self.saveTests()
        else:
            self.makeTests()

    def tearDown(self):
        """
        Overrides :py:func:`unittest.TestCase.tearDown`

        Returns
        -------
        None
        """
        self.obj.store_close(children=True)
        os.remove(self.obj.store_path)
        shutil.rmtree(self.temp_dir)

    def makeTests(self):
        """
        Initialize the test fixture with the appropriate test functions.

        Returns
        -------
        None
        """
        for key in self.obj.store:
            test_func = TEST_METHODS[key]
            test_name = "test_{}".format(key.replace("/", "_")[1:])
            setattr(self, test_name, MethodType(test_func, self))
            self.tests.append(test_name)

    def runTest(self):
        """
        Runs the test class with dynamically loaded test functions.
        
        Returns
        -------
        None
        """
        for test_func_name in self.tests:
            getattr(self, test_func_name)()

    def saveTests(self):
        """
        Save computation results and do not perform any tests. Will override
        any previously saved results. Should only be used when tests must
        be updated to reflect core changes to computations rendering previous
        tests incorrect.
        
        Returns
        -------
        None

        """
        os.makedirs(create_file_path(self.result_dir, ""), exist_ok=True)
        if self.file_ext == "pkl":
            save_result_to_pkl(self.obj, self.result_dir)
        else:
            save_result_to_txt(self.obj, self.result_dir, self.file_sep)


# -------------------------------------------------------------------------- #
#
#                               VARIANTS
#
# -------------------------------------------------------------------------- #
def test_main_variants_scores_shared_full(self):
    key = "/main/variants/scores_shared_full"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_variants_scores_shared(self):
    key = "/main/variants/scores_shared"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_variants_scores_pvalues_wt(self):
    key = "/main/variants/scores_pvalues_wt"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_variants_scores(self):
    key = "/main/variants/scores"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_variants_weights(self):
    key = "/main/variants/weights"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_variants_log_ratios(self):
    key = "/main/variants/log_ratios"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_variants_counts(self):
    key = "/main/variants/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_variants_counts_unfiltered(self):
    key = "/main/variants/counts_unfiltered"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_raw_variants_counts(self):
    key = "/raw/variants/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)

    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


# -------------------------------------------------------------------------- #
#
#                            SYNONYMOUS
#
# -------------------------------------------------------------------------- #
def test_main_synonymous_scores_shared_full(self):
    key = "/main/synonymous/scores_shared_full"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_synonymous_scores_shared(self):
    key = "/main/synonymous/scores_shared"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_synonymous_scores_pvalues_wt(self):
    key = "/main/synonymous/scores_pvalues_wt"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_synonymous_scores(self):
    key = "/main/synonymous/scores"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_synonymous_weights(self):
    key = "/main/synonymous/weights"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_synonymous_log_ratios(self):
    key = "/main/synonymous/log_ratios"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_synonymous_counts(self):
    key = "/main/synonymous/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_synonymous_counts_unfiltered(self):
    key = "/main/synonymous/counts_unfiltered"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_raw_synonymous_counts(self):
    key = "/raw/synonymous/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


# -------------------------------------------------------------------------- #
#
#                               BARCODES
#
# -------------------------------------------------------------------------- #
def test_main_barcodes_scores_shared_full(self):
    key = "/main/barcodes/scores_shared_full"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_barcodes_scores_shared(self):
    key = "/main/barcodes/scores_shared"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_barcodes_scores_pvalues_wt(self):
    key = "/main/barcodes/scores_pvalues_wt"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_barcodes_scores(self):
    key = "/main/barcodes/scores"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)

    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_barcodes_weights(self):
    key = "/main/barcodes/weights"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_barcodes_log_ratios(self):
    key = "/main/barcodes/log_ratios"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_barcodes_counts(self):
    key = "/main/barcodes/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    self.assertTrue(expected.equals(result))


def test_main_barcodes_counts_unfiltered(self):
    key = "/main/barcodes/counts_unfiltered"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    self.assertTrue(expected.equals(result))


def test_raw_barcodes_counts(self):
    key = "/raw/barcodes/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    self.assertTrue(expected.equals(result))


def test_main_barcodemap(self):
    key = "/main/barcodemap"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep)
    result = self.obj.store[key]

    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    self.assertTrue(expected.equals(result))


def test_raw_barcodemap(self):
    key = "/raw/barcodemap"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(str)
    result = self.obj.store[key].astype(str)

    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    self.assertTrue(expected.equals(result))


# -------------------------------------------------------------------------- #
#
#                               IDENTIFIERS
#
# -------------------------------------------------------------------------- #
def test_main_identifiers_scores_shared_full(self):
    key = "/main/identifiers/scores_shared_full"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_identifiers_scores_shared(self):
    key = "/main/identifiers/scores_shared"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_identifiers_scores_pvalues_wt(self):
    key = "/main/identifiers/scores_pvalues_wt"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_identifiers_scores(self):
    key = "/main/identifiers/scores"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_identifiers_weights(self):
    key = "/main/identifiers/weights"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_identifiers_log_ratios(self):
    key = "/main/identifiers/log_ratios"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.float32)
    result = self.obj.store[key].astype(np.float32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_identifiers_counts(self):
    key = "/main/identifiers/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_main_identifiers_counts_unfiltered(self):
    key = "/main/identifiers/counts_unfiltered"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


def test_raw_identifiers_counts(self):
    key = "/raw/identifiers/counts"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)
    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
    pd.testing.assert_frame_equal(result, expected)


# -------------------------------------------------------------------------- #
#
#                               FILTER
#
# -------------------------------------------------------------------------- #
def test_raw_filter(self):
    key = "/raw/filter"
    file_suffix = key.replace("/", "_")[1:]
    fname = "{}.{}".format(file_suffix, self.file_ext)
    expected = dispatch_loader(fname, self.result_dir, self.file_sep).astype(np.int32)
    result = self.obj.store[key].astype(np.int32)

    if self.verbose:
        test_name = "test_{}".format(key.replace("/", "_")[1:])
        print(print_test_comparison(test_name, expected, result))
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
