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
import pandas as pd

from enrich2.base.dataframe import fill_position_gaps, singleton_dataframe
from enrich2.base.dataframe import single_mutation_index, filter_coding_index


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUtilitiesDataframe)
    return suite


class TestUtilitiesDataframe(unittest.TestCase):

    def test_single_mutation_index(self):
        # test cases use all() because testing equality of indices returns a vector of booleans

        # test removal of double-mutants
        self.assertTrue(all(single_mutation_index(pd.Index(["c.76A>C (p.Ile26Leu)"])) == pd.Index(["c.76A>C (p.Ile26Leu)"])))
        self.assertTrue(all(single_mutation_index(pd.Index(["c.76A>C (p.Ile26Leu)", "c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu)"])) == pd.Index(["c.76A>C (p.Ile26Leu)"])))
        self.assertTrue(all(single_mutation_index(pd.Index(["c.76A>C (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])) == pd.Index(["c.76A>C (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])))
        self.assertTrue(all(single_mutation_index(pd.Index(["c.76A>C (p.Ile26Leu)", "c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])) == pd.Index(["c.76A>C (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])))

        # order matters
        self.assertFalse(all(single_mutation_index(pd.Index(["c.78C>T (p.Ile26Leu)", "c.76A>C (p.Ile26Leu)"])) == pd.Index(["c.76A>C (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])))

        # empty indices
        self.assertEqual(len(single_mutation_index(pd.Index([]))), 0)
        self.assertEqual(len(single_mutation_index(pd.Index(["c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu)"]))), 0)


    def test_filter_coding_index(self):
        # test cases use all() because testing equality of indices returns a vector of booleans

        # test removal of '???' variants
        self.assertTrue(all(filter_coding_index(pd.Index(["c.76A>C (p.Ile26Leu)"])) == pd.Index(["c.76A>C (p.Ile26Leu)"])))
        self.assertTrue(all(filter_coding_index(pd.Index(["c.76A>C (p.Ile26Leu)", "c.76A>N (p.Ile26???)"])) == pd.Index(["c.76A>C (p.Ile26Leu)"])))
        self.assertTrue(all(filter_coding_index(pd.Index(["c.76A>N (p.Ile26???)", "c.76A>C (p.Ile26Leu)"])) == pd.Index(["c.76A>C (p.Ile26Leu)"])))
        self.assertTrue(all(filter_coding_index(pd.Index(["c.76A>C (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])) == pd.Index(["c.76A>C (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])))
        self.assertTrue(all(filter_coding_index(pd.Index(["c.76A>C (p.Ile26Leu)", "c.76A>N (p.Ile26???)", "c.78C>T (p.Ile26Leu)"])) == pd.Index(["c.76A>C (p.Ile26Leu)", "c.78C>T (p.Ile26Leu)"])))

        # empty index
        self.assertEqual(len(filter_coding_index(pd.Index(["c.76A>N (p.Ile26???)"]))), 0)
        self.assertEqual(len(filter_coding_index(pd.Index([]))), 0)


    def test_single_mutations_to_tuples(self):
        pass


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

        # error checking
        with self.assertRaises(ValueError):
            fill_position_gaps([], 5)
        with self.assertRaises(TypeError):
            fill_position_gaps(None, 5)
        with self.assertRaises(TypeError):
            fill_position_gaps("abc", 5)
        with self.assertRaises(TypeError):
            fill_position_gaps([1, 2, "a"], 5)

    def test_singleton_dataframe(self):
        pass


if __name__ == "__main__":
    unittest.main()
