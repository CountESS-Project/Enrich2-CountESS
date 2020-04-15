import os
import sys
import shutil
import json
from unittest import TestCase

from ..config.types import *
from ..base.config_constants import *


# -------------------------------------------------------------------------- #
#
#                      Library Configuration Classes
#
# -------------------------------------------------------------------------- #
class BaseLibraryConfigTest(TestCase):
    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.plugin_dir = os.path.join(current_wd, "data/plugins")
        self.data_dir = os.path.join(current_wd, "data/config_check")

        self.fastq_cfg = {
            READS: os.path.join(self.data_dir, "polyA_t0.fq"),
            REVERSE: True,
            FILTERS: {
                FILTERS_CHASTITY: True,
                FILTERS_MAX_N: 2,
                FILTERS_MIN_Q: 10,
                FILTERS_AVG_Q: 10,
            },
        }

        self.basic_cfg = {
            COUNTS_FILE: None,
            IDENTIFIERS: {},
            NAME: "BaseLibStoreTest",
            REPORT_FILTERED_READS: False,
            TIMEPOINT: 0,
        }

    def tearDown(self):
        pass

    def test_error_name_not_in_cfg(self):
        cfg = {}
        with self.assertRaises(KeyError):
            BaseLibraryConfiguration(cfg).validate()

    def test_error_timepoint_not_in_cfg(self):
        cfg = {NAME: "BaseLibStoreTest"}
        with self.assertRaises(KeyError):
            BaseLibraryConfiguration(cfg).validate()

    def test_error_report_filtered_reads_not_in_cfg(self):
        cfg = {NAME: "BaseLibStoreTest", TIMEPOINT: 0}
        with self.assertRaises(KeyError):
            BaseLibraryConfiguration(cfg).validate()

    def test_error_invalid_timepoint_in_cfg(self):
        cfg = self.basic_cfg.copy()
        cfg[FASTQ] = self.fastq_cfg
        cfg[TIMEPOINT] = "1"
        with self.assertRaises(TypeError):
            BaseLibraryConfiguration(cfg).validate()

        cfg[TIMEPOINT] = -1
        with self.assertRaises(ValueError):
            BaseLibraryConfiguration(cfg).validate()

    def test_error_report_filtered_reads_not_bool(self):
        cfg = self.basic_cfg.copy()
        cfg[REPORT_FILTERED_READS] = "True"
        cfg[FASTQ] = self.fastq_cfg
        with self.assertRaises(TypeError):
            BaseLibraryConfiguration(cfg).validate()

    def test_error_invalid_counts_file(self):
        cfg = self.basic_cfg.copy()
        cfg[COUNTS_FILE] = os.path.join(self.data_dir, "testhdf5.h5")
        with self.assertRaises(IOError):
            BaseLibraryConfiguration(cfg).validate()

        cfg[COUNTS_FILE] = os.path.join(self.data_dir, "not_a_file")
        with self.assertRaises(IOError):
            BaseLibraryConfiguration(cfg).validate()

    def test_defaults_load_correctly(self):
        path = os.path.join(self.data_dir, "barcode_map.txt")
        cfg = self.basic_cfg.copy()
        cfg[COUNTS_FILE] = path

        base_cfg = BaseLibraryConfiguration(cfg).validate()
        self.assertEqual(base_cfg.seqlib_type, "IdOnlySeqLib")
        self.assertEqual(base_cfg.report_filtered_reads, False)
        self.assertEqual(base_cfg.timepoint, 0)
        self.assertEqual(base_cfg.counts_file, path)
        self.assertEqual(base_cfg.store_cfg.name, "BaseLibStoreTest")
        self.assertEqual(base_cfg.fastq_cfg, None)

    def test_override_defaults_correctly(self):
        cfg = self.basic_cfg.copy()
        cfg[REPORT_FILTERED_READS] = True
        cfg[TIMEPOINT] = 1
        cfg[FASTQ] = self.fastq_cfg

        base_cfg = BaseLibraryConfiguration(cfg, init_fastq=True).validate()
        self.assertEqual(base_cfg.seqlib_type, "IdOnlySeqLib")
        self.assertEqual(base_cfg.report_filtered_reads, True)
        self.assertEqual(base_cfg.timepoint, 1)
        self.assertEqual(base_cfg.counts_file, None)
        self.assertEqual(base_cfg.store_cfg.name, "BaseLibStoreTest")

        self.assertEqual(
            base_cfg.fastq_cfg.reads, os.path.join(self.data_dir, "polyA_t0.fq")
        )
        self.assertEqual(base_cfg.fastq_cfg.reverse, True)
        self.assertEqual(base_cfg.fastq_cfg.trim_start, 1)
        self.assertEqual(base_cfg.fastq_cfg.trim_length, sys.maxsize)

        self.assertEqual(base_cfg.fastq_cfg.filters_cfg.chaste, True)
        self.assertEqual(base_cfg.fastq_cfg.filters_cfg.max_n, 2)
        self.assertEqual(base_cfg.fastq_cfg.filters_cfg.avg_base_quality, 10)
        self.assertEqual(base_cfg.fastq_cfg.filters_cfg.min_base_quality, 10)

    def test_error_have_both_counts_file_and_reads_file(self):
        path = os.path.join(self.data_dir, "polyA_t0.txt")
        cfg = self.basic_cfg.copy()
        cfg[COUNTS_FILE] = path
        cfg[FASTQ] = self.fastq_cfg
        with self.assertRaises(ValueError):
            BaseLibraryConfiguration(cfg, init_fastq=True).validate()

    def test_error_have_init_fastq_but_no_fastq(self):
        with self.assertRaises(KeyError):
            BaseLibraryConfiguration(self.basic_cfg, init_fastq=True).validate()

    def test_error_have_not_init_fastq_but_no_counts(self):
        cfg = {
            IDENTIFIERS: {},
            NAME: "BaseLibStoreTest",
            REPORT_FILTERED_READS: False,
            TIMEPOINT: 0,
        }
        with self.assertRaises(KeyError):
            BaseLibraryConfiguration(cfg, init_fastq=False).validate()

    def test_correct_seqlib_type(self):
        idonly = json.load(open(os.path.join(self.data_dir, "idonly.json"), "r"))
        idonly[COUNTS_FILE] = os.path.join(self.data_dir, "polyA_t0.txt")
        base_cfg = BaseLibraryConfiguration(idonly).validate()
        self.assertEqual(base_cfg.seqlib_type, "IdOnlySeqLib")

        basic = json.load(open(os.path.join(self.data_dir, "basic_coding.json"), "r"))
        basic[FASTQ][READS] = os.path.join(self.data_dir, "polyA_t0.fq")
        base_cfg = BaseLibraryConfiguration(basic, init_fastq=True).validate()
        self.assertEqual(base_cfg.seqlib_type, "BasicSeqLib")

        barcode = json.load(open(os.path.join(self.data_dir, "barcode.json"), "r"))
        barcode[FASTQ][READS] = os.path.join(self.data_dir, "polyA_t0.fq")
        base_cfg = BaseLibraryConfiguration(barcode, init_fastq=True).validate()
        self.assertEqual(base_cfg.seqlib_type, "BarcodeSeqLib")

        barcodeid = json.load(open(os.path.join(self.data_dir, "barcodeid.json"), "r"))
        barcodeid[BARCODES][BARCODE_MAP_FILE] = os.path.join(
            self.data_dir, "barcode_map.txt"
        )
        barcodeid[FASTQ][READS] = os.path.join(self.data_dir, "polyA_t0.fq")
        base_cfg = BaseLibraryConfiguration(barcodeid, init_fastq=True).validate()
        self.assertEqual(base_cfg.seqlib_type, "BcidSeqLib")

        barcodevar = json.load(
            open(os.path.join(self.data_dir, "barcodevariant_coding.json"), "r")
        )
        barcodevar[BARCODES][BARCODE_MAP_FILE] = os.path.join(
            self.data_dir, "barcode_map.txt"
        )
        barcodevar[FASTQ][READS] = os.path.join(self.data_dir, "polyA_t0.fq")
        base_cfg = BaseLibraryConfiguration(barcodevar, init_fastq=True).validate()
        self.assertEqual(base_cfg.seqlib_type, "BcvSeqLib")

        path = os.path.join(self.data_dir, "../../../../test_output/")
        shutil.rmtree(path)


