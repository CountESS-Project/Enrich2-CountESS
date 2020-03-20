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
