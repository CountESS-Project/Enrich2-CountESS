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
from copy import deepcopy

from test.utilities import load_config_data
from test.utilities import DEFAULT_STORE_PARAMS
from test.methods import HDF5TestComponent

from enrich2.stores.selection import Selection


CFG_FILE = "selection_timepoint_merge.json"
CFG_DIR = "data/config/selection/"
READS_DIR = "data/reads/selection/"
RESULT_DIR = "data/result/selection/"

DRIVER = "runTest"
LIBTYPE = 'barcode'
FILE_EXT = 'tsv'
FILE_SEP = '\t'


class TestSelectionTimepointMerge(unittest.TestCase):

    def setUp(self):
        scoring = 'counts'
        logr = 'wt'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        params = deepcopy(DEFAULT_STORE_PARAMS)
        params['scoring_method'] = scoring
        params['logr_method'] = logr
        file_prefix = "timepoint_merge"

        self.general_test_component = HDF5TestComponent(
            methodName=DRIVER,
            store_constructor=Selection,
            cfg=cfg,
            params=params,
            file_prefix=file_prefix,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            verbose=False,
            save=False
        )
        self.general_test_component.setUp()

    def tearDown(self):
        self.general_test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.general_test_component.runTest()


if __name__ == "__main__":
    unittest.main()
