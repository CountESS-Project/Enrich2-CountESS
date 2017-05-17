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


import sys
import shutil
import json
from unittest import TestCase

from ..config.types import *


# -------------------------------------------------------------------------- #
#
#           Experiment, Selection, Configuration, StoreManager
#
# -------------------------------------------------------------------------- #
class StoreConfigTest(TestCase):

    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.plugin_dir = os.path.join(current_wd, 'data/plugins')
        self.data_dir = os.path.join(current_wd, 'data/config_check')
        self.scorer_cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, 'regression_scorer.py'),
            SCORER_OPTIONS: {'logr_method': 'wt', 'weighted': True}
        }
        self.output_dir = os.path.join(current_wd, 'data/testcase/')
        self.store_path = os.path.join(self.data_dir, 'testhdf5.h5')

    def tearDown(self):
        if os.path.isdir(self.output_dir):
            os.rmdir(self.output_dir)

    def test_error_name_not_in_cfg(self):
        cfg = {SCORER: self.scorer_cfg}
        with self.assertRaises(ValueError):
            StoreConfiguration(cfg).validate()

    def test_error_scorer_not_in_cfg(self):
        cfg = {NAME: 'Name'}
        with self.assertRaises(ValueError):
            StoreConfiguration(cfg).validate()

    def test_invalid_name(self):
        cfg = {SCORER: self.scorer_cfg, NAME: dict()}
        with self.assertRaises(TypeError):
            StoreConfiguration(cfg).validate()

        cfg = {SCORER: self.scorer_cfg, NAME: ''}
        with self.assertRaises(ValueError):
            StoreConfiguration(cfg).validate()

    def test_error_output_dir_not_str(self):
        cfg = {SCORER: self.scorer_cfg, NAME: 'test', OUTPUT_DIR: 1}
        with self.assertRaises(TypeError):
            StoreConfiguration(cfg).validate()

    def test_output_dir_correctly_made(self):
        cfg = {
            SCORER: self.scorer_cfg,
            NAME: 'test',
            OUTPUT_DIR: self.output_dir
        }
        StoreConfiguration(cfg).validate()
        self.assertTrue(os.path.exists(self.output_dir))

    def test_error_store_path_not_str(self):
        cfg = {
            SCORER: self.scorer_cfg,
            NAME: 'test',
            STORE: 1
        }
        with self.assertRaises(TypeError):
            StoreConfiguration(cfg).validate()

    def test_error_store_path_not_valid_file(self):
        cfg = {
            SCORER: self.scorer_cfg,
            NAME: 'test',
            STORE: self.data_dir
        }
        with self.assertRaises(IOError):
            StoreConfiguration(cfg).validate()

        cfg = {
            SCORER: self.scorer_cfg,
            NAME: 'test',
            STORE: os.path.join(self.plugin_dir, 'regression_scorer.py')
        }
        with self.assertRaises(IOError):
            StoreConfiguration(cfg).validate()

    def test_defaults_correct(self):
        cfg = {
            SCORER: self.scorer_cfg,
            NAME: 'test',
        }
        store_cfg = StoreConfiguration(cfg).validate()
        self.assertEqual(store_cfg.has_output_dir, False)
        self.assertEqual(store_cfg.has_store_path, False)
        self.assertEqual(store_cfg.output_dir, "")
        self.assertEqual(store_cfg.store_path, "")

    def test_override_default_correctly(self):
        cfg = {
            SCORER: self.scorer_cfg,
            NAME: 'test',
            OUTPUT_DIR: self.output_dir,
            STORE: self.store_path
        }
        store_cfg = StoreConfiguration(cfg).validate()
        self.assertEqual(store_cfg.has_output_dir, True)
        self.assertEqual(store_cfg.has_store_path, True)
        self.assertEqual(store_cfg.output_dir, self.output_dir)
        self.assertEqual(store_cfg.store_path, self.store_path)


