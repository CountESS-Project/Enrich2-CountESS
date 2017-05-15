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


import os
from unittest import TestCase

from ..config.types import *


class ScorerConfigTest(TestCase):

    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.plugin_dir = os.path.join(current_wd, 'data/plugins')

    def tearDown(self):
        pass

    def test_error_path_key_missing(self):
        cfg = {SCORER_OPTIONS: {}}
        with self.assertRaises(ValueError):
            ScorerConfiguration(cfg)

    def test_error_invalid_path(self):
        cfg = {SCORER_PATH: "", SCORER_OPTIONS: {}}
        with self.assertRaises(IOError):
            ScorerConfiguration(cfg)

    def test_error_options_key_missing(self):
        cfg = {SCORER_PATH: ""}
        with self.assertRaises(ValueError):
            ScorerConfiguration(cfg)

    def test_error_invalid_plugin_file(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, 'bad_scorer_incomplete.py'),
            SCORER_OPTIONS: {'logr_method': 'wt', 'weighted': False}
        }
        with self.assertRaises(ImportError):
            ScorerConfiguration(cfg)

        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, 'bad_options.py'),
            SCORER_OPTIONS: {'logr_method': 'wt', 'weighted': False}
        }
        with self.assertRaises(ImportError):
            ScorerConfiguration(cfg)

        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, 'non_python_file.txt'),
            SCORER_OPTIONS: {'logr_method': 'wt', 'weighted': False}
        }
        with self.assertRaises(IOError):
            ScorerConfiguration(cfg)

    def test_validate_valid_plugin(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, 'regression_scorer.py'),
            SCORER_OPTIONS: {'logr_method': 'wt', 'weighted': False}
        }
        scorer_cfg = ScorerConfiguration(cfg).validate()
        self.assertTrue(
            scorer_cfg.scoring_class_attrs,
            {'logr_method': 'wt', 'weighted': False}
        )
        self.assertTrue(
            scorer_cfg.scoring_class.name,
            'Regression'
        )

    def test_warn_on_missing_options(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, 'regression_scorer.py'),
            SCORER_OPTIONS: {'logr_method': 'wt'}
        }
        scorer_cfg = ScorerConfiguration(cfg).validate()
        self.assertTrue(
            scorer_cfg.scoring_class_attrs,
            {'logr_method': 'wt', 'weighted': True}
        )

    def test_error_on_unused_options(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, 'regression_scorer.py'),
            SCORER_OPTIONS: {'logr_method': 'wt', 'random_var': 1}
        }
        with self.assertRaises(ValueError):
            ScorerConfiguration(cfg).validate()

    def test_missing_options_default_correctly(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, 'regression_scorer.py'),
            SCORER_OPTIONS: {'weighted': True}
        }
        scorer_cfg = ScorerConfiguration(cfg).validate()
        self.assertTrue(
            scorer_cfg.scoring_class_attrs,
            {'logr_method': 'wt', 'weighted': True}
        )

    def test_options_override_defaults_correctly(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, 'regression_scorer.py'),
            SCORER_OPTIONS: {'logr_method': 'complete', 'weighted': False}
        }
        scorer_cfg = ScorerConfiguration(cfg).validate()
        self.assertTrue(
            scorer_cfg.scoring_class_attrs,
            {'logr_method': 'complete', 'weighted': False}
        )

    def test_loads_expected_scoring_class(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, 'regression_scorer.py'),
            SCORER_OPTIONS: {'logr_method': 'complete', 'weighted': False}
        }
        scorer_cfg = ScorerConfiguration(cfg).validate()
        self.assertTrue(
            scorer_cfg.scoring_class.name,
            'Regression'
        )

    def test_empty_options_dict_defaults_correct(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, 'regression_scorer.py'),
            SCORER_OPTIONS: {}
        }
        scorer_cfg = ScorerConfiguration(cfg).validate()
        self.assertTrue(
            scorer_cfg.scoring_class_attrs,
            {'logr_method': 'wt', 'weighted': True}
        )

    def test_error_setting_options_with_incorrect_dtypes(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, 'regression_scorer.py'),
            SCORER_OPTIONS: {'weighted': 123}
        }
        with self.assertRaises(TypeError):
            ScorerConfiguration(cfg).validate()


    def test_error_setting_options_with_incorrect_choices(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, 'regression_scorer.py'),
            SCORER_OPTIONS: {'logr_method': 'badkey', 'weighted': True}
        }
        with self.assertRaises(ValueError):
            ScorerConfiguration(cfg).validate()


class FASTQConfigTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
