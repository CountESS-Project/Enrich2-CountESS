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
from test.utilities import single_column_df_equal, print_groups
from enrich2.libraries.barcodevariant import BcvSeqLib


CFG_PATH = "barcodevariant/barcode_variant.json"
READS_DIR = "data/reads/barcodevariant"
RESULT_DIR = "barcodevariant/"


# -------------------------------------------------------------------------- #
#
#                           GENERAIC TEST DRIVER
#
# -------------------------------------------------------------------------- #
def make_libarary(cfg, **kwargs):
    obj = BcvSeqLib()
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

    def __call__(self, test_class, file_prefix, coding_prefix='c', sep=';'):
        self.test_class = test_class
        self.file_prefix = file_prefix
        self.coding_prefix = coding_prefix
        self.prefix = "{}_{}".format(coding_prefix, file_prefix)
        self.sep = sep

        self.test_raw_barcode_map()
        self.test_raw_barcodes_counts()
        self.test_main_barcodes_counts()
        self.test_main_variant_count()

        if coding_prefix != 'n':
            self.test_main_syn_count()

        if file_prefix != 'counts_only':
            self.test_serialize()
            self.test_raw_filter()

    def test_raw_barcode_map(self):
        expected = load_df_from_txt(
            '{}/{}_raw_barcodemap.tsv'.format(RESULT_DIR, self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/raw/barcodemap']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_raw_filter(self):
        expected = load_df_from_txt(
            '{}/{}_raw_filter.tsv'.format(RESULT_DIR, self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/raw/filter']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_raw_barcodes_counts(self):
        expected = load_df_from_txt(
            '{}/{}_raw_barcodes_counts.tsv'.format(RESULT_DIR, self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/raw/barcodes/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_main_barcodes_counts(self):
        expected = load_df_from_txt(
            '{}/{}_main_barcodes_counts.tsv'.format(RESULT_DIR, self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/main/barcodes/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_main_syn_count(self):
        expected = load_df_from_txt(
            '{}/{}_main_syn_counts.tsv'.format(RESULT_DIR, self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/main/synonymous/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_main_variant_count(self):
        expected = load_df_from_txt(
            '{}/{}_main_variants_counts.tsv'.format(RESULT_DIR, self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/main/variants/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_serialize(self):
        cfg = self.test_class._obj.serialize()
        self.test_class.assertTrue(self.test_class._cfg == cfg)


# -------------------------------------------------------------------------- #
#
#                   Integrated Filter and Settings Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibCountsIntegrated(unittest.TestCase):
    """
    Integrated test of all of the libraries config settings at once.
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'integrated'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(
            READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/{}_barcode_map.txt".format(
            READS_DIR, cls._prefix)

        # Set all filter parameters
        cls._cfg['fastq']['filters']['max N'] = 0
        cls._cfg['fastq']['filters']['chastity'] = True
        cls._cfg['fastq']['filters']['avg quality'] = 38
        cls._cfg['fastq']['filters']['min quality'] = 20

        # Set trim parameters
        cls._cfg['fastq']['start'] = 4
        cls._cfg['fastq']['length'] = 3
        cls._cfg['fastq']['reverse'] = True

        # Set barcode parameters
        cls._cfg['barcodes']['min count'] = 2

        # # Set Variant parameters
        cls._cfg['variants']['wild type']['sequence'] = "TTTTTT"
        cls._cfg['variants']['wild type']['reference offset'] = 3
        cls._cfg['variants']['min count'] = 3
        cls._cfg['variants']['max mutations'] = 1
        cls._cfg['variants']['use aligner'] = True
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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                   Barcode Min Conut Filter Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibCountsBarcodesMinCountFilter(unittest.TestCase):
    """
    Test that barcodes with a minimum count under 2 are correctly removed
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'barcodes_mincount'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(
            READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/barcode_map.txt".format(
            READS_DIR)

        # Set barcode parameters
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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                          Counts Only Mode Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibCountsCountsOnlyMode(unittest.TestCase):
    """
    Test counts only mode correctly reads barcodes in from a tsv with
    count values column.
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'counts_only'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['counts file'] = '{}/{}.tsv'.format(
            READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/barcode_map.txt".format(
            READS_DIR)

        # Set barcode parameters
        cls._cfg['barcodes']['min count'] = 4
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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                          FQ Filter Avg Quality Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibCountsAvgQFQFilter(unittest.TestCase):
    """
    Test that the FQ Filter average quality setting works at removing
    barcodes with average base quality less than 39 (H)
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'filter_avgq'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(
            READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/barcode_map.txt".format(
            READS_DIR)

        # Set barcode parameters
        cls._cfg['fastq']['filters']['avg quality'] = 39
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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                          FQ Filter Min Quality Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibCountsMinQFQFilter(unittest.TestCase):
    """
    Test that the FQ Filter average quality setting works at removing
    barcodes with containing any base qualities less than 39 (H)
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'filter_minq'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(
            READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/barcode_map.txt".format(
            READS_DIR)

        # Set barcode parameters
        cls._cfg['fastq']['filters']['min quality'] = 39
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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                          FQ Filter Max N Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibCountsMaxNFQFilter(unittest.TestCase):
    """
    Test that the FQ Filter average quality setting works at removing
    barcodes with more than 0 N bases.
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'filter_maxn'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(
            READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/barcode_map.txt".format(
            READS_DIR)

        # Set barcode parameters
        cls._cfg['fastq']['filters']['max N'] = 0
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
        driver(self, file_prefix=self._prefix, sep=';')

# -------------------------------------------------------------------------- #
#
#                          FQ Filter Chastity Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibCountsNotChasteFQFilter(unittest.TestCase):
    """
    Test that the FQ Filter average quality setting works at removing
    barcodes that are not chaste.
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'filter_chastity'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(
            READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/barcode_map.txt".format(
            READS_DIR)

        # Set barcode parameters
        cls._cfg['fastq']['filters']['chastity'] = True
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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                          Detect Multi-Mutation Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibDetectMultiMutations(unittest.TestCase):
    """
    Test that barcodes with multiple mutations in the barcode map value
    are displayed correctly.
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'multi_mut'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(
            READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/{}_barcode_map.txt".format(
            READS_DIR, cls._prefix)

        # Set barcode parameters
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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                          Detect Single-Mutation Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibDetectSingleMutations(unittest.TestCase):
    """
    Test that barcodes with only a single mutation in the barcode map value
    are displayed correctly, as well as those with multiple mutations within
    a single codon.
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'single_mut'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(
            READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/{}_barcode_map.txt".format(
            READS_DIR, cls._prefix)

        # Set barcode parameters
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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                          FQ Reverse Complement Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibWithRevcomp(unittest.TestCase):
    """
    Test that the reverse complement function correctly applies to each barcode
    so that they can map to a barcode map and be counted properly.
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'revcomp'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(
            READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/{}_barcode_map.txt".format(
            READS_DIR, cls._prefix)

        # Set barcode parameters
        cls._cfg['fastq']['reverse'] = True
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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                         FQ Trim Length Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibWithTrimLengthAt3(unittest.TestCase):
    """
    Test that fq reads are trimmed to the correct length (3) beginning at the
    start of the fq read (pos 1).
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'trim_len'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(
            READS_DIR, cls._prefix)
        cls._cfg['barcodes'][
            'map file'] = "{}/{}_barcode_map.txt".format(
            READS_DIR, cls._prefix)

        # Set barcode parameters
        cls._cfg['fastq']['length'] = 3
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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                          FQ Trim Start Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibWithTrimStartAt4(unittest.TestCase):
    """
    Test that fq reads are trimmed at the correct starting position (pos 4)
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'trim_start'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(
            READS_DIR, cls._prefix)
        cls._cfg['barcodes'][
            'map file'] = "{}/{}_barcode_map.txt".format(
            READS_DIR, cls._prefix)

        # Set barcode parameters
        cls._cfg['fastq']['start'] = 4
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
        driver(self, file_prefix=self._prefix, sep=';')

# -------------------------------------------------------------------------- #
#
#                          Synonymous Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibDetectSynonymous(unittest.TestCase):
    """
    Test that synonymous mutations are correctly detected
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'synonymous'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(
            READS_DIR, cls._prefix)
        cls._cfg['barcodes'][
            'map file'] = "{}/{}_barcode_map.txt".format(
            READS_DIR, cls._prefix)

        # Set barcode parameters
        cls._cfg['variants']['wild type']['sequence'] = 'CCTCCT'
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
        driver(self, file_prefix=self._prefix, sep=';')



# -------------------------------------------------------------------------- #
#
#                          Detect WildType Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibDetectWildtype(unittest.TestCase):
    """
    Test that non-variants are correctly detected
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'wildtype'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/barcode_map.txt".format(
            READS_DIR)

        # Set barcode parameters
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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                          Variant Max mutations filter
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibWithVariantMaxMutationsFilter(unittest.TestCase):
    """
    Test that variants with more than one mutation are filtered out, even
    those with multiple mutations on a single codon.
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'variant_maxmutations'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/barcode_map.txt".format(
            READS_DIR)

        # Set barcode parameters
        cls._cfg['variants']['max mutations'] = 1
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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                          Variant Min Count Filter
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibWithVariantMinCountFilter(unittest.TestCase):
    """
    Test that variants with less than a count of 2 are removed.
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'variant_mincount'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/barcode_map.txt".format(
            READS_DIR)

        # Set barcode parameters
        cls._cfg['variants']['min count'] = 2
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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                          Variant With Reference Offset
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibWithReferenceOffset(unittest.TestCase):
    """
    Test that variants are reported with the offset added correctly to
    nucleotide and residue locations.
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'variant_refoffset'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/barcode_map.txt".format(
            READS_DIR)

        # Set barcode parameters
        cls._cfg['variants']['wild type']['reference offset'] = 3
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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                     Variant With Use Aligner Setting
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibWithUseAlignerSetting(unittest.TestCase):
    """
    Test that variants are reported correctly wrt the wildtype sequence
    when using alignment.
    """

    @classmethod
    def setUpClass(cls):
        cls._prefix = 'variant_use_aligner'
        cls._cfg = load_config_data(CFG_PATH)
        cls._cfg['fastq']['reads'] = '{}/{}.fq'.format(READS_DIR, cls._prefix)
        cls._cfg['barcodes']['map file'] = "{}/{}_barcode_map.txt".format(
            READS_DIR, cls._prefix)

        # Set barcode parameters
        cls._cfg['variants']['use aligner'] = True
        cls._obj = make_libarary(cls._cfg)
        print_groups(cls._obj.store)

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
        driver(self, file_prefix=self._prefix, sep=';')


# -------------------------------------------------------------------------- #
#
#                                   MAIN
#
# -------------------------------------------------------------------------- #
if __name__ == "__main__":
    unittest.main()