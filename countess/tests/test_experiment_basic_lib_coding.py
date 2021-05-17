import unittest
from copy import deepcopy

from ..experiment.experiment import Experiment
from .methods import HDF5TestComponent
from .utilities import DEFAULT_STORE_PARAMS
from .utilities import load_config_data, update_cfg_file

CFG_FILE = "basic_experiment_coding.json"
CFG_DIR = "data/config/experiment/"
READS_DIR = "data/reads/experiment/"
RESULT_DIR = "data/result/experiment/"

DRIVER = "runTest"
LIBTYPE = "basic"
CODING_STR = "c"
FILE_EXT = "tsv"
FILE_SEP = "\t"


class TestExperimentBasicLibWLSScoringCompleteNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibWLSScoringFullNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibWLSScoringWTNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibOLSScoringCompleteNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibOLSScoringFullNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibOLSScoringWTNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibRatiosScoringCompleteNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibRatiosScoringFullNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibRatiosScoringWTNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibCountsScoringCompleteNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibCountsScoringFullNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibCountsScoringWTNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibSimpleScoringCompleteNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibSimpleScoringFullNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


class TestExperimentBasicLibSimpleScoringWTNormC(unittest.TestCase):
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
            coding="coding",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


if __name__ == "__main__":
    unittest.main()
