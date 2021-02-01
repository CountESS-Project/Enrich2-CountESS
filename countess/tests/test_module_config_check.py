import unittest
import operator
from functools import reduce

from ..config.config_check import *


def get_from_nested_dict(dictionary, map_list):
    return reduce(operator.getitem, map_list, dictionary)


class TestConfigCheckModule(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_experiment(self):
        cfg = {"conditions": []}
        self.assertEquals(element_type(cfg), "Experiment")

    def test_is_condition(self):
        cfg = {"selections": []}
        self.assertEquals(element_type(cfg), "Condition")

    def test_is_selection(self):
        cfg = {"libraries": []}
        self.assertEquals(element_type(cfg), "Selection")

    def test_seqlib_type_is_basic(self):
        cfg = {"fastq": {}, "variants": {}}
        self.assertEquals(element_type(cfg), "BasicSeqLib")

    def test_seqlib_type_is_barcode(self):
        cfg = {"barcodes": {}, "fastq": {}}
        self.assertEquals(element_type(cfg), "BarcodeSeqLib")

    def test_seqlib_type_is_barcode_variant(self):
        cfg = {"barcodes": {"map file": 0}, "fastq": {}, "variants": {}}
        self.assertEquals(element_type(cfg), "BcvSeqLib")

    def test_seqlib_type_is_idonly(self):
        cfg = {"identifiers": {}}
        self.assertEquals(element_type(cfg), "IdOnlySeqLib")

    def test_seqlib_type_is_barcode_id(self):
        cfg = {"barcodes": {"map file": 0}, "fastq": {}, "identifiers": {}}
        self.assertEquals(element_type(cfg), "BcidSeqLib")

    def test_seqlib_type_is_invalid(self):
        cfg = {
            "barcodes": {"map file": 0},
            "fastq": {},
            "identifiers": {},
            "variants": {},
        }
        with self.assertRaises(ValueError):
            element_type(cfg)

    def test_error_invalid_element_type(self):
        cfg = {"nothing": []}
        with self.assertRaises(ValueError):
            element_type(cfg)


if __name__ == "__main__":
    unittest.main()
