import os
from unittest import TestCase

from ..config.types import *
from ..base.config_constants import *


# -------------------------------------------------------------------------- #
#
#           Experiment, Selection, Configuration, StoreManager
#
# -------------------------------------------------------------------------- #
class StoreConfigTest(TestCase):
    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.plugin_dir = os.path.join(current_wd, "data/plugins")
        self.data_dir = os.path.join(current_wd, "data/config_check")
        self.scorer_cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "regression_scorer.py"),
            SCORER_OPTIONS: {"logr_method": "wt", "weighted": True},
        }
        self.output_dir = os.path.join(current_wd, "data/testcase/")
        self.store_path = os.path.join(self.data_dir, "testhdf5.h5")

    def tearDown(self):
        if os.path.isdir(self.output_dir):
            os.rmdir(self.output_dir)

    def test_error_name_not_in_cfg(self):
        cfg = {SCORER: self.scorer_cfg}
        with self.assertRaises(KeyError):
            StoreConfiguration(cfg).validate()

    def test_error_scorer_not_in_cfg(self):
        cfg = {NAME: "Name"}
        with self.assertRaises(KeyError):
            StoreConfiguration(cfg).validate()

    def test_invalid_name(self):
        cfg = {SCORER: self.scorer_cfg, NAME: dict()}
        with self.assertRaises(TypeError):
            StoreConfiguration(cfg).validate()

        cfg = {SCORER: self.scorer_cfg, NAME: ""}
        with self.assertRaises(ValueError):
            StoreConfiguration(cfg).validate()

    def test_error_output_dir_not_str(self):
        cfg = {SCORER: self.scorer_cfg, NAME: "test", OUTPUT_DIR: 1}
        with self.assertRaises(TypeError):
            StoreConfiguration(cfg).validate()

    def test_output_dir_correctly_made(self):
        cfg = {SCORER: self.scorer_cfg, NAME: "test", OUTPUT_DIR: self.output_dir}
        StoreConfiguration(cfg).validate()
        self.assertTrue(os.path.exists(self.output_dir))

    def test_error_store_path_not_str(self):
        cfg = {SCORER: self.scorer_cfg, NAME: "test", STORE: 1}
        with self.assertRaises(TypeError):
            StoreConfiguration(cfg).validate()

    def test_error_store_path_not_valid_file(self):
        cfg = {SCORER: self.scorer_cfg, NAME: "test", STORE: self.data_dir}
        with self.assertRaises(IOError):
            StoreConfiguration(cfg).validate()

        cfg = {
            SCORER: self.scorer_cfg,
            NAME: "test",
            STORE: os.path.join(self.plugin_dir, "regression_scorer.py"),
        }
        with self.assertRaises(IOError):
            StoreConfiguration(cfg).validate()

    def test_defaults_correct(self):
        cfg = {SCORER: self.scorer_cfg, NAME: "test"}
        store_cfg = StoreConfiguration(cfg).validate()
        self.assertEqual(store_cfg.has_output_dir, False)
        self.assertEqual(store_cfg.has_store_path, False)
        self.assertEqual(store_cfg.output_dir, "")
        self.assertEqual(store_cfg.store_path, "")

    def test_override_default_correctly(self):
        cfg = {
            SCORER: self.scorer_cfg,
            NAME: "test",
            OUTPUT_DIR: self.output_dir,
            STORE: self.store_path,
        }
        store_cfg = StoreConfiguration(cfg).validate()
        self.assertEqual(store_cfg.has_output_dir, True)
        self.assertEqual(store_cfg.has_store_path, True)
        self.assertEqual(store_cfg.output_dir, self.output_dir)
        self.assertEqual(store_cfg.store_path, self.store_path)


