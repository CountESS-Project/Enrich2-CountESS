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

import unittest
from copy import deepcopy

from ..selection.selection import Selection
from .methods import HDF5TestComponent
from .utilities import DEFAULT_STORE_PARAMS
from .utilities import load_config_data, create_file_path

CFG_FILE = "idonly_selection.json"
CFG_DIR = "data/config/selection/"
READS_DIR = "data/reads/selection/"
RESULT_DIR = "data/result/selection/"

DRIVER = "runTest"
LIBTYPE = 'idonly'
FILE_EXT = 'tsv'
FILE_SEP = '\t'

SAVE = False
VERBOSE = False


class TestSelectionIdOnlyLibWLSScoringCompleteNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'WLS'
        logr = 'complete'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        cfg["scorer"]["scorer_path"] = create_file_path(
            'regression_scorer.py', 'data/plugins/'
        )
        cfg["scorer"]["scorer_options"] = {
            'logr_method': logr,
            'weighted': True if scoring == 'WLS' else False
        }
        file_prefix = '{}_{}_{}'.format(LIBTYPE, scoring, logr)

        self.general_test_component = HDF5TestComponent(
            methodName=DRIVER,
            store_constructor=Selection,
            cfg=cfg,
            params=params,
            file_prefix=file_prefix,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            verbose=VERBOSE,
            save=SAVE
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionIdOnlyLibWLSScoringFullNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'WLS'
        logr = 'full'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        cfg["scorer"]["scorer_path"] = create_file_path(
            'regression_scorer.py', 'data/plugins/'
        )
        cfg["scorer"]["scorer_options"] = {
            'logr_method': logr,
            'weighted': True if scoring == 'WLS' else False
        }
        file_prefix = '{}_{}_{}'.format(LIBTYPE, scoring, logr)

        self.general_test_component = HDF5TestComponent(
            methodName=DRIVER,
            store_constructor=Selection,
            cfg=cfg,
            params=params,
            file_prefix=file_prefix,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            verbose=VERBOSE,
            save=SAVE
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionIdOnlyLibOLSScoringCompleteNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'OLS'
        logr = 'complete'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        cfg["scorer"]["scorer_path"] = create_file_path(
            'regression_scorer.py', 'data/plugins/'
        )
        cfg["scorer"]["scorer_options"] = {
            'logr_method': logr,
            'weighted': True if scoring == 'WLS' else False
        }
        file_prefix = '{}_{}_{}'.format(LIBTYPE, scoring, logr)

        self.general_test_component = HDF5TestComponent(
            methodName=DRIVER,
            store_constructor=Selection,
            cfg=cfg,
            params=params,
            file_prefix=file_prefix,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            verbose=VERBOSE,
            save=SAVE
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionIdOnlyLibOLSScoringFullNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'OLS'
        logr = 'full'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        cfg["scorer"]["scorer_path"] = create_file_path(
            'regression_scorer.py', 'data/plugins/'
        )
        cfg["scorer"]["scorer_options"] = {
            'logr_method': logr,
            'weighted': True if scoring == 'WLS' else False
        }
        file_prefix = '{}_{}_{}'.format(LIBTYPE, scoring, logr)

        self.general_test_component = HDF5TestComponent(
            methodName=DRIVER,
            store_constructor=Selection,
            cfg=cfg,
            params=params,
            file_prefix=file_prefix,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            verbose=VERBOSE,
            save=SAVE
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionIdOnlyLibRatiosScoringCompleteNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'ratios'
        logr = 'complete'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        cfg["scorer"]["scorer_path"] = create_file_path(
            'ratios_scorer.py', 'data/plugins/'
        )
        cfg["scorer"]["scorer_options"] = {
            'logr_method': logr
        }
        file_prefix = '{}_{}_{}'.format(LIBTYPE, scoring, logr)

        self.general_test_component = HDF5TestComponent(
            methodName=DRIVER,
            store_constructor=Selection,
            cfg=cfg,
            params=params,
            file_prefix=file_prefix,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            verbose=VERBOSE,
            save=SAVE
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionIdOnlyLibRatiosScoringFullNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'ratios'
        logr = 'full'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        cfg["scorer"]["scorer_path"] = create_file_path(
            'ratios_scorer.py', 'data/plugins/'
        )
        cfg["scorer"]["scorer_options"] = {
            'logr_method': logr
        }
        file_prefix = '{}_{}_{}'.format(LIBTYPE, scoring, logr)

        self.general_test_component = HDF5TestComponent(
            methodName=DRIVER,
            store_constructor=Selection,
            cfg=cfg,
            params=params,
            file_prefix=file_prefix,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            verbose=VERBOSE,
            save=SAVE
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionIdOnlyLibCountsScoringCompleteNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'counts'
        logr = 'complete'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        cfg["scorer"]["scorer_path"] = create_file_path(
            'counts_scorer.py', 'data/plugins/'
        )
        cfg["scorer"]["scorer_options"] = {}
        file_prefix = '{}_{}_{}'.format(LIBTYPE, scoring, logr)

        self.general_test_component = HDF5TestComponent(
            methodName=DRIVER,
            store_constructor=Selection,
            cfg=cfg,
            params=params,
            file_prefix=file_prefix,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            verbose=VERBOSE,
            save=SAVE
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionIdOnlyLibCountsScoringFullNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'counts'
        logr = 'full'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        cfg["scorer"]["scorer_path"] = create_file_path(
            'counts_scorer.py', 'data/plugins/'
        )
        cfg["scorer"]["scorer_options"] = {}
        file_prefix = '{}_{}_{}'.format(LIBTYPE, scoring, logr)

        self.general_test_component = HDF5TestComponent(
            methodName=DRIVER,
            store_constructor=Selection,
            cfg=cfg,
            params=params,
            file_prefix=file_prefix,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            verbose=VERBOSE,
            save=SAVE
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionIdOnlyLibSimpleScoringCompleteNorm(unittest.TestCase):
    def setUp(self):
        scoring = 'simple'
        logr = 'complete'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        cfg["scorer"]["scorer_path"] = create_file_path(
            'counts_scorer.py', 'data/plugins/'
        )
        cfg["scorer"]["scorer_options"] = {}
        file_prefix = '{}_{}_{}'.format(LIBTYPE, scoring, logr)

        self.general_test_component = HDF5TestComponent(
            methodName=DRIVER,
            store_constructor=Selection,
            cfg=cfg,
            params=params,
            file_prefix=file_prefix,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            verbose=VERBOSE,
            save=SAVE
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionIdOnlyLibSimpleScoringFullNorm(unittest.TestCase):
    def setUp(self):
        scoring = 'simple'
        logr = 'full'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        cfg["scorer"]["scorer_path"] = create_file_path(
            'counts_scorer.py', 'data/plugins/'
        )
        cfg["scorer"]["scorer_options"] = {}
        file_prefix = '{}_{}_{}'.format(LIBTYPE, scoring, logr)

        self.general_test_component = HDF5TestComponent(
            methodName=DRIVER,
            store_constructor=Selection,
            cfg=cfg,
            params=params,
            file_prefix=file_prefix,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            verbose=VERBOSE,
            save=SAVE
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


if __name__ == "__main__":
    unittest.main()
