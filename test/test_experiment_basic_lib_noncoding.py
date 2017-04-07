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
from itertools import product
from copy import deepcopy

from test.utilities import load_config_data
from test.utilities import DEFAULT_STORE_PARAMS
from test.test_methods import GeneralTestCase
from enrich2.stores.experiment import Experiment

CFG_PATH = "data/config/experiment/"
READS_DIR = "data/reads/experiment/"
RESULT_DIR = "data/result/experiment/"

if __name__ == "__main__":
    suite = unittest.TestSuite()
    score_methods = ['WLS', 'OLS', 'ratios', 'counts', 'simple']
    logr_methods = ['wt', 'complete', 'full']
    libtype = 'basic'
    coding_str = 'n'
    cfg_file = "{}_experiment_noncoding.json".format(libtype)
    cfg = load_config_data(cfg_file, CFG_PATH)
    driver_name = "runTest"

    for (s, l) in product(score_methods, logr_methods):
        params = deepcopy(DEFAULT_STORE_PARAMS)
        params['scoring_method'] = s
        params['logr_method'] = l
        test_case = GeneralTestCase(
            methodName=driver_name,
            store_constructor=Experiment,
            cfg=cfg,
            params=params,
            file_prefix='{}_{}_{}_{}'.format(libtype, coding_str, s, l),
            result_dir=RESULT_DIR,
            file_ext='pkl',
            verbose=False,
            save=False
        )
        class_name = "TestExperiment{}Lib{}Scoring{}Norm{}".format(
            libtype.capitalize(), s.capitalize(), l.capitalize(),
            coding_str.upper()
        )
        test_case.__name__ = class_name
        suite.addTest(test_case)

    # Run suite
    runner = unittest.TextTestRunner()
    runner.run(suite)
