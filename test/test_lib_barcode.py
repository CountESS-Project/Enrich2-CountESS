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
import shutil
import unittest
import os.path

from test.utilities import load_config_data, load_df_from_txt
from test.utilities import print_groups, single_column_df_equal
from enrich2.libraries.barcode import BarcodeSeqLib


# -------------------------------------------------------------------------- #
#
#                           UTILTIES
#
# -------------------------------------------------------------------------- #
def make_libarary(cfg, **kwargs):
    obj = BarcodeSeqLib()
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
            self.test_filter_stats()
            self.test_serialize()
        self.test_raw_barcode_count()
        self.test_main_barcode_count()

    def test_main_barcode_count(self):
        expected = load_df_from_txt(
            'barcode/{}_main_barcodes_counts.tsv'.format(self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/main/barcodes/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_raw_barcode_count(self):
        expected = load_df_from_txt(
            'barcode/{}_raw_barcodes_counts.tsv'.format(self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/raw/barcodes/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_filter_stats(self):
        expected = load_df_from_txt(
            'barcode/{}_raw_filter.tsv'.format(self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/raw/filter']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_serialize(self):
        cfg = self.test_class._obj.serialize()
        self.test_class.assertTrue(self.test_class._cfg == cfg)


# -------------------------------------------------------------------------- #
#
#                   BARCODE INTEGRATED COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibCountsIntegratedFilters(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("barcode/barcode_only.json")
        cls._cfg['fastq']['reads'] = 'data/reads/barcode/integrated.fq'
        cls._cfg['fastq']['filters']['max N'] = 0
        cls._cfg['fastq']['filters']['chastity'] = True
        cls._cfg['fastq']['filters']['avg quality'] = 38
        cls._cfg['fastq']['filters']['min quality'] = 20
        cls._cfg['fastq']['start'] = 4
        cls._cfg['fastq']['length'] = 3
        cls._cfg['fastq']['reverse'] = True
        cls._cfg['barcodes']['min count'] = 2
        cls._obj = make_libarary(cls._cfg)

    @classmethod
    def tearDownClass(cls):
        cls._obj.store_close(children=True)
        os.remove(cls._obj.store_path)
        shutil.rmtree(cls._obj.output_dir)

    @property
    def store(self):
        return self._obj.store

    def test_main(self):
        driver = HDF5Verifier()
        driver(self, file_prefix='integrated', sep=';')


# -------------------------------------------------------------------------- #
#
#                   BARCODE MINCOUNT COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibCountWithBarcodeMinCountSetting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("barcode/barcode_only.json")
        cls._cfg['fastq']['reads'] = 'data/reads/barcode/barcode_mincount.fq'
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
        driver(self, file_prefix='barcode_mincount', sep=';')


# -------------------------------------------------------------------------- #
#
#                BARCODE COUNTS ONLY MODE COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibCountCountsOnlyMode(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("barcode/barcode_only.json")
        cls._cfg['counts file'] = 'data/reads/barcode/counts_only.tsv'
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
        driver(self, file_prefix='counts_only', sep=';')


# -------------------------------------------------------------------------- #
#
#                FASTQ FILTER AVERAGE QUALITY
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibWithAvgQualityFQFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("barcode/barcode_only.json")
        cls._cfg['fastq']['reads'] = 'data/reads/barcode/filter_avgq.fq'
        cls._cfg['fastq']['filters']['avg quality'] = 39
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
        driver(self, file_prefix='filter_avgq', sep=';')


# -------------------------------------------------------------------------- #
#
#                           FASTQ FILTER MAX N
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibWithMaxNFQFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("barcode/barcode_only.json")
        cls._cfg['fastq']['reads'] = 'data/reads/barcode/filter_maxn.fq'
        cls._cfg['fastq']['filters']['max N'] = 1
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
        driver(self, file_prefix='filter_maxn', sep=';')


# -------------------------------------------------------------------------- #
#
#                           FASTQ FILTER MIN QUALITY
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibWithMinQualFQFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("barcode/barcode_only.json")
        cls._cfg['fastq']['reads'] = 'data/reads/barcode/filter_minq.fq'
        cls._cfg['fastq']['filters']['min quality'] = 38
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
        driver(self, file_prefix='filter_minq', sep=';')


# -------------------------------------------------------------------------- #
#
#                           FASTQ FILTER NOT CHASTE
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibWithChastityFQFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("barcode/barcode_only.json")
        cls._cfg['fastq'][
            'reads'] = 'data/reads/barcode/filter_not_chaste.fq'
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
        driver(self, file_prefix='filter_not_chaste', sep=';')


# -------------------------------------------------------------------------- #
#
#                          USE REVCOMP
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibWithRevcompSetting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("barcode/barcode_only.json")
        cls._cfg['fastq']['reads'] = 'data/reads/barcode/revcomp.fq'
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
        driver(self, file_prefix='revcomp', sep=';')


# -------------------------------------------------------------------------- #
#
#                       USE TRIM LENGTH SETTING
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibWithTrimStartSetting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("barcode/barcode_only.json")
        cls._cfg['fastq']['reads'] = 'data/reads/barcode/trim_start.fq'
        cls._cfg['fastq']['start'] = 4
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
        driver(self, file_prefix='trim_start', sep=';')


# -------------------------------------------------------------------------- #
#
#                        USE TRIM LENGTH SETTING
#
# -------------------------------------------------------------------------- #
class TestBarcodeSeqLibWithTrimLenSetting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("barcode/barcode_only.json")
        cls._cfg['fastq']['reads'] = 'data/reads/barcode/trim_len.fq'
        cls._cfg['fastq']['length'] = 5
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
        driver(self, file_prefix='trim_len', sep=';')


# -------------------------------------------------------------------------- #
#
#                                   MAIN
#
# -------------------------------------------------------------------------- #
if __name__ == "__main__":
    unittest.main()
