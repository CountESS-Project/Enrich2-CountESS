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

from ..libraries.idonly import IdOnlySeqLib
from .utilities import load_config_data, create_file_path
from .methods import HDF5TestComponent


CFG_FILE = "idonly.json"
CFG_DIR = "data/config/idonly/"
READS_DIR = create_file_path("idonly/", "data/reads/")
RESULT_DIR = "data/result/idonly/"

LIBTYPE = 'idonly'
FILE_EXT = 'tsv'
FILE_SEP = '\t'


# -------------------------------------------------------------------------- #
#
#                          Counts Only Mode No Filter
#
# -------------------------------------------------------------------------- #
class TestIdonlySeqLibCountsOnlyModeNoFilter(unittest.TestCase):

    def setUp(self):
        prefix = 'counts_only'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['counts file'] = "{}/{}".format(
            READS_DIR ,'{}.tsv'.format(prefix))

        self.test_component = HDF5TestComponent(
            store_constructor=IdOnlySeqLib, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, verbose=False,
            libtype=prefix, scoring_method='', logr_method='', coding=''
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()
    
    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                      Barcode Min Count Filter
#
# -------------------------------------------------------------------------- #
class TestIdonlySeqLibCountsWithIdentifiersMinCountSetting(unittest.TestCase):

    def setUp(self):
        prefix = 'identifiers_mincount'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['counts file'] = "{}/{}".format(
            READS_DIR , '{}.tsv'.format(prefix))
        cfg['identifiers']['min count'] = 2

        self.test_component = HDF5TestComponent(
            store_constructor=IdOnlySeqLib, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, verbose=False,
            libtype=prefix, scoring_method='', logr_method='', coding=''
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                                   MAIN
#
# -------------------------------------------------------------------------- #
if __name__ == "__main__":
    unittest.main()
