import sys
import os
from unittest import TestCase

from ..config.types import *
from ..base.config_constants import *


# -------------------------------------------------------------------------- #
#
#                      Component Configuration Classes
#
# -------------------------------------------------------------------------- #
class ScorerConfigTest(TestCase):
    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.plugin_dir = os.path.join(current_wd, "data/plugins")

    def tearDown(self):
        pass

    def test_error_path_key_missing(self):
        cfg = {SCORER_OPTIONS: {}}
        with self.assertRaises(KeyError):
            ScorerConfiguration(cfg)

    def test_error_invalid_path(self):
        cfg = {SCORER_PATH: "", SCORER_OPTIONS: {}}
        with self.assertRaises(IOError):
            ScorerConfiguration(cfg)

    def test_error_options_key_missing(self):
        cfg = {SCORER_PATH: ""}
        with self.assertRaises(KeyError):
            ScorerConfiguration(cfg)

    def test_error_invalid_plugin_file(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "bad_scorer_incomplete.py"),
            SCORER_OPTIONS: {"logr_method": "wt", "weighted": False},
        }
        with self.assertRaises(ImportError):
            ScorerConfiguration(cfg)

        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "bad_options.py"),
            SCORER_OPTIONS: {"logr_method": "wt", "weighted": False},
        }
        with self.assertRaises(ImportError):
            ScorerConfiguration(cfg)

        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "non_python_file.txt"),
            SCORER_OPTIONS: {"logr_method": "wt", "weighted": False},
        }
        with self.assertRaises(IOError):
            ScorerConfiguration(cfg)

    def test_validate_valid_plugin(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "regression_scorer.py"),
            SCORER_OPTIONS: {"logr_method": "wt", "weighted": False},
        }
        scorer_cfg = ScorerConfiguration(cfg).validate()
        self.assertTrue(
            scorer_cfg.scorer_class_attrs, {"logr_method": "wt", "weighted": False}
        )
        self.assertTrue(scorer_cfg.scorer_class.name, "Regression")

    def test_warn_on_missing_options(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "regression_scorer.py"),
            SCORER_OPTIONS: {"logr_method": "wt"},
        }
        scorer_cfg = ScorerConfiguration(cfg).validate()
        self.assertTrue(
            scorer_cfg.scorer_class_attrs, {"logr_method": "wt", "weighted": True}
        )

    def test_error_on_unused_options(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "regression_scorer.py"),
            SCORER_OPTIONS: {"logr_method": "wt", "random_var": 1},
        }
        with self.assertRaises(ValueError):
            ScorerConfiguration(cfg).validate()

    def test_missing_options_default_correctly(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "regression_scorer.py"),
            SCORER_OPTIONS: {"weighted": True},
        }
        scorer_cfg = ScorerConfiguration(cfg).validate()
        self.assertTrue(
            scorer_cfg.scorer_class_attrs, {"logr_method": "wt", "weighted": True}
        )

    def test_options_override_defaults_correctly(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "regression_scorer.py"),
            SCORER_OPTIONS: {"logr_method": "complete", "weighted": False},
        }
        scorer_cfg = ScorerConfiguration(cfg).validate()
        self.assertTrue(
            scorer_cfg.scorer_class_attrs,
            {"logr_method": "complete", "weighted": False},
        )

    def test_loads_expected_scorer_class(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "regression_scorer.py"),
            SCORER_OPTIONS: {"logr_method": "complete", "weighted": False},
        }
        scorer_cfg = ScorerConfiguration(cfg).validate()
        self.assertTrue(scorer_cfg.scorer_class.name, "Regression")

    def test_empty_options_dict_defaults_correct(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "regression_scorer.py"),
            SCORER_OPTIONS: {},
        }
        scorer_cfg = ScorerConfiguration(cfg).validate()
        self.assertTrue(
            scorer_cfg.scorer_class_attrs, {"logr_method": "wt", "weighted": True}
        )

    def test_error_setting_options_with_incorrect_dtypes(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "regression_scorer.py"),
            SCORER_OPTIONS: {"weighted": 123},
        }
        with self.assertRaises(TypeError):
            ScorerConfiguration(cfg).validate()

    def test_error_setting_options_with_incorrect_choices(self):
        cfg = {
            SCORER_PATH: os.path.join(self.plugin_dir, "regression_scorer.py"),
            SCORER_OPTIONS: {"logr_method": "badkey", "weighted": True},
        }
        with self.assertRaises(ValueError):
            ScorerConfiguration(cfg).validate()