class BasicSeqLibConfigTest(TestCase):
    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.data_dir = os.path.join(current_wd, "data/config_check")
        self.variants_cfg = {WILDTYPE: {SEQUENCE: "AAA"}}
        self.fastq_cfg = {
            READS: os.path.join(self.data_dir, "polyA_t0.fq"),
            FILTERS: {},
        }
        self.basic_cfg = {
            FASTQ: self.fastq_cfg,
            VARIANTS: self.variants_cfg,
            NAME: "BasicTest",
            TIMEPOINT: 0,
            REPORT_FILTERED_READS: False,
        }

    def tearDown(self):
        pass

    def test_minimal_config_loads_correctly(self):
        cfg = BasicSeqLibConfiguration(self.basic_cfg, init_fastq=True)
        self.assertEqual(cfg.timepoint, 0)
        self.assertEqual(cfg.counts_file, None)
        self.assertEqual(cfg.seqlib_type, "BasicSeqLib")
        self.assertEqual(cfg.report_filtered_reads, False)

        self.assertEqual(cfg.store_cfg.name, "BasicTest")
        self.assertEqual(cfg.store_cfg.has_store_path, False)
        self.assertEqual(cfg.store_cfg.store_path, "")
        self.assertEqual(cfg.store_cfg.has_output_dir, False)
        self.assertEqual(cfg.store_cfg.output_dir, "")
        self.assertEqual(cfg.store_cfg.has_scorer, False)
        self.assertEqual(cfg.store_cfg.scorer_cfg, None)

        self.assertEqual(cfg.variants_cfg.max_mutations, 10)
        self.assertEqual(cfg.variants_cfg.min_count, 0)
        self.assertEqual(cfg.variants_cfg.use_aligner, False)
        self.assertEqual(cfg.variants_cfg.wildtype_cfg.sequence, "AAA")
        self.assertEqual(cfg.variants_cfg.wildtype_cfg.coding, False)
        self.assertEqual(cfg.variants_cfg.wildtype_cfg.reference_offset, 0)

        self.assertEqual(cfg.fastq_cfg.reverse, False)
        self.assertEqual(cfg.fastq_cfg.trim_start, 1)
        self.assertEqual(cfg.fastq_cfg.trim_length, sys.maxsize)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.chaste, False)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.max_n, sys.maxsize)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.avg_base_quality, 0)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.min_base_quality, 0)
        self.assertEqual(
            cfg.fastq_cfg.reads, os.path.join(self.data_dir, "polyA_t0.fq")
        )


