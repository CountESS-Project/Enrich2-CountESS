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

from enrich2.sequence.fqread import read_fastq


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestFQReaderFormatting
    )
    return suite


class TestFQReaderFormatting(unittest.TestCase):

    def run_read_fq(self, fname):
        return list(read_fastq(fname))

    @classmethod
    def setUpClass(cls):
        return

    @classmethod
    def tearDownClass(cls):
        return

    def test_read_fq_raises_value_errors(self):
        empty_seq = os.path.join(
            os.path.dirname(__file__),
            "data", "fastq", "empty_sequence.fq"
        )
        self.assertRaises(ValueError, self.run_read_fq, empty_seq)

        missing_sequence = os.path.join(
            os.path.dirname(__file__),
            "data", "fastq", "missing_sequence.fq"
        )
        self.assertRaises(ValueError, self.run_read_fq, missing_sequence)

        missing_quality = os.path.join(
            os.path.dirname(__file__),
            "data", "fastq", "missing_quality.fq"
        )
        self.assertRaises(ValueError, self.run_read_fq, missing_quality)

        bad_header = os.path.join(
            os.path.dirname(__file__),
            "data", "fastq", "bad_header.fq"
        )
        self.assertRaises(ValueError, self.run_read_fq, bad_header)

        no_plus_sign = os.path.join(
            os.path.dirname(__file__),
            "data", "fastq", "no_plus_sign.fq"
        )
        self.assertRaises(ValueError, self.run_read_fq, no_plus_sign)

        dff_length = os.path.join(
            os.path.dirname(__file__),
            "data", "fastq", "seq_qual_diff_length.fq"
        )
        self.assertRaises(ValueError, self.run_read_fq, dff_length)

        eof = os.path.join(
            os.path.dirname(__file__),
            "data", "fastq", "premature_eof.fq"
        )
        result = str(self.run_read_fq(eof)[-1])
        expected = "@FQTEST:8:8:8:8:1#0/1\n" \
                   "AAAAAAAAAAAAAAAA\n+\nHHHHHHHHHHHHHHHH"
        self.assertEqual(result, expected)

        not_a_fastq = os.path.join(
            os.path.dirname(__file__),
            "data", "fastq", "not_a_fastq.fq"
        )
        self.assertRaises(ValueError, self.run_read_fq, not_a_fastq)

        empty = os.path.join(
            os.path.dirname(__file__),
            "data", "fastq", "empty.fq"
        )
        self.assertEqual(self.run_read_fq(empty), [])

if __name__ == "__main__":
    unittest.main()