class FASTQConfigTest(TestCase):
    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.data_path = os.path.join(current_wd, "data/config_check")

    def tearDown(self):
        pass

    def test_error_missing_reads_key(self):
        cfg = {}
        with self.assertRaises(KeyError):
            FASTQConfiguration(cfg).validate()

    def test_defaults_load_correctly(self):
        cfg = {READS: os.path.join(self.data_path, "polyA_t0.fq")}
        fastq_cfg = FASTQConfiguration(cfg).validate()

        self.assertEqual(fastq_cfg.reverse, False)
        self.assertEqual(fastq_cfg.trim_start, 1)
        self.assertEqual(fastq_cfg.trim_length, sys.maxsize)

    def test_override_defaults_correctly(self):
        cfg = {
            READS: os.path.join(self.data_path, "polyA_t0.fq"),
            REVERSE: True,
            TRIM_START: 10,
            TRIM_LENGTH: 10,
        }
        fastq_cfg = FASTQConfiguration(cfg).validate()

        self.assertEqual(fastq_cfg.reverse, True)
        self.assertEqual(fastq_cfg.trim_start, 10)
        self.assertEqual(fastq_cfg.trim_length, 10)

    def test_error_non_bool_reverse(self):
        cfg = {READS: os.path.join(self.data_path, "polyA_t0.fq"), REVERSE: "str"}
        with self.assertRaises(TypeError):
            FASTQConfiguration(cfg).validate()

    def test_error_trim_len_start_not_int(self):
        cfg = {READS: os.path.join(self.data_path, "polyA_t0.fq"), TRIM_LENGTH: "str"}
        with self.assertRaises(TypeError):
            FASTQConfiguration(cfg).validate()

        cfg = {READS: os.path.join(self.data_path, "polyA_t0.fq"), TRIM_START: 6.5}
        with self.assertRaises(TypeError):
            FASTQConfiguration(cfg).validate()

    def test_error_trim_len_start_negative(self):
        cfg = {READS: os.path.join(self.data_path, "polyA_t0.fq"), TRIM_LENGTH: -190}
        with self.assertRaises(ValueError):
            FASTQConfiguration(cfg).validate()

        cfg = {READS: os.path.join(self.data_path, "polyA_t0.fq"), TRIM_START: -100}
        with self.assertRaises(ValueError):
            FASTQConfiguration(cfg).validate()

    def test_error_reads_path_not_string(self):
        cfg = {READS: {"a": 230}}
        with self.assertRaises(TypeError):
            FASTQConfiguration(cfg).validate()

    def test_error_reads_path_not_a_file(self):
        cfg = {READS: os.path.join(self.data_path, "/")}
        with self.assertRaises(IOError):
            FASTQConfiguration(cfg).validate()

    def test_error_reads_file_incorrect_ext(self):
        cfg = {READS: os.path.join(self.data_path, "polyA_t0.txt")}
        with self.assertRaises(IOError):
            FASTQConfiguration(cfg).validate()


class FiltersConfigTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_defaults_load_correctly(self):
        cfg = {}
        filters_cfg = FiltersConfiguration(cfg).validate()
        self.assertEqual(filters_cfg.chaste, False)
        self.assertEqual(filters_cfg.max_n, sys.maxsize)
        self.assertEqual(filters_cfg.avg_base_quality, 0)
        self.assertEqual(filters_cfg.min_base_quality, 0)

    def test_override_defaults_correctly(self):
        cfg = {
            FILTERS_CHASTITY: True,
            FILTERS_MAX_N: 10,
            FILTERS_AVG_Q: 20,
            FILTERS_MIN_Q: 30,
        }
        filters_cfg = FiltersConfiguration(cfg).validate()
        self.assertEqual(filters_cfg.chaste, True)
        self.assertEqual(filters_cfg.max_n, 10)
        self.assertEqual(filters_cfg.avg_base_quality, 20)
        self.assertEqual(filters_cfg.min_base_quality, 30)

    def test_error_maxn_not_int(self):
        cfg = {FILTERS_MAX_N: []}
        with self.assertRaises(TypeError):
            FiltersConfiguration(cfg).validate()

    def test_error_maxn_negative(self):
        cfg = {FILTERS_MAX_N: -12}
        with self.assertRaises(ValueError):
            FiltersConfiguration(cfg).validate()

    def test_error_avgq_not_int(self):
        cfg = {FILTERS_AVG_Q: 3.2}
        with self.assertRaises(TypeError):
            FiltersConfiguration(cfg).validate()

    def test_error_avgq_negative(self):
        cfg = {FILTERS_AVG_Q: -12}
        with self.assertRaises(ValueError):
            FiltersConfiguration(cfg).validate()

    def test_error_minq_not_int(self):
        cfg = {FILTERS_MIN_Q: set()}
        with self.assertRaises(TypeError):
            FiltersConfiguration(cfg).validate()

    def test_error_minq_negative(self):
        cfg = {FILTERS_MIN_Q: -12}
        with self.assertRaises(ValueError):
            FiltersConfiguration(cfg).validate()

    def test_error_chaste_not_bool(self):
        cfg = {FILTERS_CHASTITY: "str"}
        with self.assertRaises(TypeError):
            FiltersConfiguration(cfg).validate()


class BarcodeConfigTest(TestCase):
    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.data_path = os.path.join(current_wd, "data/config_check")

    def tearDown(self):
        pass

    def test_defaults_load_correctly(self):
        cfg = {BARCODE_MAP_FILE: os.path.join(self.data_path, "barcode_map.txt")}
        barcode_cfg = BarcodeConfiguration(cfg).validate()
        self.assertEqual(barcode_cfg.min_count, 0)

    def test_override_defaults_correctly(self):
        cfg = {
            BARCODE_MAP_FILE: os.path.join(self.data_path, "barcode_map.txt"),
            BARCODE_MIN_COUNT: 10,
        }
        barcode_cfg = BarcodeConfiguration(cfg).validate()
        self.assertEqual(barcode_cfg.min_count, 10)

    def test_error_no_barcode_map_when_requested(self):
        cfg = {}
        with self.assertRaises(ValueError):
            BarcodeConfiguration(cfg, require_map=True).validate()

    def test_error_minc_not_int(self):
        cfg = {BARCODE_MIN_COUNT: dict()}
        with self.assertRaises(TypeError):
            BarcodeConfiguration(cfg).validate()

    def test_error_minc_negative(self):
        cfg = {BARCODE_MIN_COUNT: -1}
        with self.assertRaises(ValueError):
            BarcodeConfiguration(cfg).validate()

    def test_error_mapfile_not_exist(self):
        cfg = {BARCODE_MAP_FILE: os.path.join(self.data_path, "i_dont_exist")}
        with self.assertRaises(IOError):
            BarcodeConfiguration(cfg).validate()

    def test_error_mapfile_not_str(self):
        cfg = {BARCODE_MAP_FILE: b"file"}
        with self.assertRaises(TypeError):
            BarcodeConfiguration(cfg).validate()

    def test_error_mapfile_invalid_ext(self):
        cfg = {BARCODE_MAP_FILE: os.path.join(self.data_path, "polyA_t0.fq")}
        with self.assertRaises(IOError):
            BarcodeConfiguration(cfg).validate()


class IdentifiersConfigTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_defaults_load_correctly(self):
        cfg = {}
        id_cfg = IdentifiersConfiguration(cfg).validate()
        self.assertEqual(id_cfg.min_count, 0)

    def test_override_defaults_correctly(self):
        cfg = {IDENTIFIERS_MIN_COUNT: 10}
        id_cfg = IdentifiersConfiguration(cfg).validate()
        self.assertEqual(id_cfg.min_count, 10)

    def test_error_min_count_not_int(self):
        cfg = {IDENTIFIERS_MIN_COUNT: dict()}
        with self.assertRaises(TypeError):
            IdentifiersConfiguration(cfg).validate()

    def test_error_min_count_negative(self):
        cfg = {IDENTIFIERS_MIN_COUNT: -10}
        with self.assertRaises(ValueError):
            IdentifiersConfiguration(cfg).validate()


class VariantsConfigTest(TestCase):
    def setUp(self):
        self.wt_cfg = {CODING: False, SEQUENCE: "AAAAAA", REF_OFFSET: 0}

    def tearDown(self):
        pass

    def test_error_wildtype_key_missing(self):
        cfg = {}
        with self.assertRaises(KeyError):
            VariantsConfiguration(cfg).validate()

    def test_defaults_load_correctly(self):
        cfg = {WILDTYPE: self.wt_cfg}
        v_cfg = VariantsConfiguration(cfg).validate()
        self.assertEqual(v_cfg.use_aligner, False)
        self.assertEqual(
            v_cfg.max_mutations, VariantsConfiguration.DEFAULT_MAX_MUTATIONS
        )
        self.assertEqual(v_cfg.min_count, 0)
        self.assertEqual(v_cfg.wildtype_cfg.coding, False)
        self.assertEqual(v_cfg.wildtype_cfg.sequence, "AAAAAA")
        self.assertEqual(v_cfg.wildtype_cfg.reference_offset, 0)

    def test_override_defaults_correctly(self):
        cfg = {
            WILDTYPE: self.wt_cfg,
            USE_ALIGNER: True,
            VARIANTS_MAX_MUTATIONS: 9,
            VARIANTS_MIN_COUNT: 0,
        }
        v_cfg = VariantsConfiguration(cfg).validate()
        self.assertEqual(v_cfg.use_aligner, True)
        self.assertEqual(v_cfg.max_mutations, 9)
        self.assertEqual(v_cfg.min_count, 0)
        self.assertEqual(v_cfg.wildtype_cfg.coding, False)
        self.assertEqual(v_cfg.wildtype_cfg.sequence, "AAAAAA")
        self.assertEqual(v_cfg.wildtype_cfg.reference_offset, 0)

    def test_error_aligner_not_bool(self):
        cfg = {WILDTYPE: self.wt_cfg, USE_ALIGNER: 12}
        with self.assertRaises(TypeError):
            VariantsConfiguration(cfg).validate()

    def test_error_max_mutations_not_int(self):
        cfg = {WILDTYPE: self.wt_cfg, VARIANTS_MAX_MUTATIONS: 0.2}
        with self.assertRaises(TypeError):
            VariantsConfiguration(cfg).validate()

    def test_error_max_mutations_negative(self):
        cfg = {WILDTYPE: self.wt_cfg, VARIANTS_MAX_MUTATIONS: -12}
        with self.assertRaises(ValueError):
            VariantsConfiguration(cfg).validate()

    def test_error_max_mutations_too_high(self):
        cfg = {WILDTYPE: self.wt_cfg, VARIANTS_MAX_MUTATIONS: 11}
        with self.assertRaises(ValueError):
            VariantsConfiguration(cfg).validate()

    def test_error_min_count_not_int(self):
        cfg = {WILDTYPE: self.wt_cfg, VARIANTS_MIN_COUNT: 0.2}
        with self.assertRaises(TypeError):
            VariantsConfiguration(cfg).validate()

    def test_error_min_count_negative(self):
        cfg = {WILDTYPE: self.wt_cfg, VARIANTS_MIN_COUNT: -12}
        with self.assertRaises(ValueError):
            VariantsConfiguration(cfg).validate()


