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

from ..sequence.fqread import read_fastq
from .utilities import create_file_path


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
        direc = "data/reads/fqreader/"
        empty_seq = create_file_path("empty_sequence.fq", direc)
        self.assertRaises(ValueError, self.run_read_fq, empty_seq)

        missing_sequence = create_file_path("missing_sequence.fq", direc)
        self.assertRaises(ValueError, self.run_read_fq, missing_sequence)

        missing_quality = create_file_path("missing_quality.fq", direc)
        self.assertRaises(ValueError, self.run_read_fq, missing_quality)

        bad_header = create_file_path("bad_header.fq", direc)
        self.assertRaises(ValueError, self.run_read_fq, bad_header)

        no_plus_sign = create_file_path("no_plus_sign.fq", direc)
        self.assertRaises(ValueError, self.run_read_fq, no_plus_sign)

        dff_length = create_file_path("seq_qual_diff_length.fq", direc)
        self.assertRaises(ValueError, self.run_read_fq, dff_length)

        eof = create_file_path("premature_eof.fq", direc)
        result = str(self.run_read_fq(eof)[-1])
        read = "@FQTEST:8:8:8:8:1#0/1\nAAAAAAAAAAAAAAAA\n+\nHHHHHHHHHHHHHHHH"
        expected = read

        self.assertEqual(result, expected)

        not_a_fastq = create_file_path("not_a_fastq.fq", direc)
        self.assertRaises(ValueError, self.run_read_fq, not_a_fastq)

        empty = create_file_path("empty.fq", direc)
        self.assertEqual(self.run_read_fq(empty), [])


# --------------------------------------------------------------------------- #
#
#                                   MAIN
#
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    unittest.main()
