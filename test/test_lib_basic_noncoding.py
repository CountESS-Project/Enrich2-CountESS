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

from test.utilities import load_config_data, load_result_df
from test.utilities import single_column_df_equal, print_groups
from enrich2.libraries.basic import BasicSeqLib


# -------------------------------------------------------------------------- #
#
#                           GENERAIC TEST DRIVER
#
# -------------------------------------------------------------------------- #
def make_libarary(cfg, **kwargs):
    obj = BasicSeqLib()
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

    def __call__(self, test_class, file_prefix, coding_prefix, sep=';'):
        self.test_class = test_class
        self.file_prefix = file_prefix
        self.coding_prefix = coding_prefix
        self.prefix = "{}_{}".format(coding_prefix, file_prefix)
        self.sep = sep
        self.test_filter_stats()
        if coding_prefix == 'c':
            self.test_main_syn_count()
        self.test_main_variant_count()
        self.test_raw_variant_count()

    def test_main_variant_count(self):
        expected = load_result_df(
            'basic/{}_main_variants_count.tsv'.format(self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/main/variants/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_raw_variant_count(self):
        expected = load_result_df(
            'basic/{}_raw_variants_count.tsv'.format(self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/raw/variants/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_filter_stats(self):
        expected = load_result_df(
            'basic/{}_stats.tsv'.format(self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/raw/filter']
        self.test_class.assertTrue(single_column_df_equal(expected, result))

    def test_main_syn_count(self):
        expected = load_result_df(
            'basic/{}_main_syn_count.tsv'.format(self.prefix),
            sep=self.sep
        )
        result = self.test_class.store['/main/synonymous/counts']
        self.test_class.assertTrue(single_column_df_equal(expected, result))


# -------------------------------------------------------------------------- #
#
#                           INTEGRATION COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsIntegrated(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/integrated.fq'

        # Set all filter parameters
        cls._cfg['fastq']['filters']['max N'] = 0
        cls._cfg['fastq']['filters']['chastity'] = True
        cls._cfg['fastq']['filters']['avg quality'] = 38
        cls._cfg['fastq']['filters']['min quality'] = 20

        # Set trim parameters
        cls._cfg['fastq']['start'] = 4
        cls._cfg['fastq']['length'] = 3
        cls._cfg['fastq']['reverse'] = True
        cls._cfg['variants']['wild type']['sequence'] = "TTT"

        # Set Variant parameters
        cls._cfg['variants']['wild type']['reference offset'] = 5
        cls._cfg['variants']['min count'] = 2
        cls._cfg['variants']['max mutations'] = 1
        cls._cfg['variants']['use aligner'] = True

        cls._obj = BasicSeqLib()
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
        driver(self, coding_prefix='n', file_prefix='integrated', sep=';')


# -------------------------------------------------------------------------- #
#
#                   SYNONYMOUS COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsSynonymous(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/synonymous.fq'
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
        driver(self, coding_prefix='n', file_prefix='synonymous', sep=';')


# -------------------------------------------------------------------------- #
#
#                   SINGLE MUTATION COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsSingleMutation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/single_mutation.fq'
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
        driver(self, coding_prefix='n', file_prefix='single_mut', sep=';')


# -------------------------------------------------------------------------- #
#
#                   MULTIMUTATION COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsMultiMutation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/multi_mutation.fq'
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
        driver(self, coding_prefix='n', file_prefix='multi_mut', sep=';')


# -------------------------------------------------------------------------- #
#
#                   WILDTYPE COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWildType(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/wildtype.fq'
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
        driver(self, coding_prefix='n', file_prefix='wildtype', sep=';')


# -------------------------------------------------------------------------- #
#
#                   FASTQ MAXN FILTER COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithMaxNFQFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/max_n.fq'
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
        driver(self, coding_prefix='n', file_prefix='filter_maxn', sep=';')


# -------------------------------------------------------------------------- #
#
#                   FASTQ CHASTE FILTER COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithChaste(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/not_chaste_reads.fq'
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
        driver(self, coding_prefix='n', file_prefix='filter_chastity', sep=';')


# -------------------------------------------------------------------------- #
#
#                    FASTQ MIN QUAL FILTER COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithMinQualFQFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/min_quality.fq'
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
        driver(self, coding_prefix='n', file_prefix='filter_minq', sep=';')


# -------------------------------------------------------------------------- #
#
#                    FASTQ AVG QUAL FILTER COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithAvgQualFQFilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/avg_quality.fq'
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
        driver(self, coding_prefix='n', file_prefix='filter_avgq', sep=';')


# -------------------------------------------------------------------------- #
#
#                    FASTQ TRIM LENGTH COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsTrimLengthSetting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/trim_len.fq'
        cls._cfg['fastq']['length'] = 3
        cls._cfg['variants']['wild type']['sequence'] = "AAA"
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
        driver(self, coding_prefix='n', file_prefix='trim_len', sep=';')


# -------------------------------------------------------------------------- #
#
#                    FASTQ TRIM START COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsTrimStartSetting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/trim_start.fq'
        cls._cfg['fastq']['start'] = 4
        cls._cfg['variants']['wild type']['sequence'] = "AAA"
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
        driver(self, coding_prefix='n', file_prefix='trim_start', sep=';')


# -------------------------------------------------------------------------- #
#
#                    FASTQ REVERSE COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsReverseSetting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/reverse_complement.fq'
        cls._cfg['fastq']['reverse'] = True
        cls._cfg['variants']['wild type']['sequence'] = "TTTTTT"
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
        driver(self, coding_prefix='n', file_prefix='revcomp', sep=';')


# -------------------------------------------------------------------------- #
#
#                    VARIANT WT-OFFSET COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithRefOffset(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/reference_offset.fq'
        cls._cfg['variants']['wild type']['reference offset'] = 6
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
        driver(self, coding_prefix='n', file_prefix='wtoffset', sep=';')


# -------------------------------------------------------------------------- #
#
#                    VARIANT WT-OFFSET COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithRefOffsetNotMultipleOfThree(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq'][
            'reads'] = 'data/reads/basic/reference_offset.fq'
        cls._cfg['variants']['wild type']['reference offset'] = 5
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
        driver(self, coding_prefix='n', file_prefix='wtoffset_not_multiple',
               sep=';')


# -------------------------------------------------------------------------- #
#
#                    VARIANT MIN COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithVariantMinCount(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/min_count.fq'
        cls._cfg['variants']['min count'] = 2
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
        driver(self, coding_prefix='n',
               file_prefix='variant_mincount', sep=';')


# -------------------------------------------------------------------------- #
#
#                    VARIANT MAX MUTATIONS COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithVariantMaxMutations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/max_mutations.fq'
        cls._cfg['variants']['max mutations'] = 1
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
        driver(self, coding_prefix='n',
               file_prefix='variant_maxmutations', sep=';')


# -------------------------------------------------------------------------- #
#
#                    VARIANT ALIGNER COUNT TESTING
#
# -------------------------------------------------------------------------- #
class TestBasicSeqLibCountsWithVariantAligner(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cfg = load_config_data("basic/basic_noncoding.json")
        cls._cfg['fastq']['reads'] = 'data/reads/basic/use_aligner.fq'
        cls._cfg['variants']['use aligner'] = True
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
        driver(self, coding_prefix='n',
               file_prefix='use_aligner', sep=';')


# -------------------------------------------------------------------------- #
#
#                                   MAIN
#
# -------------------------------------------------------------------------- #
if __name__ == "__main__":
    unittest.main()