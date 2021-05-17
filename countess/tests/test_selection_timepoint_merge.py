import unittest
from copy import deepcopy

from ..selection.selection import Selection
from .methods import HDF5TestComponent
from .utilities import DEFAULT_STORE_PARAMS
from .utilities import load_config_data, update_cfg_file

CFG_FILE = "selection_timepoint_merge.json"
CFG_DIR = "data/config/selection/"
READS_DIR = "data/reads/selection/"
RESULT_DIR = "data/result/selection/"

DRIVER = "runTest"
LIBTYPE = "barcode"
FILE_EXT = "tsv"
FILE_SEP = "\t"


class TestSelectionTimepointMerge(unittest.TestCase):
    def setUp(self):
        scoring = "counts"
        logr = "wt"
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
            scoring_method="timepoint_merge",
            logr_method="",
            coding="",
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


if __name__ == "__main__":
    unittest.main()
