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

from ..sequence.aligner import Aligner


class TestAlignerModule(unittest.TestCase):
    def setUp(self):
        self.aligner = Aligner(backend="ambivert")

    def tearDown(self):
        pass

    def test_correct_alignment_insertion(self):
        trace = self.aligner.align("ATG", "ACTG")
        expected_trace = [
            (0, 0, "match", None),
            (0, 1, "insertion", 1),
            (1, 2, "match", None),
            (2, 3, "match", None),
        ]
        self.assertEquals(trace, expected_trace)

    def test_correct_alignment_deletion(self):
        trace = self.aligner.align("ACTG", "ATG")
        expected_trace = [
            (0, 0, "match", None),
            (1, 0, "deletion", 1),
            (2, 1, "match", None),
            (3, 2, "match", None),
        ]
        self.assertEquals(trace, expected_trace)

    def test_correct_alignment_mismatch(self):
        trace = self.aligner.align("ATG", "ACG")
        expected_trace = [
            (0, 0, "match", None),
            (1, 1, "mismatch", None),
            (2, 2, "match", None),
        ]
        self.assertEquals(trace, expected_trace)

    def test_correct_alignment_exact_match(self):
        trace = self.aligner.align("ATG", "ATG")
        expected_trace = [
            (0, 0, "match", None),
            (1, 1, "match", None),
            (2, 2, "match", None),
        ]
        self.assertEquals(trace, expected_trace)

    def test_typeerror_non_string_input(self):
        with self.assertRaises(TypeError):
            self.aligner.align(123, "ATG")
        with self.assertRaises(TypeError):
            self.aligner.align("ATG", 123)
        with self.assertRaises(TypeError):
            self.aligner.align("ATG", None)

    def test_valueerror_empty_input(self):
        with self.assertRaises(ValueError):
            self.aligner.align("", "ATG")
        with self.assertRaises(ValueError):
            self.aligner.align("ATG", "")
        with self.assertRaises(ValueError):
            self.aligner.align("", "")

    def test_lower_upper_string_characters_considered_equal(self):
        trace = self.aligner.align("ATG", "atg")
        expected_trace = [
            (0, 0, "match", None),
            (1, 1, "match", None),
            (2, 2, "match", None),
        ]
        self.assertEquals(trace, expected_trace)

    def test_value_error_missing_gap_penalty(self):
        simple_similarity = {
            "A": {"A": 1, "C": -1, "G": -1, "T": -1, "N": 0, "X": 0},
            "C": {"A": -1, "C": 1, "G": -1, "T": -1, "N": 0, "X": 0},
            "G": {"A": -1, "C": -1, "G": 1, "T": -1, "N": 0, "X": 0},
            "T": {"A": -1, "C": -1, "G": -1, "T": 1, "N": 0, "X": 0},
            "N": {"A": 0, "C": 0, "G": 0, "T": 0, "N": 0, "X": 0},
            "X": {"A": 0, "C": 0, "G": 0, "T": 0, "N": 0, "X": 0},
        }
        with self.assertRaises(ValueError):
            Aligner(simple_similarity)

    def test_value_error_asymmetric_scoring(self):
        simple_similarity = {
            "A": {"A": 1, "C": -1, "G": -1, "T": -1, "N": 0},
            "C": {"A": -1, "C": 1, "G": -1, "T": -1, "N": 0},
            "G": {"A": -1, "C": -1, "G": 1, "T": -1, "N": 0, "X": 0},
            "T": {"A": -1, "C": -1, "G": -1, "T": 1, "N": 0, "X": 0},
            "N": {"A": 0, "C": 0, "G": 0, "T": 0, "N": 0, "X": 0},
            "X": {"A": 0, "C": 0, "G": 0, "T": 0, "N": 0, "X": 0},
        }
        with self.assertRaises(ValueError):
            Aligner(simple_similarity)


if __name__ == "__main__":
    unittest.main()
