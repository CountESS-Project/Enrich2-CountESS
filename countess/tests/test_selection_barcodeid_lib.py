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
LIBTYPE = "barcodeid"
FILE_EXT = "tsv"
FILE_SEP = "\t"


class TestSelectionBarcodeidLibWLSScoringCompleteNorm(unittest.TestCase):
    def setUp(self):
        scoring = "WLS"
        logr = "complete"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            params=params,
            verbose=False,
            libtype=LIBTYPE,
            scoring_method=scoring,
            logr_method=logr,
            coding="",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarcodeidLibWLSScoringFullNorm(unittest.TestCase):
    def setUp(self):
        scoring = "WLS"
        logr = "full"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            params=params,
            verbose=False,
            libtype=LIBTYPE,
            scoring_method=scoring,
            logr_method=logr,
            coding="",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarcodeidLibOLSScoringCompleteNorm(unittest.TestCase):
    def setUp(self):
        scoring = "OLS"
        logr = "complete"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            params=params,
            verbose=False,
            libtype=LIBTYPE,
            scoring_method=scoring,
            logr_method=logr,
            coding="",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarcodeidLibOLSScoringFullNorm(unittest.TestCase):
    def setUp(self):
        scoring = "OLS"
        logr = "full"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            params=params,
            verbose=False,
            libtype=LIBTYPE,
            scoring_method=scoring,
            logr_method=logr,
            coding="",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarcodeidLibRatiosScoringCompleteNorm(unittest.TestCase):
    def setUp(self):
        scoring = "ratios"
        logr = "complete"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            params=params,
            verbose=False,
            libtype=LIBTYPE,
            scoring_method=scoring,
            logr_method=logr,
            coding="",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarcodeidLibRatiosScoringFullNorm(unittest.TestCase):
    def setUp(self):
        scoring = "ratios"
        logr = "full"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            params=params,
            verbose=False,
            libtype=LIBTYPE,
            scoring_method=scoring,
            logr_method=logr,
            coding="",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarcodeidLibCountsScoringCompleteNorm(unittest.TestCase):
    def setUp(self):
        scoring = "counts"
        logr = "complete"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            params=params,
            verbose=False,
            libtype=LIBTYPE,
            scoring_method=scoring,
            logr_method=logr,
            coding="",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarcodeidLibCountsScoringFullNorm(unittest.TestCase):
    def setUp(self):
        scoring = "counts"
        logr = "full"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            params=params,
            verbose=False,
            libtype=LIBTYPE,
            scoring_method=scoring,
            logr_method=logr,
            coding="",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarcodeidLibSimpleScoringCompleteNorm(unittest.TestCase):
    def setUp(self):
        scoring = "simple"
        logr = "complete"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            params=params,
            verbose=False,
            libtype=LIBTYPE,
            scoring_method=scoring,
            logr_method=logr,
            coding="",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestSelectionBarcodeidLibSimpleScoringFullNorm(unittest.TestCase):
    def setUp(self):
        scoring = "simple"
        logr = "full"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)

        self.general_test_component = HDF5TestComponent(
            store_constructor=Selection,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            params=params,
            verbose=False,
            libtype=LIBTYPE,
            scoring_method=scoring,
            logr_method=logr,
            coding="",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


if __name__ == "__main__":
    unittest.main()
