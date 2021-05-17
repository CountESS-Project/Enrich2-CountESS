import unittest

from ..sequence.wildtype import WildTypeSequence


def make_cfg(sequence, offset=0, coding=False):
    cfg = dict()
    cfg["sequence"] = sequence
    cfg["reference offset"] = offset
    cfg["coding"] = coding
    return cfg


class TestWildTypeModule(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_keyerror_when_cfg_incomplete(self):
        cfg = {}
        wt = WildTypeSequence("Test")
        with self.assertRaises(KeyError):
            wt.configure(cfg)

    def test_sequence_loads_correctly(self):
        cfg = make_cfg("GATTACA")
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        self.assertTrue(wt.dna_seq == "GATTACA")

        cfg = make_cfg("gattaca")
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        self.assertTrue(wt.dna_seq == "GATTACA")

    def test_protein_sequence_loads_correctly(self):
        cfg = make_cfg("AAAAAA", coding=True)
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        self.assertTrue(wt.protein_seq == "KK")

    def test_protein_sequence_loads_correctly_noncoding(self):
        cfg = make_cfg("AAAAAA", coding=False)
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        self.assertEquals(wt.protein_seq, None)

    def test_is_coding(self):
        cfg = make_cfg("AAAAAA", coding=True)
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        self.assertTrue(wt.is_coding())

    def test_is_not_coding(self):
        cfg = make_cfg("AAAAAA", coding=False)
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        self.assertFalse(wt.is_coding())

    def test_should_not_be_equal(self):
        cfg = make_cfg("GATTACA", 0, False)
        wt_a = WildTypeSequence("Test")
        wt_a.configure(cfg)

        cfg = make_cfg("GATTACA", 3, False)
        wt_b = WildTypeSequence("Test")
        wt_b.configure(cfg)

        self.assertFalse(wt_a == wt_b)

    def test_should_be_equal(self):
        cfg = make_cfg("GATTACA", 0, False)
        wt_a = WildTypeSequence("Test")
        wt_a.configure(cfg)

        cfg = make_cfg("GATTACA", 0, False)
        wt_b = WildTypeSequence("Test")
        wt_b.configure(cfg)

        self.assertTrue(wt_a == wt_b)

    def test_error_when_incorrect_seq_characters(self):
        cfg = make_cfg("1234ACa")
        wt = WildTypeSequence("Test")
        with self.assertRaises(ValueError):
            wt.configure(cfg)
        cfg = make_cfg("GATTAC^&")
        wt = WildTypeSequence("Test")
        with self.assertRaises(ValueError):
            wt.configure(cfg)

    def test_error_when_coding_but_seqlen_not_multiple_of_three(self):
        cfg = make_cfg("GATTACA", coding=True)
        wt = WildTypeSequence("Test")
        with self.assertRaises(ValueError):
            wt.configure(cfg)

    def test_error_protein_offset_when_coding_but_not_multiple_of_three(self):
        cfg = make_cfg("AAAAAA", offset=1, coding=True)
        wt = WildTypeSequence("Test")
        with self.assertRaises(ValueError):
            wt.configure(cfg)

    def test_error_invalid_offset_not_a_number(self):
        cfg = make_cfg("AAAAAA", offset="a")
        wt = WildTypeSequence("Test")
        with self.assertRaises(TypeError):
            wt.configure(cfg)

        cfg = make_cfg("AAAAAA", offset=None)
        wt = WildTypeSequence("Test")
        with self.assertRaises(TypeError):
            wt.configure(cfg)

    def test_error_invalid_offset_negative(self):
        cfg = make_cfg("AAAAAA", offset=-1)
        wt = WildTypeSequence("Test")
        with self.assertRaises(ValueError):
            wt.configure(cfg)

    def test_correct_dna_offset_loads_when_coding(self):
        cfg = make_cfg("AAAAAA", offset=3, coding=True)
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        self.assertEquals(wt.dna_offset, 3)

    def test_correct_protein_offset_loads_when_coding(self):
        cfg = make_cfg("AAAAAA", offset=6, coding=True)
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        self.assertEquals(wt.protein_offset, 2)

    def test_correct_dna_offset_loads_when_noncoding(self):
        cfg = make_cfg("AAAAAA", offset=3, coding=False)
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        self.assertEquals(wt.dna_offset, 3)

    def test_correct_protein_offset_loads_when_noncoding(self):
        cfg = make_cfg("AAAAAA", offset=3, coding=False)
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        self.assertEquals(wt.protein_offset, None)

    def test_serialize_is_matches_input_cfg(self):
        cfg = make_cfg("AAAAAA", offset=0, coding=True)
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        result_cfg = wt.serialize()
        self.assertEquals(cfg, result_cfg)

        cfg = make_cfg("AAAAAA", offset=0, coding=True)
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        result_cfg = wt.serialize()
        self.assertEquals(cfg, result_cfg)

    def test_duplicate_is_correct(self):
        cfg = make_cfg("AAAAAA", offset=0, coding=True)
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        new_wt = wt.duplicate("New")
        self.assertEquals(wt, new_wt)

    def test_position_tuples_has_correct_offset_coding(self):
        cfg = make_cfg("AAAAAA", offset=6, coding=True)
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        tuples = wt.position_tuples(protein=True)
        self.assertEquals(tuples, [(3, "K"), (4, "K")])

    def test_position_tuples_has_correct_offset_noncoding(self):
        cfg = make_cfg("AAA", offset=6, coding=False)
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        tuples = wt.position_tuples(protein=False)
        self.assertEquals(tuples, [(7, "A"), (8, "A"), (9, "A")])

    def test_throw_error_position_tuples_protein_but_seq_not_coding(self):
        cfg = make_cfg("AAAAAA", offset=6, coding=False)
        wt = WildTypeSequence("Test")
        wt.configure(cfg)
        with self.assertRaises(AttributeError):
            wt.position_tuples(protein=True)


if __name__ == "__main__":
    unittest.main()
