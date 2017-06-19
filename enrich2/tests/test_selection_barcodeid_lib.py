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
from .utilities import load_config_data
from .utilities import update_cfg_file

CFG_FILE = "barcodeid_selection.json"
CFG_DIR = "data/config/selection/"
READS_DIR = "data/reads/selection/"
RESULT_DIR = "data/result/selection/"

DRIVER = "runTest"
LIBTYPE = 'barcodeid'
FILE_EXT = 'tsv'
FILE_SEP = '\t'


class TestSelectionBarocdeidLibWLSScoringCompleteNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'WLS'
        logr = 'complete'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, params=params,
            verbose=False, libtype=LIBTYPE, scoring_method=scoring,
            logr_method=logr, coding='')
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarocdeidLibWLSScoringFullNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'WLS'
        logr = 'full'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, params=params,
            verbose=False, libtype=LIBTYPE, scoring_method=scoring,
            logr_method=logr, coding='')
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarocdeidLibOLSScoringCompleteNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'OLS'
        logr = 'complete'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, params=params,
            verbose=False, libtype=LIBTYPE, scoring_method=scoring,
            logr_method=logr, coding='')
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarocdeidLibOLSScoringFullNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'OLS'
        logr = 'full'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, params=params,
            verbose=False, libtype=LIBTYPE, scoring_method=scoring,
            logr_method=logr, coding='')
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarocdeidLibRatiosScoringCompleteNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'ratios'
        logr = 'complete'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, params=params,
            verbose=False, libtype=LIBTYPE, scoring_method=scoring,
            logr_method=logr, coding='')
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarocdeidLibRatiosScoringFullNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'ratios'
        logr = 'full'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, params=params,
            verbose=False, libtype=LIBTYPE, scoring_method=scoring,
            logr_method=logr, coding='')
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarocdeidLibCountsScoringCompleteNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'counts'
        logr = 'complete'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, params=params,
            verbose=False, libtype=LIBTYPE, scoring_method=scoring,
            logr_method=logr, coding='')
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarocdeidLibCountsScoringFullNorm(unittest.TestCase):

    def setUp(self):
        scoring = 'counts'
        logr = 'full'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, params=params,
            verbose=False, libtype=LIBTYPE, scoring_method=scoring,
            logr_method=logr, coding='')
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarocdeidLibSimpleScoringCompleteNorm(unittest.TestCase):
    def setUp(self):
        scoring = 'simple'
        logr = 'complete'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, params=params,
            verbose=False, libtype=LIBTYPE, scoring_method=scoring,
            logr_method=logr, coding='')
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarocdeidLibSimpleScoringFullNorm(unittest.TestCase):
    def setUp(self):
        scoring = 'simple'
        logr = 'full'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, params=params,
            verbose=False, libtype=LIBTYPE, scoring_method=scoring,
            logr_method=logr, coding='')
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


if __name__ == "__main__":
    unittest.main()
