import unittest
import pandas as pd

from ..base.dataframe import fill_position_gaps, singleton_dataframe
from ..base.dataframe import single_mutations_to_tuples
from ..base.dataframe import single_mutation_index, filter_coding_index
from ..base.dataframe import SingleMut
from ..sequence.wildtype import WildTypeSequence


class TestUtilitiesDataframe(unittest.TestCase):
    def test_single_mutation_index(self):
        # test cases use all() because testing equality of indices returns a vector of booleans

        # test removal of double-mutants
        self.assertTrue(
            all(
                single_mutation_index(pd.Index(["c.76A>C (p.Ile26Leu)"]))
                == pd.Index(["c.76A>C (p.Ile26Leu)"])
            )
        )
        self.assertTrue(
            all(
                single_mutation_index(
                    pd.Index(
                        [
                            "c.76A>C (p.Ile26Leu)",
                            "c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu)",
                        ]
                    )
                )
                == pd.Index(["c.76A>C (p.Ile26Leu)"])
            )
        )
        self.assertTrue(
            all(
                single_mutation_index(
                    pd.Index(["c.76A>C (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])
                )
                == pd.Index(["c.76A>C (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])
            )
        )
        self.assertTrue(
            all(
                single_mutation_index(
                    pd.Index(
                        [
                            "c.76A>C (p.Ile26Leu)",
                            "c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu)",
                            "c.78C>T (p.Ile26Leu)",
                        ]
                    )
                )
                == pd.Index(["c.76A>C (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])
            )
        )

        # order matters
        self.assertFalse(
            all(
                single_mutation_index(
                    pd.Index(["c.78C>T (p.Ile26Leu)", "c.76A>C (p.Ile26Leu)"])
                )
                == pd.Index(["c.76A>C (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])
            )
        )

        # empty indices
        self.assertEqual(len(single_mutation_index(pd.Index([]))), 0)
        self.assertEqual(
            len(
                single_mutation_index(
                    pd.Index(["c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu)"])
                )
            ),
            0,
        )

    def test_filter_coding_index(self):
        # test cases use all() because testing equality of indices returns a vector of booleans

        # test removal of '???' variants
        self.assertTrue(
            all(
                filter_coding_index(pd.Index(["c.76A>C (p.Ile26Leu)"]))
                == pd.Index(["c.76A>C (p.Ile26Leu)"])
            )
        )
        self.assertTrue(
            all(
                filter_coding_index(
                    pd.Index(["c.76A>C (p.Ile26Leu)", "c.76A>N (p.Ile26???)"])
                )
                == pd.Index(["c.76A>C (p.Ile26Leu)"])
            )
        )
        self.assertTrue(
            all(
                filter_coding_index(
                    pd.Index(["c.76A>N (p.Ile26???)", "c.76A>C (p.Ile26Leu)"])
                )
                == pd.Index(["c.76A>C (p.Ile26Leu)"])
            )
        )
        self.assertTrue(
            all(
                filter_coding_index(
                    pd.Index(["c.76A>C (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])
                )
                == pd.Index(["c.76A>C (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])
            )
        )
        self.assertTrue(
            all(
                filter_coding_index(
                    pd.Index(
                        [
                            "c.76A>C (p.Ile26Leu)",
                            "c.76A>N (p.Ile26???)",
                            "c.78C>T (p.Ile26Leu)",
                        ]
                    )
                )
                == pd.Index(["c.76A>C (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])
            )
        )

        # empty index
        self.assertEqual(
            len(filter_coding_index(pd.Index(["c.76A>N (p.Ile26???)"]))), 0
        )
        self.assertEqual(len(filter_coding_index(pd.Index([]))), 0)

    def test_single_mutations_to_tuples(self):
        # proteins
        single_mut_1 = SingleMut(pre="I", post="L", pos=26, key="p.Ile26Leu")
        single_mut_2 = SingleMut(pre="*", post="I", pos=76, key="p.Ter76Ile")
        self.assertEqual(
            single_mutations_to_tuples(pd.Index(["p.Ile26Leu", "p.Ter76Ile"])),
            [single_mut_1, single_mut_2],
        )
        self.assertEqual(
            single_mutations_to_tuples(pd.Index(["p.Ile26Leu", "p.Ile26Leu"])),
            [single_mut_1, single_mut_1],
        )
        self.assertEqual(
            single_mutations_to_tuples(pd.Index(["p.Ter76Ile", "p.Ile26Leu"])),
            [single_mut_2, single_mut_1],
        )
        self.assertNotEqual(
            single_mutations_to_tuples(pd.Index(["p.Ter76Ile", "p.Ile26Leu"])),
            [single_mut_1, single_mut_2],
        )
        self.assertNotEqual(
            single_mutations_to_tuples(pd.Index(["p.Ter76Ile", "p.Ile26Leu"])),
            [single_mut_1, single_mut_2],
        )

        with self.assertRaises(KeyError):
            single_mutations_to_tuples(pd.Index(["p.Ter76Ixx"]))
        with self.assertRaises(ValueError):
            single_mutations_to_tuples(pd.Index(["p.Ter76Ile", "n.76A>C"]))
        with self.assertRaises(ValueError):
            single_mutations_to_tuples(pd.Index(["I21L"]))
        with self.assertRaises(ValueError):
            single_mutations_to_tuples(pd.Index(["p.Ter76Ile, p.Ter76Ile"]))
        with self.assertRaises(ValueError):
            single_mutations_to_tuples(pd.Index(["_sy"]))
        with self.assertRaises(ValueError):
            single_mutations_to_tuples(pd.Index(["_wt"]))
        with self.assertRaises(ValueError):
            single_mutations_to_tuples(pd.Index(["p.Ter76Ile", "c.76A>C"]))
        with self.assertRaises(ValueError):
            single_mutations_to_tuples(pd.Index(["c.78C>T (p.Ile26Leu)", "c.76A>C"]))
        with self.assertRaises(ValueError):
            single_mutations_to_tuples(pd.Index(["c.78C>T", "c.76A>C"]))
        # with self.assertRaises(ValueError):
        #     single_mutations_to_tuples(pd.Index(
        #         ['n.78C>T (p.Ile26Leu)', 'n.76A>C']))
        with self.assertRaises(TypeError):
            single_mutations_to_tuples(pd.Index([b"p.Ter76Ile"]))

        # coding
        coding_1 = "c.76A>C (p.Ile26Leu)"
        coding_2 = "c.78C>T (p.Ile26Leu)"
        coding_tup_1 = SingleMut(pre="A", post="C", pos=76, key="c.76A>C (p.Ile26Leu)")
        coding_tup_2 = SingleMut(pre="C", post="T", pos=78, key="c.78C>T (p.Ile26Leu)")
        self.assertEqual(
            single_mutations_to_tuples(pd.Index([coding_1, coding_2])),
            [coding_tup_1, coding_tup_2],
        )
        self.assertEqual(
            single_mutations_to_tuples(pd.Index([coding_2, coding_1])),
            [coding_tup_2, coding_tup_1],
        )
        self.assertEqual(
            single_mutations_to_tuples(pd.Index([coding_1, coding_1])),
            [coding_tup_1, coding_tup_1],
        )
        self.assertNotEqual(
            single_mutations_to_tuples(pd.Index([coding_2, coding_1])),
            [coding_tup_1, single_mut_2],
        )

        # noncoding
        single_mut_1 = SingleMut(pre="A", post="C", pos=76, key="n.76A>C")
        single_mut_2 = SingleMut(pre="G", post="T", pos=26, key="n.26G>T")
        self.assertEqual(
            single_mutations_to_tuples(pd.Index(["n.76A>C", "n.26G>T"])),
            [single_mut_1, single_mut_2],
        )
        self.assertEqual(
            single_mutations_to_tuples(pd.Index(["n.26G>T", "n.76A>C"])),
            [single_mut_2, single_mut_1],
        )
        self.assertEqual(
            single_mutations_to_tuples(pd.Index(["n.76A>C", "n.76A>C"])),
            [single_mut_1, single_mut_1],
        )
        self.assertNotEqual(
            single_mutations_to_tuples(pd.Index(["n.26G>T", "n.76A>C"])),
            [single_mut_1, single_mut_2],
        )

    def test_fill_position_gaps(self):
        self.assertSequenceEqual(fill_position_gaps([1, 5], 1), [1, 5])
        self.assertSequenceEqual(fill_position_gaps([1, 1, 5], 1), [1, 5])
        self.assertSequenceEqual(fill_position_gaps([5, 1], 1), [1, 5])
        self.assertSequenceEqual(fill_position_gaps([5, 1, 5], 1), [1, 5])
        self.assertSequenceEqual(fill_position_gaps([1, 5], 3), [1, 5])
        self.assertSequenceEqual(fill_position_gaps([1, 5], 4), [1, 2, 3, 4, 5])
        self.assertSequenceEqual(fill_position_gaps([1, 1, 5], 4), [1, 2, 3, 4, 5])
        self.assertSequenceEqual(fill_position_gaps([5, 1], 4), [1, 2, 3, 4, 5])
        self.assertSequenceEqual(fill_position_gaps([5, 1, 5], 4), [1, 2, 3, 4, 5])
        self.assertSequenceEqual(fill_position_gaps([1, 5, 15], 4), [1, 2, 3, 4, 5, 15])
        self.assertSequenceEqual(fill_position_gaps([15, 5, 1], 4), [1, 2, 3, 4, 5, 15])
        self.assertSequenceEqual(fill_position_gaps([15, 1, 5], 4), [1, 2, 3, 4, 5, 15])
        self.assertSequenceEqual(fill_position_gaps([15, 17, 15], 4), [15, 16, 17])
        self.assertSequenceEqual(fill_position_gaps([1, 1, 1, 1], 1), [1])

        # error checking
        with self.assertRaises(ValueError):
            fill_position_gaps([], 5)
        with self.assertRaises(TypeError):
            fill_position_gaps(None, 5)
        with self.assertRaises(TypeError):
            fill_position_gaps("abc", 5)
        with self.assertRaises(TypeError):
            fill_position_gaps([1, 2, "a"], 5)
        with self.assertRaises(ValueError):
            fill_position_gaps([1, 2, 3], -5)
        with self.assertRaises(TypeError):
            fill_position_gaps([1, 2, 3], 2.0)
        with self.assertRaises(TypeError):
            fill_position_gaps([1, 2.0, 3], 1)

    def test_singleton_dataframe_offset(self):
        cfg = {
            "coding": False,
            "reference offset": 3,
            "sequence": "AAAAAAAAAAAAAAAAAAAAA",
        }
        wt = WildTypeSequence("tests")
        wt.configure(cfg)
        values = pd.Series(
            data=[1, 2, 3], index=["c.4A>T (p.Ile3Leu)", "c.5A>C (p.Ile5Leu)", "_wt"]
        )
        frame, wt_sequence = singleton_dataframe(
            values, wt, coding=False, plot_wt_score=False
        )
        self.assertTrue(all(frame == frame))
        self.assertEqual(wt_sequence, "AA")

        with self.assertRaises(ValueError):
            values = pd.Series(
                data=[1, 2, 3],
                index=["c.1A>T (p.Ile3Leu)", "c.5A>C (p.Ile5Leu)", "_wt"],
            )
            singleton_dataframe(values, wt, coding=False, plot_wt_score=False)

    def test_singleton_dataframe_noncoding(self):
        cfg = {
            "coding": False,
            "reference offset": 0,
            "sequence": "AAAAAAAAAAAAAAAAAAAAA",
        }
        wt = WildTypeSequence("tests")
        wt.configure(cfg)
        values = pd.Series(
            data=[1, 2, 3, 4],
            index=[
                "c.1A>G (p.Ile1Leu)",
                "c.3A>T (p.Ile3Leu)",
                "c.5A>C (p.Ile5Leu)",
                "_wt",
            ],
        )
        frame, wt_sequence = singleton_dataframe(
            values, wt, coding=False, plot_wt_score=False
        )
        self.assertTrue(all(frame == frame))
        self.assertEqual(wt_sequence, "AAAAA")
        with self.assertRaises(AttributeError):
            singleton_dataframe(values, wt, coding=True)

        # missing _wt
        values = pd.Series(
            data=[1, 2, 3],
            index=["c.1A>G (p.Ile1Leu)", "c.3A>T (p.Ile3Leu)", "c.5A>C (p.Ile5Leu)"],
        )
        frame, wt_sequence = singleton_dataframe(
            values, wt, coding=False, plot_wt_score=True
        )
        self.assertTrue(all(frame == frame))
        self.assertEqual(wt_sequence, "AAAAA")

        # one multiple mutation
        values = pd.Series(
            data=[1, 2, 3],
            index=[
                "c.1A>G (p.Ile1Leu)",
                "c.3A>T (p.Ile3Leu)",
                "c.5A>C (p.Ile5Leu), c.6A>C (p.Ile5Leu)",
            ],
        )
        frame, wt_sequence = singleton_dataframe(
            values, wt, coding=False, plot_wt_score=False
        )
        self.assertTrue(all(frame == frame))
        self.assertEqual(wt_sequence, "AAA")

        # noncoding index
        values = pd.Series(data=[1, 2, 3], index=["n.1A>G", "n.3A>T", "n.5A>C, n.6A>C"])
        frame, wt_sequence = singleton_dataframe(
            values, wt, coding=False, plot_wt_score=False
        )
        self.assertTrue(all(frame == frame))
        self.assertEqual(wt_sequence, "AAA")

        # gap size
        values = pd.Series(
            data=[1, 2, 3, 4], index=["n.1A>G", "n.3A>T", "n.5A>C", "n.10A>C"]
        )
        frame, wt_sequence = singleton_dataframe(
            values, wt, gap_size=3, coding=False, plot_wt_score=False
        )
        self.assertTrue(all(frame == frame))
        self.assertEqual(wt_sequence, "AAAAAA")

    def test_singleton_dataframe_coding(self):
        cfg = {
            "coding": True,
            "reference offset": 0,
            "sequence": "AAAAAAAAAAAAAAAAAAAAA",
        }
        wt = WildTypeSequence("tests")
        wt.configure(cfg)
        values = pd.Series(
            data=[1, 2, 3, 4], index=["p.Lys1Leu", "p.Lys3Lys", "p.Lys5Lys", "_wt"]
        )
        frame, wt_sequence = singleton_dataframe(values, wt, coding=True)
        self.assertTrue(all(frame == frame))
        self.assertEqual(wt_sequence, "KKKKK")

        values = pd.Series(
            data=[1, 2, 3, 4],
            index=["p.Lys1Leu, p.Lys2Leu", "p.Lys3Lys", "p.Lys5Lys", "_wt"],
        )
        frame, wt_sequence = singleton_dataframe(values, wt, coding=True)
        self.assertTrue(all(frame == frame))
        self.assertEqual(wt_sequence, "KKK")

    def test_singleton_dataframe_invalid_input(self):
        cfg = {
            "coding": True,
            "reference offset": 0,
            "sequence": "AAAAAAAAAAAAAAAAAAAAA",
        }
        wt = WildTypeSequence("tests")
        wt.configure(cfg)

        with self.assertRaises(ValueError):
            values = pd.Series(
                data=[1, 2, 3, "4"],
                index=[
                    "c.1A>G (p.Ile1Leu)",
                    "c.3A>T (p.Ile3Leu)",
                    "c.5A>C (p.Ile5Leu)",
                    "_wt",
                ],
            )
            singleton_dataframe(values, wt, coding=True)

        with self.assertRaises(ValueError):
            values = pd.Series(
                data=[1, 2, 3, b"4"],
                index=[
                    "c.1A>G (p.Ile1Leu)",
                    "c.3A>T (p.Ile3Leu)",
                    "c.5A>C (p.Ile5Leu)",
                    "_wt",
                ],
            )
            singleton_dataframe(values, wt, coding=True)

        with self.assertRaises(ValueError):
            values = pd.Series(
                data=[1, 2, 3, b"4"],
                index=[
                    "c.1G>G (p.Ile1Leu)",
                    "c.3A>T (p.Ile3Leu)",
                    "c.5A>C (p.Ile5Leu)",
                    "_wt",
                ],
            )
            singleton_dataframe(values, wt)

        with self.assertRaises(ValueError):
            values = pd.Series(
                data=[1, 2, 3],
                index=[
                    "c.1G>G (p.Ile1Leu), c.1G>G (p.Ile1Leu)",
                    "c.3A>T (p.Ile3Leu), c.3G>G (p.Ile1Leu)",
                    "c.5A>C (p.Ile5Leu), c.1G>G (p.Ile1Leu)",
                ],
            )
            singleton_dataframe(values, wt, plot_wt_score=False)

        with self.assertRaises(ValueError):
            values = pd.Series(
                data=[1, 2, 3, 4],
                index=[
                    "c.1A>G (p.Ile1Leu)",
                    "c.3A>T (p.Ile3Leu)",
                    "c.5A>C (p.Ile5Leu)",
                    "_wt",
                ],
            )
            singleton_dataframe(values, wt, coding=True)

        with self.assertRaises(KeyError):
            values = pd.Series(
                data=[1, 2, 3, 4],
                index=[
                    "n.1A>G (p.Ile1Leu)",
                    "n.3A>T (p.Ile3Leu)",
                    "n.5A>C (p.Ile5Leu)",
                    "_wt",
                ],
            )
            singleton_dataframe(values, wt, coding=False)

        # out of bounds compared to wt sequence
        with self.assertRaises(ValueError):
            values = pd.Series(
                data=[1, 2, 3, 4],
                index=[
                    "c.1A>G (p.Ile1Leu)",
                    "c.3A>T (p.Ile3Leu)",
                    "c.51A>C (p.Ile5Leu)",
                    "_wt",
                ],
            )
            singleton_dataframe(values, wt, coding=False)

        with self.assertRaises(ValueError):
            cfg = {"coding": True, "reference offset": 0, "sequence": "TAA"}
            wt = WildTypeSequence("tests")
            wt.configure(cfg)
            values = pd.Series(data=[1], index=["c.1A>G (p.Ile1Leu)"])
            singleton_dataframe(values, wt, coding=False)

        with self.assertRaises(ValueError):
            cfg = {"coding": True, "reference offset": 3, "sequence": "TAATAA"}
            wt = WildTypeSequence("tests")
            wt.configure(cfg)
            values = pd.Series(data=[1], index=["c.4A>G (p.Ile1Leu)"])
            singleton_dataframe(values, wt, coding=False)


if __name__ == "__main__":
    unittest.main()