class IdOnlySeqlibTest(TestCase):
    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.data_dir = os.path.join(current_wd, "data/config_check")
        self.cfg = {
            COUNTS_FILE: os.path.join(self.data_dir, "polyA_t0.txt"),
            IDENTIFIERS: {},
            NAME: "IdonlyTest",
            TIMEPOINT: 0,
            REPORT_FILTERED_READS: False,
        }

    def tearDown(self):
        pass

    def test_minimal_config_loads_correctly(self):
        cfg = IdOnlySeqLibConfiguration(self.cfg)
        self.assertEqual(cfg.timepoint, 0)
        self.assertEqual(cfg.seqlib_type, "IdOnlySeqLib")
        self.assertEqual(cfg.report_filtered_reads, False)

        self.assertEqual(cfg.store_cfg.name, "IdonlyTest")
        self.assertEqual(cfg.store_cfg.has_store_path, False)
        self.assertEqual(cfg.store_cfg.store_path, "")
        self.assertEqual(cfg.store_cfg.has_output_dir, False)
        self.assertEqual(cfg.store_cfg.output_dir, "")
        self.assertEqual(cfg.store_cfg.has_scorer, False)
        self.assertEqual(cfg.store_cfg.scorer_cfg, None)

        self.assertEqual(cfg.identifiers_cfg.min_count, 0)


