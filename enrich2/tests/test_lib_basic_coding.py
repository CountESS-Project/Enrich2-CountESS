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

from ..libraries.basic import BasicSeqLib
from .utilities import load_config_data, create_file_path
from .methods import HDF5TestComponent


CFG_FILE = "basic_coding.json"
CFG_DIR = "data/config/basic/"
READS_DIR = create_file_path("basic/", "data/reads/")
RESULT_DIR = "data/result/basic/"

LIBTYPE = 'basic'
FILE_EXT = 'tsv'
FILE_SEP = '\t'
CODING_STR = 'c'


# -------------------------------------------------------------------------- #
#
#                          INTEGRATION COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsIntegrated(unittest.TestCase):

    def setUp(self):
        prefix = 'integrated'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)

        # Set all filter parameters
        cfg['fastq']['filters']['max N'] = 0
        cfg['fastq']['filters']['chastity'] = True
        cfg['fastq']['filters']['avg quality'] = 38
        cfg['fastq']['filters']['min quality'] = 20

        # Set trim parameters
        cfg['fastq']['start'] = 4
        cfg['fastq']['length'] = 3
        cfg['fastq']['reverse'] = True
        cfg['variants']['wild type']['sequence'] = "TTT"

        # Set Variant parameters
        cfg['variants']['wild type']['reference offset'] = 5
        cfg['variants']['min counts'] = 2
        cfg['variants']['max mutations'] = 1
        cfg['variants']['use aligner'] = True

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()
    
    def tearDown(self):
        self.test_component.tearDown()
    
    
    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                   SYNONYMOUS COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsSynonymous(unittest.TestCase):
    
    def setUp(self):
        prefix = 'synonymous'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)
        
        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                   SINGLE MUTATION COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsSingleMutation(unittest.TestCase):
    
    def setUp(self):
        prefix = 'single_mut'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                   MULTIMUTATION COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsMultiMutation(unittest.TestCase):
    
    def setUp(self):
        prefix = 'multi_mut'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                   WILDTYPE COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWildType(unittest.TestCase):

    def setUp(self):
        prefix = 'wildtype'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                   FASTQ MAXN FILTER COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithMaxNFQFilter(unittest.TestCase):
    
    def setUp(self):
        prefix = 'filter_maxn'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)
        cfg['fastq']['filters']['max N'] = 0

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                   FASTQ CHASTE FILTER COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithChaste(unittest.TestCase):

    def setUp(self):
        prefix = 'filter_chastity'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)
        cfg['fastq']['filters']['chastity'] = True

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                    FASTQ MIN QUAL FILTER COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithMinQualFQFilter(unittest.TestCase):
    
    def setUp(self):
        prefix = 'filter_minq'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)
        cfg['fastq']['filters']['min quality'] = 20

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()

# -------------------------------------------------------------------------- #
#
#                    FASTQ AVG QUAL FILTER COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithAvgQualFQFilter(unittest.TestCase):
    
    def setUp(self):
        prefix = 'filter_avgq'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)
        cfg['fastq']['filters']['avg quality'] = 38

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                    FASTQ TRIM LENGTH COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsTrimLengthSetting(unittest.TestCase):
    
    def setUp(self):
        prefix = 'trim_len'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)
        cfg['fastq']['length'] = 3
        cfg['variants']['wild type']['sequence'] = "AAA"

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                    FASTQ TRIM START COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsTrimStartSetting(unittest.TestCase):
    
    def setUp(self):
        prefix = 'trim_start'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)
        cfg['fastq']['start'] = 4
        cfg['variants']['wild type']['sequence'] = "AAA"

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                    FASTQ REVERSE COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsReverseSetting(unittest.TestCase):
    
    def setUp(self):
        prefix = 'revcomp'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)
        cfg['fastq']['reverse'] = True
        cfg['variants']['wild type']['sequence'] = "TTTTTT"

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                    VARIANT WT-OFFSET COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithRefOffset(unittest.TestCase):
    
    def setUp(self):
        prefix = 'reference_offset'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)
        cfg['variants']['wild type']['reference offset'] = 6

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()

# -------------------------------------------------------------------------- #
#
#                    VARIANT WT-OFFSET COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithRefOffsetNotMultipleOfThree(unittest.TestCase):
    
    def setUp(self):
        prefix = 'reference_offset_not_multiple'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq'][
            'reads'] = '{}/{}.fq'.format(READS_DIR, prefix)
        cfg['variants']['wild type']['reference offset'] = 5

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                    VARIANT MIN COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithVariantMinCount(unittest.TestCase):

    def setUp(self):
        prefix = 'variant_mincounts'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)
        cfg['variants']['min counts'] = 2

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                    VARIANT MAX MUTATIONS COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithVariantMaxMutations(unittest.TestCase):

    def setUp(self):
        prefix = 'variant_maxmutations'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)
        cfg['variants']['max mutations'] = 1

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                    VARIANT ALIGNER COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithVariantAligner(unittest.TestCase):

    def setUp(self):
        prefix = 'use_aligner'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, prefix)
        cfg['variants']['use aligner'] = True

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                   COUNTS ONLY MODE
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsOnlyMode(unittest.TestCase):
    
    def setUp(self):
        prefix = 'counts_only'
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg['counts file'] = '{}/{}.tsv'.format(READS_DIR, prefix)

        self.test_component = HDF5TestComponent(
            store_constructor=BasicSeqLib,
            cfg=cfg,
            file_prefix="{}_{}".format(CODING_STR, prefix),
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False
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