class SelectionConfigurationTest(TestCase):
    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.plugin_dir = os.path.join(current_wd, "data/plugins")
        self.data_dir = os.path.join(current_wd, "data/config_check")
        self.scorer_cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "regression_scorer.py"),
            SCORER_OPTIONS: {"logr_method": "wt", "weighted": True},
        }
        self.output_dir = os.path.join(current_wd, "data/testcase/")
        self.store_path = os.path.join(self.data_dir, "testhdf5.h5")

        self.lib_1_cfg = {
            NAME: "Lib1",
            REPORT_FILTERED_READS: False,
            TIMEPOINT: 0,
            IDENTIFIERS: {},
            COUNTS_FILE: os.path.join(self.data_dir, "barcode_map.txt"),
        }
        self.lib_2_cfg = {
            NAME: "Lib2",
            REPORT_FILTERED_READS: False,
            TIMEPOINT: 1,
            IDENTIFIERS: {},
            COUNTS_FILE: os.path.join(self.data_dir, "barcode_map.txt"),
        }
        self.lib_3_cfg = {
            NAME: "Lib3",
            REPORT_FILTERED_READS: False,
            TIMEPOINT: 2,
            IDENTIFIERS: {},
            COUNTS_FILE: os.path.join(self.data_dir, "barcode_map.txt"),
        }

    def tearDown(self):
        pass

    def test_error_libraries_not_in_cfg(self):
        self.cfg = {NAME: "TestSelection", SCORER: self.scorer_cfg}
        with self.assertRaises(KeyError):
            SelectionConfiguration(self.cfg, has_scorer=True).validate()

    def test_error_libraries_empty(self):
        self.cfg = {LIBRARIES: [], NAME: "TestSelection", SCORER: self.scorer_cfg}
        with self.assertRaises(ValueError):
            SelectionConfiguration(self.cfg, has_scorer=True).validate()

    def test_error_libraries_not_list(self):
        self.cfg = {LIBRARIES: set([]), NAME: "TestSelection", SCORER: self.scorer_cfg}
        with self.assertRaises(TypeError):
            SelectionConfiguration(self.cfg, has_scorer=True).validate()

    def test_error_zero_not_in_timepoints(self):
        lib_1_cfg = self.lib_1_cfg.copy()
        lib_1_cfg[TIMEPOINT] = 4
        self.cfg = {
            LIBRARIES: [lib_1_cfg, self.lib_2_cfg, self.lib_3_cfg],
            NAME: "TestSelection",
            SCORER: self.scorer_cfg,
        }
        with self.assertRaises(ValueError):
            SelectionConfiguration(self.cfg, has_scorer=True).validate()

    def test_error_less_than_two_timepoints(self):
        self.cfg = {
            LIBRARIES: [self.lib_1_cfg],
            NAME: "TestSelection",
            SCORER: self.scorer_cfg,
        }
        with self.assertRaises(ValueError):
            SelectionConfiguration(self.cfg, has_scorer=True).validate()

    def test_error_insufficient_timepoints_regression(self):
        self.cfg = {
            LIBRARIES: [self.lib_1_cfg, self.lib_2_cfg],
            NAME: "TestSelection",
            SCORER: self.scorer_cfg,
        }
        with self.assertRaises(ValueError):
            SelectionConfiguration(self.cfg, has_scorer=True).validate()

    def test_error_non_unique_lib_names(self):
        lib_1_cfg = self.lib_1_cfg.copy()
        lib_1_cfg[NAME] = "Lib2"
        self.cfg = {
            LIBRARIES: [lib_1_cfg, self.lib_2_cfg, self.lib_3_cfg],
            NAME: "TestSelection",
            SCORER: self.scorer_cfg,
        }
        with self.assertRaises(ValueError):
            SelectionConfiguration(self.cfg, has_scorer=True).validate()


class ConditionConfigTest(TestCase):
    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.plugin_dir = os.path.join(current_wd, "data/plugins")
        self.data_dir = os.path.join(current_wd, "data/config_check")

        self.lib_1_cfg = {
            NAME: "Lib1",
            REPORT_FILTERED_READS: False,
            TIMEPOINT: 0,
            IDENTIFIERS: {},
            COUNTS_FILE: os.path.join(self.data_dir, "barcode_map.txt"),
        }
        self.lib_2_cfg = {
            NAME: "Lib2",
            REPORT_FILTERED_READS: False,
            TIMEPOINT: 1,
            IDENTIFIERS: {},
            COUNTS_FILE: os.path.join(self.data_dir, "barcode_map.txt"),
        }
        self.lib_3_cfg = {
            NAME: "Lib3",
            REPORT_FILTERED_READS: False,
            TIMEPOINT: 2,
            IDENTIFIERS: {},
            COUNTS_FILE: os.path.join(self.data_dir, "barcode_map.txt"),
        }
        self.selection_1_cfg = {
            LIBRARIES: [self.lib_1_cfg, self.lib_2_cfg, self.lib_3_cfg],
            NAME: "Selection_1",
        }
        self.selection_2_cfg = {
            LIBRARIES: [self.lib_1_cfg, self.lib_2_cfg, self.lib_3_cfg],
            NAME: "Selection_2",
        }

    def tearDown(self):
        pass

    def test_error_selections_not_in_cfg(self):
        cfg = {}
        with self.assertRaises(KeyError):
            ConditonConfiguration(cfg)

    def test_error_selections_empty(self):
        cfg = {NAME: "TestCondition", SELECTIONS: []}
        with self.assertRaises(ValueError):
            ConditonConfiguration(cfg)

    def test_error_selections_not_list(self):
        cfg = {NAME: "TestCondition", SELECTIONS: {}}
        with self.assertRaises(TypeError):
            ConditonConfiguration(cfg)

    def test_selections_load_correctly(self):
        cfg = {
            NAME: "TestCondition",
            SELECTIONS: [self.selection_1_cfg, self.selection_2_cfg],
        }
        cfg = ConditonConfiguration(cfg).validate()
        self.assertEqual(cfg.store_cfg.name, "TestCondition")
        self.assertEqual(len(cfg.selection_cfgs), 2)
        self.assertEqual(cfg.selection_cfgs[0].store_cfg.name, "Selection_1")
        self.assertEqual(cfg.selection_cfgs[1].store_cfg.name, "Selection_2")


