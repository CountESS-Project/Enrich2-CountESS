import os
import shutil
import unittest

from ..selection.selection import Selection
from .utilities import load_config_data, update_cfg_file

CFG_PATH = "data/config/selection/"
READS_DIR = "data/reads/selection/"
RESULT_DIR = "data/result/selection/"


class TestSelectionRaisesValueErrorOnlyWTCounts(unittest.TestCase):
    def setUp(self):
        cfg = load_config_data("selection_valueerror_only_wt.json", CFG_PATH)
        cfg = update_cfg_file(cfg, "counts", "wt")
        obj = Selection()
        obj.force_recalculate = False
        obj.component_outliers = False
        obj.tsv_requested = False
        obj.output_dir_override = False

        # perform the analysis
        obj.configure(cfg)
        obj.validate()
        obj.store_open(children=True)
        self.obj = obj

    def tearDown(self):
        self.obj.store_close(children=True)
        os.remove(self.obj.store_path)
        shutil.rmtree(self.obj.output_dir)

    def test_value_error_only_wt_counts_in_timepoints(self):
        with self.assertRaises(ValueError):
            self.obj.calculate()


if __name__ == "__main__":
    unittest.main()