class BarcodeSeqLibConfigTest(TestCase):
    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.data_dir = os.path.join(current_wd, "data/config_check")
        self.fastq_cfg = {
            READS: os.path.join(self.data_dir, "polyA_t0.fq"),
            FILTERS: {},
        }
        self.basic_cfg = {
            FASTQ: self.fastq_cfg,
            BARCODES: {},
            NAME: "BarcodeSeqLib",
            TIMEPOINT: 0,
            REPORT_FILTERED_READS: False,
        }

    def tearDown(self):
        pass

    def test_minimal_config_loads_correctly(self):
        cfg = BarcodeSeqLibConfiguration(self.basic_cfg, init_fastq=True)
        self.assertEqual(cfg.timepoint, 0)
        self.assertEqual(cfg.counts_file, None)
        self.assertEqual(cfg.seqlib_type, "BarcodeSeqLib")
        self.assertEqual(cfg.report_filtered_reads, False)

        self.assertEqual(cfg.barcodes_cfg.barcodemap, None)
        self.assertEqual(cfg.barcodes_cfg.min_count, 0)

        self.assertEqual(cfg.store_cfg.name, "BarcodeSeqLib")
        self.assertEqual(cfg.store_cfg.has_store_path, False)
        self.assertEqual(cfg.store_cfg.store_path, "")
        self.assertEqual(cfg.store_cfg.has_output_dir, False)
        self.assertEqual(cfg.store_cfg.output_dir, "")
        self.assertEqual(cfg.store_cfg.has_scorer, False)
        self.assertEqual(cfg.store_cfg.scorer_cfg, None)

        self.assertEqual(cfg.fastq_cfg.reverse, False)
        self.assertEqual(cfg.fastq_cfg.trim_start, 1)
        self.assertEqual(cfg.fastq_cfg.trim_length, sys.maxsize)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.chaste, False)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.max_n, sys.maxsize)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.avg_base_quality, 0)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.min_base_quality, 0)
        self.assertEqual(
            cfg.fastq_cfg.reads, os.path.join(self.data_dir, "polyA_t0.fq")
        )


class BcidSeqLibConfigTest(TestCase):
    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.data_dir = os.path.join(current_wd, "data/config_check")
        self.map_path = os.path.join(self.data_dir, "barcode_map.txt")
        self.fastq_cfg = {
            READS: os.path.join(self.data_dir, "polyA_t0.fq"),
            FILTERS: {},
        }
        self.basic_cfg = {
            FASTQ: self.fastq_cfg,
            BARCODES: {BARCODE_MAP_FILE: self.map_path},
            IDENTIFIERS: {},
            NAME: "BcidSeqLib",
            TIMEPOINT: 0,
            REPORT_FILTERED_READS: False,
        }

    def tearDown(self):
        pass

    def test_minimal_config_loads_correctly(self):
        cfg = BcidSeqLibConfiguration(self.basic_cfg, init_fastq=True)
        self.assertEqual(cfg.timepoint, 0)
        self.assertEqual(cfg.counts_file, None)
        self.assertEqual(cfg.seqlib_type, "BcidSeqLib")
        self.assertEqual(cfg.report_filtered_reads, False)

        self.assertEqual(cfg.barcodes_cfg.map_file, self.map_path)
        self.assertEqual(cfg.barcodes_cfg.min_count, 0)

        self.assertEqual(cfg.identifers_cfg.min_count, 0)
        self.assertEqual(cfg.barcodes_cfg.map_file, self.map_path)
        self.assertEqual(cfg.barcodes_cfg.min_count, 0)

        self.assertEqual(cfg.store_cfg.name, "BcidSeqLib")
        self.assertEqual(cfg.store_cfg.has_store_path, False)
        self.assertEqual(cfg.store_cfg.store_path, "")
        self.assertEqual(cfg.store_cfg.has_output_dir, False)
        self.assertEqual(cfg.store_cfg.output_dir, "")
        self.assertEqual(cfg.store_cfg.has_scorer, False)
        self.assertEqual(cfg.store_cfg.scorer_cfg, None)

        self.assertEqual(cfg.fastq_cfg.reverse, False)
        self.assertEqual(cfg.fastq_cfg.trim_start, 1)
        self.assertEqual(cfg.fastq_cfg.trim_length, sys.maxsize)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.chaste, False)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.max_n, sys.maxsize)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.avg_base_quality, 0)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.min_base_quality, 0)
        self.assertEqual(
            cfg.fastq_cfg.reads, os.path.join(self.data_dir, "polyA_t0.fq")
        )


