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

from ..libraries.barcode import BarcodeSeqLib
from .utilities import load_config_data, create_file_path
from .methods import HDF5TestComponent


CFG_FILE = "barcode.json"
CFG_DIR = "data/config/barcode/"
READS_DIR = create_file_path("barcode/", "data/reads/")
RESULT_DIR = "data/result/barcode/"

LIBTYPE = 'barcode'
FILE_EXT = 'tsv'
FILE_SEP = '\t'


# -------------------------------------------------------------------------- #
#
#                   BARCODE INTEGRATED COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibCountsIntegratedFilters(unittest.TestCase):

    def setUp(self):
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/integrated.fq'.format(READS_DIR)
        cfg['fastq']['filters']['max N'] = 0
        cfg['fastq']['filters']['chastity'] = True
        cfg['fastq']['filters']['avg quality'] = 38
        cfg['fastq']['filters']['min quality'] = 20
        cfg['fastq']['start'] = 4
        cfg['fastq']['length'] = 3
        cfg['fastq']['reverse'] = True
        cfg['barcodes']['min count'] = 2

        self.test_component = HDF5TestComponent(
            store_constructor=BarcodeSeqLib, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, verbose=False,
            libtype='integrated', scoring_method='', logr_method='', coding=''
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                   BARCODE MINCOUNT COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibCountWithBarcodeMinCountSetting(unittest.TestCase):

    def setUp(self):
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/barcode_mincount.fq'.format(READS_DIR)
        cfg['barcodes']['min count'] = 2

        self.test_component = HDF5TestComponent(
            store_constructor=BarcodeSeqLib, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, verbose=False,
            libtype='mincount', scoring_method='', logr_method='', coding=''
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                BARCODE COUNTS ONLY MODE COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibCountCountsOnlyMode(unittest.TestCase):

    def setUp(self):
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['counts file'] = '{}/counts_only.tsv'.format(READS_DIR)
        cfg['barcodes']['min count'] = 2

        self.test_component = HDF5TestComponent(
            store_constructor=BarcodeSeqLib, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, verbose=False,
            libtype='counts_only', scoring_method='', logr_method='', coding=''
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                FASTQ FILTER AVERAGE QUALITY
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibWithAvgQualityFQFilter(unittest.TestCase):

    def setUp(self):
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/filter_avgq.fq'.format(READS_DIR)
        cfg['fastq']['filters']['avg quality'] = 39

        self.test_component = HDF5TestComponent(
            store_constructor=BarcodeSeqLib, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, verbose=False,
            libtype='filter_avgq', scoring_method='', logr_method='', coding=''
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                           FASTQ FILTER MAX N
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibWithMaxNFQFilter(unittest.TestCase):

    def setUp(self):
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/filter_maxn.fq'.format(READS_DIR)
        cfg['fastq']['filters']['max N'] = 1

        self.test_component = HDF5TestComponent(
            store_constructor=BarcodeSeqLib, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, verbose=False,
            libtype='filter_maxn', scoring_method='', logr_method='', coding=''
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                           FASTQ FILTER MIN QUALITY
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibWithMinQualFQFilter(unittest.TestCase):

    def setUp(self):
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/filter_minq.fq'.format(READS_DIR)
        cfg['fastq']['filters']['min quality'] = 38

        self.test_component = HDF5TestComponent(
            store_constructor=BarcodeSeqLib, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, verbose=False,
            libtype='filter_minq', scoring_method='', logr_method='', coding=''
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                           FASTQ FILTER NOT CHASTE
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibWithChastityFQFilter(unittest.TestCase):

    def setUp(self):
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/filter_not_chaste.fq'.format(READS_DIR)
        cfg['fastq']['filters']['chastity'] = True

        self.test_component = HDF5TestComponent(
            store_constructor=BarcodeSeqLib, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, verbose=False,
            libtype='filter_not_chaste', scoring_method='',
            logr_method='', coding=''
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          USE REVCOMP
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibWithRevcompSetting(unittest.TestCase):

    def setUp(self):
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/revcomp.fq'.format(READS_DIR)
        cfg['fastq']['reverse'] = True

        self.test_component = HDF5TestComponent(
            store_constructor=BarcodeSeqLib, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, verbose=False,
            libtype='revcomp', scoring_method='', logr_method='', coding=''
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                       USE TRIM START SETTING
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibWithTrimStartSetting(unittest.TestCase):

    def setUp(self):
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/trim_start.fq'.format(READS_DIR)
        cfg['fastq']['start'] = 4

        self.test_component = HDF5TestComponent(
            store_constructor=BarcodeSeqLib, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, verbose=False,
            libtype='trim_start', scoring_method='', logr_method='', coding=''
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                        USE TRIM LENGTH SETTING
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibWithTrimLenSetting(unittest.TestCase):

    def setUp(self):
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/trim_len.fq'.format(READS_DIR)
        cfg['fastq']['length'] = 5

        self.test_component = HDF5TestComponent(
            store_constructor=BarcodeSeqLib, cfg=cfg, result_dir=RESULT_DIR,
            file_ext=FILE_EXT, file_sep=FILE_SEP, save=False, verbose=False,
            libtype='trim_len', scoring_method='', logr_method='', coding=''
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
