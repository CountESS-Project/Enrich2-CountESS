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

from ..config.types import *
from ..config.config_check import element_type


class TestConfigTypesModule(unittest.TestCase):

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
        cfg = {
            "fastq": {},
            "variants": {}
        }
        self.assertEquals(element_type(cfg), "BasicSeqLib")

    def test_seqlib_type_is_barcode(self):
        cfg = {
            "barcodes": {},
            "fastq": {}
        }
        self.assertEquals(element_type(cfg), "BarcodeSeqLib")

    def test_seqlib_type_is_barcode_variant(self):
        cfg = {
            "barcodes": {"map file": 0},
            "fastq": {},
            "variants": {}
        }
        self.assertEquals(element_type(cfg), "BcvSeqLib")

    def test_seqlib_type_is_idonly(self):
        cfg = {
            "identifiers": {}
        }
        self.assertEquals(element_type(cfg), "IdOnlySeqLib")

    def test_seqlib_type_is_barcode_id(self):
        cfg = {
            "barcodes": {"map file": 0},
            "fastq": {},
            "identifiers": {}
        }
        self.assertEquals(element_type(cfg), "BcidSeqLib")

    def test_seqlib_type_is_invalid(self):
        cfg = {
            "barcodes": {"map file": 0},
            "fastq": {},
            "identifiers": {},
            "variants": {}
        }
        with self.assertRaises(ValueError):
            element_type(cfg)

    def test_error_invalid_element_type(self):
        cfg = {"nothing": []}
        with self.assertRaises(ValueError):
            element_type(cfg)

if __name__ == "__main__":
    unittest.main()