class SelectionConfigurationTest(TestCase):

    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.plugin_dir = os.path.join(current_wd, 'data/plugins')
        self.data_dir = os.path.join(current_wd, 'data/config_check')
        self.scorer_cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, 'regression_scorer.py'),
            SCORER_OPTIONS: {'logr_method': 'wt', 'weighted': True}
        }
        self.output_dir = os.path.join(current_wd, 'data/testcase/')
        self.store_path = os.path.join(self.data_dir, 'testhdf5.h5')

        self.lib_1_cfg = {
            NAME: 'Lib1',
            REPORT_FILTERED_READS: False,
            TIMEPOINT: 0,
            IDENTIFIERS: {},
            COUNTS_FILE: os.path.join(self.data_dir, 'barcode_map.txt')
        }
        self.lib_2_cfg = {
            NAME: 'Lib2',
            REPORT_FILTERED_READS: False,
            TIMEPOINT: 1,
            IDENTIFIERS: {},
            COUNTS_FILE: os.path.join(self.data_dir, 'barcode_map.txt')
        }
        self.lib_3_cfg = {
            NAME: 'Lib3',
            REPORT_FILTERED_READS: False,
            TIMEPOINT: 2,
            IDENTIFIERS: {},
            COUNTS_FILE: os.path.join(self.data_dir, 'barcode_map.txt')
        }

        self.cfg = {
            LIBRARIES: [self.lib_1_cfg, self.lib_2_cfg, self.lib_3_cfg],
            NAME: "TestSelection",
            SCORER: self.scorer_cfg
        }
        print(SelectionsConfiguration(self.cfg))

    def tearDown(self):
        pass

    def test_error_libraries_not_in_cfg(self):
        self.cfg = {
            NAME: "TestSelection",
            SCORER: self.scorer_cfg
        }
        with self.assertRaises(ValueError):
            SelectionsConfiguration(self.cfg, has_scorer=True).validate()

    def test_error_libraries_empty(self):
        self.cfg = {
            LIBRARIES: [],
            NAME: "TestSelection",
            SCORER: self.scorer_cfg
        }
        with self.assertRaises(ValueError):
            SelectionsConfiguration(self.cfg, has_scorer=True).validate()

    def test_error_libraries_not_list(self):
        self.cfg = {
            LIBRARIES: set([]),
            NAME: "TestSelection",
            SCORER: self.scorer_cfg
        }
        with self.assertRaises(TypeError):
            SelectionsConfiguration(self.cfg, has_scorer=True).validate()

    def test_error_zero_not_in_timepoints(self):
        lib_1_cfg = self.lib_1_cfg.copy()
        lib_1_cfg[TIMEPOINT] = 4
        self.cfg = {
            LIBRARIES: [lib_1_cfg, self.lib_2_cfg, self.lib_3_cfg],
            NAME: "TestSelection",
            SCORER: self.scorer_cfg
        }
        with self.assertRaises(ValueError):
            SelectionsConfiguration(self.cfg, has_scorer=True).validate()

    def test_error_less_than_two_timepoints(self):
        self.cfg = {
            LIBRARIES: [self.lib_1_cfg],
            NAME: "TestSelection",
            SCORER: self.scorer_cfg
        }
        with self.assertRaises(ValueError):
            SelectionsConfiguration(self.cfg, has_scorer=True).validate()

    def test_error_insufficient_timepoints_regression(self):
        self.cfg = {
            LIBRARIES: [self.lib_1_cfg, self.lib_2_cfg],
            NAME: "TestSelection",
            SCORER: self.scorer_cfg
        }
        with self.assertRaises(ValueError):
            SelectionsConfiguration(self.cfg, has_scorer=True).validate()

    def test_error_non_unique_lib_names(self):
        lib_1_cfg = self.lib_1_cfg.copy()
        lib_1_cfg[NAME] = 'Lib2'
        self.cfg = {
            LIBRARIES: [lib_1_cfg, self.lib_2_cfg, self.lib_3_cfg],
            NAME: "TestSelection",
            SCORER: self.scorer_cfg
        }
        with self.assertRaises(ValueError):
            SelectionsConfiguration(self.cfg, has_scorer=True).validate()


class ConditionConfigTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_error_selections_not_in_cfg(self):
        pass

    def test_error_selections_empty(self):
        pass

    def test_error_selections_not_list(self):
        pass



class ExperimentConfigTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_error_conditions_not_in_cfg(self):
        pass

    def test_error_conditions_empty(self):
        pass

    def test_error_conditions_not_list(self):
        pass

    def test_error_condition_names_not_unique(self):
        pass

    def test_error_selection_names_across_conditons_not_unique(self):
        pass

