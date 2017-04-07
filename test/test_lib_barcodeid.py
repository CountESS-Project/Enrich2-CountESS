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
import unittest
import os.path

from test.utilities import load_config_data, load_df_from_txt
from test.utilities import print_groups, single_column_df_equal
from enrich2.libraries.barcodeid import BcidSeqLib


# -------------------------------------------------------------------------- #
#
#                           UTILTIES
#
# -------------------------------------------------------------------------- #
CFG_PATH = "barcodeid/barcodeid.json"
READS_DIR = "data/reads/barcodeid"
RESULT_DIR = "barcodeid/"


def make_libarary(cfg, **kwargs):
    obj = BcidSeqLib()
    obj.force_recalculate = False
    obj.component_outliers = False
    obj.scoring_method = 'counts'
    obj.logr_method = 'wt'
    obj.plots_requested = False
    obj.tsv_requested = False
    obj.output_dir_override = False

    # perform the analysis
    obj.configure(cfg)
    obj.validate()
    obj.store_open(children=True)
    obj.calculate()

    for k, v in kwargs.items():
        setattr(obj, k, v)
    return obj


class HDF5Verifier(object):

    def __call__(self, test_class, file_prefix, sep=';'):
        self.test_class = test_class
        self.prefix = file_prefix
        self.sep = sep
        if file_prefix != 'counts_only':
            self.test_raw_filter()
            self.test_serialize()
        self.test_main_barcodes_counts()
        self.test_raw_barcodes_counts()
        self.test_main_identifiers_counts()
        self.test_raw_barcode_map()

    def test_main_barcodes_counts(self):
        expected = load_df_from_txt(
            '{}/{}_main_barcodes_counts.tsv'.format(RESULT_DIR, self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/main/barcodes/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_raw_barcodes_counts(self):
        expected = load_df_from_txt(
            '{}/{}_raw_barcodes_counts.tsv'.format(RESULT_DIR, self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/raw/barcodes/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_main_identifiers_counts(self):
        expected = load_df_from_txt(
            '{}/{}_main_identifiers_counts.tsv'.format(
                RESULT_DIR, self.prefix), sep=self.sep
        )
        result = self.test_class.store['/main/identifiers/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_raw_filter(self):
        expected = load_df_from_txt(
            '{}/{}_raw_filter.tsv'.format(RESULT_DIR, self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/raw/filter']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_raw_barcode_map(self):
        expected = load_df_from_txt(
            '{}/{}_raw_barcodemap.tsv'.format(RESULT_DIR, self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/raw/barcodemap']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_serialize(self):
        cfg = self.test_class._obj.serialize()
        self.test_class.assertTrue(self.test_class._cfg == cfg)


# -------------------------------------------------------------------------- #
#
#                          Integrated Filters
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsIntegratedFilters(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'integrated'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR ,'{}.fq'.format(cls._prefix))
        cls._cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'integrated_barcode_map.txt')
        cls._cfg['fastq']['filters']['max N'] = 0
        cls._cfg['fastq']['filters']['chastity'] = True
        cls._cfg['fastq']['filters']['avg quality'] = 38
        cls._cfg['fastq']['filters']['min quality'] = 20
        cls._cfg['fastq']['start'] = 4
        cls._cfg['fastq']['length'] = 3
        cls._cfg['fastq']['reverse'] = True
        cls._cfg['barcodes']['min count'] = 2
        cls._cfg['identifiers']['min count'] = 3
        cls._obj = make_libarary(cls._cfg)

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    @property
    def store(self):
        return self._obj.store

    def test_main(self):
        driver = HDF5Verifier()
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                      Barcode Min Count Filter
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsBarcodeMinCountSetting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'barcode_mincount'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(cls._prefix))
        cls._cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'barcode_map.txt')
        cls._cfg['barcodes']['min count'] = 2
        cls._obj = make_libarary(cls._cfg)

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    @property
    def store(self):
        return self._obj.store

    def test_main(self):
        driver = HDF5Verifier()
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                      Counts Only Mode
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsCountsOnlyMode(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'counts_only'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['counts file'] = "{}/{}".format(
            READS_DIR , '{}.tsv'.format(cls._prefix))
        cls._cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'barcode_map.txt')
        cls._obj = make_libarary(cls._cfg)

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    @property
    def store(self):
        return self._obj.store

    def test_main(self):
        driver = HDF5Verifier()
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                      Average Qual FASTQ Filter
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsAvgQualFQFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'filter_avgq'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(cls._prefix))
        cls._cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'barcode_map.txt')
        cls._cfg['fastq']['filters']['avg quality'] = 38
        cls._obj = make_libarary(cls._cfg)

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    @property
    def store(self):
        return self._obj.store

    def test_main(self):
        driver = HDF5Verifier()
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                      Max N FASTQ Filter
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsMaxNFQFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'filter_maxn'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(cls._prefix))
        cls._cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'barcode_map.txt')
        cls._cfg['fastq']['filters']['max N'] = 0
        cls._obj = make_libarary(cls._cfg)

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    @property
    def store(self):
        return self._obj.store

    def test_main(self):
        driver = HDF5Verifier()
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                      Min Quality FASTQ Filter
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsMinQualFQFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'filter_minq'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(cls._prefix))
        cls._cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'barcode_map.txt')
        cls._cfg['fastq']['filters']['min quality'] = 20
        cls._obj = make_libarary(cls._cfg)

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    @property
    def store(self):
        return self._obj.store

    def test_main(self):
        driver = HDF5Verifier()
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                      Not Chaste FASTQ Filter
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsNotChasteFQFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'filter_not_chaste'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(cls._prefix))
        cls._cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'barcode_map.txt')
        cls._cfg['fastq']['filters']['chastity'] = True
        cls._obj = make_libarary(cls._cfg)

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    @property
    def store(self):
        return self._obj.store

    def test_main(self):
        driver = HDF5Verifier()
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                      Identifiers Min Count Filter
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsWithIdentifiersMinCountFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'identifiers_mincount'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(cls._prefix))
        cls._cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'barcode_map.txt')
        cls._cfg['identifiers']['min count'] = 2
        cls._obj = make_libarary(cls._cfg)

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    @property
    def store(self):
        return self._obj.store

    def test_main(self):
        driver = HDF5Verifier()
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                      Reverse Completement Setting On
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsWithRevCompSetting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'revcomp'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(cls._prefix))
        cls._cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'revcomp_barcode_map.txt')
        cls._cfg['fastq']['reverse'] = True
        cls._obj = make_libarary(cls._cfg)

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    @property
    def store(self):
        return self._obj.store

    def test_main(self):
        driver = HDF5Verifier()
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                      Trim Length Setting
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsWithTrimLengthSetting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'trim_len'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(cls._prefix))
        cls._cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'trim_len_barcode_map.txt')
        cls._cfg['fastq']['length'] = 3
        cls._obj = make_libarary(cls._cfg)

        print_groups(cls._obj.store)

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    @property
    def store(self):
        return self._obj.store

    def test_main(self):
        driver = HDF5Verifier()
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                      Trim Start Setting
#
# -------------------------------------------------------------------------- #
class TestBcidSeqLibCountsWithTrimStartSetting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'trim_start'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = "{}/{}".format(
            READS_DIR , '{}.fq'.format(cls._prefix))
        cls._cfg['barcodes']['map file'] = "{}/{}".format(
            READS_DIR, 'trim_start_barcode_map.txt')
        cls._cfg['fastq']['start'] = 4
        cls._obj = make_libarary(cls._cfg)

        print_groups(cls._obj.store)

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        os.rmdir(cls._obj.output_dir)

    @property
    def store(self):
        return self._obj.store

    def test_main(self):
        driver = HDF5Verifier()
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                                   MAIN
#
# -------------------------------------------------------------------------- #
if __name__ == "__main__":
    unittest.main()
