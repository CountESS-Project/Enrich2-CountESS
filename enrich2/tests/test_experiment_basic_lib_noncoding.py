import unittest
from copy import deepcopy

from ..experiment.experiment import Experiment
from .methods import HDF5TestComponent
from .utilities import DEFAULT_STORE_PARAMS
from .utilities import load_config_data, update_cfg_file

CFG_FILE = "basic_experiment_noncoding.json"
CFG_DIR = "data/config/experiment/"
READS_DIR = "data/reads/experiment/"
RESULT_DIR = "data/result/experiment/"

DRIVER = "runTest"
LIBTYPE = "basic"
CODING_STR = "n"
FILE_EXT = "tsv"
FILE_SEP = "\t"


class TestExperimentBasicLibWLSScoringCompleteNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "WLS"
        logr = "complete"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibWLSScoringFullNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "WLS"
        logr = "full"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibWLSScoringWTNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "WLS"
        logr = "wt"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibOLSScoringCompleteNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "OLS"
        logr = "complete"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibOLSScoringFullNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "OLS"
        logr = "full"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibOLSScoringWTNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "OLS"
        logr = "wt"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibRatiosScoringCompleteNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "ratios"
        logr = "complete"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibRatiosScoringFullNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "ratios"
        logr = "full"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibRatiosScoringWTNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "ratios"
        logr = "wt"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibCountsScoringCompleteNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "counts"
        logr = "complete"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibCountsScoringFullNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "counts"
        logr = "full"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibCountsScoringWTNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "counts"
        logr = "wt"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibSimpleScoringCompleteNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "simple"
        logr = "complete"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibSimpleScoringFullNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "simple"
        logr = "full"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibSimpleScoringWTNormNC(unittest.TestCase):
    def setUp(self):
        scoring = "simple"
        logr = "wt"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg = update_cfg_file(cfg, scoring, logr)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        self.general_test_component = HDF5TestComponent(
            store_constructor=Experiment,
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
            coding="noncoding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


if __name__ == "__main__":
    unittest.main()
