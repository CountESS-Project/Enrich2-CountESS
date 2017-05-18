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

from ..plugins import load_scorer_class_and_options
from ..plugins.options import Options


class PluginLoadingTest(TestCase):

    def setUp(self):
        self.directory = os.path.dirname(__file__)
        self.bad_scorer = os.path.join(
            self.directory, 'data/plugins/bad_scorer.py')
        self.counts_scorer = os.path.join(
            self.directory, 'data/plugins/counts_scorer.py')
        self.no_scorers = os.path.join(
            self.directory, 'data/plugins/no_scorers.py')
        self.non_py_file = os.path.join(
            self.directory, 'data/plugins/non_python_file.txt')
        self.regression_scorer = os.path.join(
            self.directory, 'data/plugins/regression_scorer.py')
        self.two_scorers = os.path.join(
            self.directory, 'data/plugins/two_scorers.py')
        self.two_scorers = os.path.join(
            self.directory, 'data/plugins/two_scorers.py')
        self.bad_scorer_incomplete = os.path.join(
            self.directory, 'data/plugins/bad_scorer_incomplete.py')
        self.bad_options = os.path.join(
            self.directory, 'data/plugins/bad_options.py')
        self.non_existent = os.path.join(
            self.directory, 'data/plugins/random.py')
        self.two_optons_def = os.path.join(
            self.directory, 'data/plugins/two_options.py')
        self.empty_options = os.path.join(
            self.directory, 'data/plugins/empty_options.py')
        self.non_module = os.path.join(
            self.directory, 'data/plugins_non_module/counts_scorer.py')

    def tearDown(self):
        pass

    def test_error_non_module(self):
        with self.assertRaises(ImportError):
            load_scorer_class_and_options(self.non_module)

    def test_error_non_python_file(self):
        with self.assertRaises(IOError):
            load_scorer_class_and_options(self.non_py_file)

    def test_error_bad_path(self):
        with self.assertRaises(IOError):
            load_scorer_class_and_options(self.non_existent)

    def test_error_too_many_classes(self):
        with self.assertRaises(ImportError):
            load_scorer_class_and_options(self.two_scorers)

    def test_error_no_classes(self):
        with self.assertRaises(ImportError):
            load_scorer_class_and_options(self.no_scorers)

    def test_error_two_options_classes_defined(self):
        with self.assertRaises(ImportError):
            load_scorer_class_and_options(self.two_optons_def)

    def test_error_empty_options_class(self):
        with self.assertRaises(ImportError):
            load_scorer_class_and_options(self.empty_options)

    def test_correct_options(self):
        _, result, _ = load_scorer_class_and_options(self.regression_scorer)
        expected = Options()
        expected.add_option(
            name="Normalization Method",
            varname="logr_method",
            dtype=str,
            default='Wild Type',
            choices={'Wild Type': 'wt', 'Full': 'full',
                     'Complete': 'complete'},
            hidden=False
        )
        expected.add_option(
            name="Weighted",
            varname="weighted",
            dtype=bool,
            default=True,
            choices=None,
            hidden=False
        )
        self.assertEqual(expected, result)

    def test_correct_options_file(self):
        _, _, options_file = load_scorer_class_and_options(self.counts_scorer)
        self.assertTrue(options_file is None)

        _, _, options_file = load_scorer_class_and_options(
            self.regression_scorer)
        self.assertTrue(options_file is not None)

    def test_error_incomplete_implementation(self):
        with self.assertRaises(ImportError):
            load_scorer_class_and_options(self.bad_scorer_incomplete)