class ExperimentConfigTest(TestCase):
    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.plugin_dir = os.path.join(current_wd, "data/plugins")
        self.data_dir = os.path.join(current_wd, "data/config_check")
        self.scorer_cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "regression_scorer.py"),
            SCORER_OPTIONS: {"logr_method": "wt", "weighted": True},
        }
        self.output_dir = os.path.join(current_wd, "data/testcase/")
        self.store_path = os.path.join(self.data_dir, "testhdf5.h5")

        self.lib_1_cfg = {
            NAME: "Lib1",
            REPORT_FILTERED_READS: False,
            TIMEPOINT: 0,
            IDENTIFIERS: {},
            COUNTS_FILE: os.path.join(self.data_dir, "barcode_map.txt"),
        }
        self.lib_2_cfg = {
            NAME: "Lib2",
            REPORT_FILTERED_READS: False,
            TIMEPOINT: 1,
            IDENTIFIERS: {},
            COUNTS_FILE: os.path.join(self.data_dir, "barcode_map.txt"),
        }
        self.lib_3_cfg = {
            NAME: "Lib3",
            REPORT_FILTERED_READS: False,
            TIMEPOINT: 2,
            IDENTIFIERS: {},
            COUNTS_FILE: os.path.join(self.data_dir, "barcode_map.txt"),
        }

        self.selection_1_cfg = {
            LIBRARIES: [self.lib_1_cfg, self.lib_2_cfg, self.lib_3_cfg],
            NAME: "Selection_1",
        }
        self.selection_2_cfg = {
            LIBRARIES: [self.lib_1_cfg, self.lib_2_cfg, self.lib_3_cfg],
            NAME: "Selection_2",
        }
        self.selection_3_cfg = {
            LIBRARIES: [self.lib_1_cfg, self.lib_2_cfg, self.lib_3_cfg],
            NAME: "Selection_3",
        }

        self.condition_1_cfg = {
            NAME: "Condition_1",
            SELECTIONS: [self.selection_1_cfg, self.selection_2_cfg],
        }
        self.condition_2_cfg = {
            NAME: "Condition_2",
            SELECTIONS: [self.selection_1_cfg, self.selection_2_cfg],
        }
        self.condition_3_cfg = {NAME: "Condition_3", SELECTIONS: [self.selection_3_cfg]}

    def tearDown(self):
        pass

    def test_error_conditions_not_in_cfg(self):
        cfg = {NAME: "TestExperiment", SCORER: self.scorer_cfg}
        with self.assertRaises(KeyError):
            ExperimentConfiguration(cfg).validate()

    def test_error_conditions_empty(self):
        cfg = {NAME: "TestExperiment", CONDITIONS: [], SCORER: self.scorer_cfg}
        with self.assertRaises(ValueError):
            ExperimentConfiguration(cfg).validate()

    def test_error_conditions_not_list(self):
        cfg = {NAME: "TestExperiment", CONDITIONS: {}, SCORER: self.scorer_cfg}
        with self.assertRaises(TypeError):
            ExperimentConfiguration(cfg).validate()

    def test_error_condition_names_not_unique(self):
        cfg = {
            NAME: "TestExperiment",
            CONDITIONS: [self.condition_1_cfg, self.condition_1_cfg],
            SCORER: self.scorer_cfg,
        }
        with self.assertRaises(ValueError):
            ExperimentConfiguration(cfg).validate()

    def test_error_selection_names_across_conditons_not_unique(self):
        cfg = {
            NAME: "TestExperiment",
            CONDITIONS: [self.condition_1_cfg, self.condition_2_cfg],
            SCORER: self.scorer_cfg,
        }
        with self.assertRaises(ValueError):
            ExperimentConfiguration(cfg).validate()

    def test_conditions_load_correctly(self):
        cfg = {
            NAME: "TestExperiment",
            CONDITIONS: [self.condition_1_cfg, self.condition_3_cfg],
            SCORER: self.scorer_cfg,
        }
        cfg = ExperimentConfiguration(cfg).validate()
        self.assertEqual(cfg.store_cfg.name, "TestExperiment")
        self.assertEqual(len(cfg.condition_cfgs), 2)
        self.assertEqual(cfg.condition_cfgs[0].store_cfg.name, "Condition_1")
        self.assertEqual(cfg.condition_cfgs[1].store_cfg.name, "Condition_3")

        selection_names = [
            s_cfg.store_cfg.name
            for c_cfg in cfg.condition_cfgs
            for s_cfg in c_cfg.selection_cfgs
        ]
        expected_names = set(["Selection_1", "Selection_2", "Selection_3"])
        self.assertEqual(len(selection_names), 3)
        self.assertEqual(len(set(selection_names)), 3)
        self.assertEqual(set(selection_names), expected_names)

        self.assertEqual(cfg.store_cfg.scorer_cfg.scorer_class.name, "Regression")
        self.assertEqual(
            cfg.store_cfg.scorer_cfg.scorer_class_attrs,
            {"logr_method": "wt", "weighted": True},
        )
