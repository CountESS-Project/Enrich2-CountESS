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

from ..libraries.barcodeid import BcidSeqLib
from .utilities import load_config_data, create_file_path
from .methods import HDF5TestComponent


CFG_FILE = "barcodeid.json"
CFG_DIR = "data/config/barcodeid/"
READS_DIR = create_file_path("barcodeid/", "data/reads/")
RESULT_DIR = "data/result/barcodeid/"

LIBTYPE = 'barcodeid'
FILE_EXT = 'tsv'
FILE_SEP = '\t'


# -------------------------------------------------------------------------- #
#
#                          Integrated Filters
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsIntegratedFilters(unittest.TestCase):
    
    def setUp(self):
        prefix = 'integrated'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR ,'{}.fq'.format(prefix))
        cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'integrated_barcode_map.txt')
        cfg['fastq']['filters']['max N'] = 0
        cfg['fastq']['filters']['chastity'] = True
        cfg['fastq']['filters']['avg quality'] = 38
        cfg['fastq']['filters']['min quality'] = 20
        cfg['fastq']['start'] = 4
        cfg['fastq']['length'] = 3
        cfg['fastq']['reverse'] = True
        cfg['barcodes']['min count'] = 2
        cfg['identifiers']['min count'] = 3
        
        self.test_component = HDF5TestComponent(store_constructor=BcidSeqLib,
                                                cfg=cfg, file_prefix=prefix,
                                                result_dir=RESULT_DIR,
                                                file_ext=FILE_EXT,
                                                file_sep=FILE_SEP, save=False,
                                                verbose=False)
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
class TestBcidSeqLibCountsBarcodeMinCountSetting(unittest.TestCase):

    def setUp(self):
        prefix = 'barcode_mincount'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(prefix))
        cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'barcode_map.txt')
        cfg['barcodes']['min count'] = 2

        self.test_component = HDF5TestComponent(store_constructor=BcidSeqLib,
                                                cfg=cfg, file_prefix=prefix,
                                                result_dir=RESULT_DIR,
                                                file_ext=FILE_EXT,
                                                file_sep=FILE_SEP, save=False,
                                                verbose=False)
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                      Counts Only Mode
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsCountsOnlyMode(unittest.TestCase):

    def setUp(self):
        prefix = 'counts_only'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['counts file'] = "{}/{}".format(
            READS_DIR , '{}.tsv'.format(prefix))
        cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'barcode_map.txt')
        
        self.test_component = HDF5TestComponent(store_constructor=BcidSeqLib,
                                                cfg=cfg, file_prefix=prefix,
                                                result_dir=RESULT_DIR,
                                                file_ext=FILE_EXT,
                                                file_sep=FILE_SEP, save=False,
                                                verbose=False)
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                      Average Qual FASTQ Filter
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsAvgQualFQFilter(unittest.TestCase):

    
    def setUp(self):
        prefix = 'filter_avgq'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(prefix))
        cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'barcode_map.txt')
        cfg['fastq']['filters']['avg quality'] = 38
        
        self.test_component = HDF5TestComponent(store_constructor=BcidSeqLib,
                                                cfg=cfg, file_prefix=prefix,
                                                result_dir=RESULT_DIR,
                                                file_ext=FILE_EXT,
                                                file_sep=FILE_SEP, save=False,
                                                verbose=False)
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()

# -------------------------------------------------------------------------- #
#
#                      Max N FASTQ Filter
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsMaxNFQFilter(unittest.TestCase):

    
    def setUp(self):
        prefix = 'filter_maxn'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(prefix))
        cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'barcode_map.txt')
        cfg['fastq']['filters']['max N'] = 0
        
        self.test_component = HDF5TestComponent(store_constructor=BcidSeqLib,
                                                cfg=cfg, file_prefix=prefix,
                                                result_dir=RESULT_DIR,
                                                file_ext=FILE_EXT,
                                                file_sep=FILE_SEP, save=False,
                                                verbose=False)
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                      Min Quality FASTQ Filter
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsMinQualFQFilter(unittest.TestCase):

    
    def setUp(self):
        prefix = 'filter_minq'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(prefix))
        cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'barcode_map.txt')
        cfg['fastq']['filters']['min quality'] = 20

        self.test_component = HDF5TestComponent(store_constructor=BcidSeqLib,
                                                cfg=cfg, file_prefix=prefix,
                                                result_dir=RESULT_DIR,
                                                file_ext=FILE_EXT,
                                                file_sep=FILE_SEP, save=False,
                                                verbose=False)
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                      Not Chaste FASTQ Filter
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsNotChasteFQFilter(unittest.TestCase):

    
    def setUp(self):
        prefix = 'filter_not_chaste'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(prefix))
        cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'barcode_map.txt')
        cfg['fastq']['filters']['chastity'] = True

        self.test_component = HDF5TestComponent(store_constructor=BcidSeqLib,
                                                cfg=cfg, file_prefix=prefix,
                                                result_dir=RESULT_DIR,
                                                file_ext=FILE_EXT,
                                                file_sep=FILE_SEP, save=False,
                                                verbose=False)
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                      Identifiers Min Count Filter
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsWithIdentifiersMinCountFilter(unittest.TestCase):

    
    def setUp(self):
        prefix = 'identifiers_mincount'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(prefix))
        cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'barcode_map.txt')
        cfg['identifiers']['min count'] = 2

        self.test_component = HDF5TestComponent(store_constructor=BcidSeqLib,
                                                cfg=cfg, file_prefix=prefix,
                                                result_dir=RESULT_DIR,
                                                file_ext=FILE_EXT,
                                                file_sep=FILE_SEP, save=False,
                                                verbose=False)
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                      Reverse Completement Setting On
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsWithRevCompSetting(unittest.TestCase):

    
    def setUp(self):
        prefix = 'revcomp'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(prefix))
        cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'revcomp_barcode_map.txt')
        cfg['fastq']['reverse'] = True

        self.test_component = HDF5TestComponent(store_constructor=BcidSeqLib,
                                                cfg=cfg, file_prefix=prefix,
                                                result_dir=RESULT_DIR,
                                                file_ext=FILE_EXT,
                                                file_sep=FILE_SEP, save=False,
                                                verbose=False)
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                      Trim Length Setting
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsWithTrimLengthSetting(unittest.TestCase):

    
    def setUp(self):
        prefix = 'trim_len'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(prefix))
        cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'trim_len_barcode_map.txt')
        cfg['fastq']['length'] = 3

        self.test_component = HDF5TestComponent(store_constructor=BcidSeqLib,
                                                cfg=cfg, file_prefix=prefix,
                                                result_dir=RESULT_DIR,
                                                file_ext=FILE_EXT,
                                                file_sep=FILE_SEP, save=False,
                                                verbose=False)
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                      Trim Start Setting
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsWithTrimStartSetting(unittest.TestCase):

    
    def setUp(self):
        prefix = 'trim_start'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(prefix))
        cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'trim_start_barcode_map.txt')
        cfg['fastq']['start'] = 4

        self.test_component = HDF5TestComponent(store_constructor=BcidSeqLib,
                                                cfg=cfg, file_prefix=prefix,
                                                result_dir=RESULT_DIR,
                                                file_ext=FILE_EXT,
                                                file_sep=FILE_SEP, save=False,
                                                verbose=False)
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