class WildTypeConfigTest(TestCase):
    def setUp(self):
        current_wd = os.path.dirname(__file__)
        self.data_path = os.path.join(current_wd, "data/config_check")

    def tearDown(self):
        pass

    def test_defaults_load_correctly(self):
        cfg = {SEQUENCE: "AAA"}
        wt_cfg = WildTypeConfiguration(cfg).validate()
        self.assertEqual(wt_cfg.coding, False)
        self.assertEqual(wt_cfg.sequence, "AAA")
        self.assertEqual(wt_cfg.reference_offset, 0)

    def test_override_defaults_correctly(self):
        cfg = {CODING: True, REF_OFFSET: 3, SEQUENCE: "AAAAAA"}
        wt_cfg = WildTypeConfiguration(cfg).validate()
        self.assertEqual(wt_cfg.coding, True)
        self.assertEqual(wt_cfg.sequence, "AAAAAA")
        self.assertEqual(wt_cfg.reference_offset, 3)

    def test_error_coding_not_bool(self):
        cfg = {CODING: 1, SEQUENCE: "AAA"}
        with self.assertRaises(TypeError):
            WildTypeConfiguration(cfg).validate()

    def test_error_ref_offset_not_int(self):
        cfg = {REF_OFFSET: "1", SEQUENCE: "AAA"}
        with self.assertRaises(TypeError):
            WildTypeConfiguration(cfg).validate()

    def test_ref_offset_negative(self):
        cfg = {REF_OFFSET: -1, SEQUENCE: "AAA"}
        with self.assertRaises(ValueError):
            WildTypeConfiguration(cfg).validate()

    def test_ref_offset_not_multiple_of_three_noncoding(self):
        cfg = {SEQUENCE: "AAA", REF_OFFSET: 2, CODING: False}
        wt_cfg = WildTypeConfiguration(cfg).validate()
        self.assertEqual(wt_cfg.reference_offset, 2)

    def test_error_ref_offset_not_multiple_of_three_coding(self):
        cfg = {SEQUENCE: "AAA", REF_OFFSET: 2, CODING: True}
        with self.assertRaises(ValueError):
            WildTypeConfiguration(cfg).validate()

    def test_error_sequence_not_str(self):
        cfg = {SEQUENCE: b"AAA"}
        with self.assertRaises(TypeError):
            WildTypeConfiguration(cfg).validate()

    def test_error_invalid_seq_chars(self):
        cfg = {SEQUENCE: "ATX"}
        with self.assertRaises(ValueError):
            WildTypeConfiguration(cfg).validate()

    def test_error_coding_but_seq_not_multiple_of_three(self):
        cfg = {CODING: True, SEQUENCE: "A"}
        with self.assertRaises(ValueError):
            WildTypeConfiguration(cfg).validate()

    def test_noncoding_seq_not_multiple_of_three(self):
        cfg = {CODING: False, SEQUENCE: "A"}
        wt_cfg = WildTypeConfiguration(cfg).validate()
        self.assertEqual(wt_cfg.sequence, "A")

    def test_sequence_stored_as_uppercase(self):
        cfg = {CODING: False, SEQUENCE: "aa"}
        wt_cfg = WildTypeConfiguration(cfg).validate()
        self.assertEqual(wt_cfg.sequence, "AA")

    def test_error_invalid_seq_file(self):
        cfg = {CODING: False, SEQUENCE: os.path.join(self.data_path, "polyA_t0.txt")}
        with self.assertRaises(IOError):
            WildTypeConfiguration(cfg).validate()

        cfg = {CODING: False, SEQUENCE: os.path.join(self.data_path, "bad_sequence.fa")}
        with self.assertRaises(ValueError):
            WildTypeConfiguration(cfg).validate()

    def test_sequence_loads_from_file(self):
        cfg = {CODING: False, SEQUENCE: os.path.join(self.data_path, "sequence.fa")}
        wt_cfg = WildTypeConfiguration(cfg).validate()
        self.assertEqual(wt_cfg.sequence, "AAAAAAAAAAAA")