class BcvSeqLibConfigTest(TestCase):
    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.data_dir = os.path.join(current_wd, "data/config_check")
        self.map_path = os.path.join(self.data_dir, "barcode_map.txt")
        self.fastq_cfg = {
            READS: os.path.join(self.data_dir, "polyA_t0.fq"),
            FILTERS: {},
        }
        self.variants_cfg = {WILDTYPE: {SEQUENCE: "AAA"}}
        self.basic_cfg = {
            FASTQ: self.fastq_cfg,
            BARCODES: {BARCODE_MAP_FILE: self.map_path},
            VARIANTS: self.variants_cfg,
            NAME: "BcvSeqLib",
            TIMEPOINT: 0,
            REPORT_FILTERED_READS: False,
        }

    def tearDown(self):
        pass

    def test_minimal_config_loads_correctly(self):
        cfg = BcvSeqLibConfiguration(self.basic_cfg, init_fastq=True)
        self.assertEqual(cfg.timepoint, 0)
        self.assertEqual(cfg.counts_file, None)
        self.assertEqual(cfg.seqlib_type, "BcvSeqLib")
        self.assertEqual(cfg.report_filtered_reads, False)

        self.assertEqual(cfg.barcodes_cfg.map_file, self.map_path)
        self.assertEqual(cfg.barcodes_cfg.min_count, 0)

        self.assertEqual(cfg.variants_cfg.max_mutations, 10)
        self.assertEqual(cfg.variants_cfg.min_count, 0)
        self.assertEqual(cfg.variants_cfg.use_aligner, False)
        self.assertEqual(cfg.variants_cfg.wildtype_cfg.sequence, "AAA")
        self.assertEqual(cfg.variants_cfg.wildtype_cfg.coding, False)
        self.assertEqual(cfg.variants_cfg.wildtype_cfg.reference_offset, 0)

        self.assertEqual(cfg.barcodes_cfg.map_file, self.map_path)
        self.assertEqual(cfg.barcodes_cfg.min_count, 0)

        self.assertEqual(cfg.store_cfg.name, "BcvSeqLib")
        self.assertEqual(cfg.store_cfg.has_store_path, False)
        self.assertEqual(cfg.store_cfg.store_path, "")
        self.assertEqual(cfg.store_cfg.has_output_dir, False)
        self.assertEqual(cfg.store_cfg.output_dir, "")
        self.assertEqual(cfg.store_cfg.has_scorer, False)
        self.assertEqual(cfg.store_cfg.scorer_cfg, None)

        self.assertEqual(cfg.fastq_cfg.reverse, False)
        self.assertEqual(cfg.fastq_cfg.trim_start, 1)
        self.assertEqual(cfg.fastq_cfg.trim_length, sys.maxsize)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.chaste, False)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.max_n, sys.maxsize)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.avg_base_quality, 0)
        self.assertEqual(cfg.fastq_cfg.filters_cfg.min_base_quality, 0)
        self.assertEqual(
            cfg.fastq_cfg.reads, os.path.join(self.data_dir, "polyA_t0.fq")
        )
