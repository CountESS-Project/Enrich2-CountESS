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
from enrich2.libraries.variant import mutation_count, has_indel
from enrich2.libraries.variant import protein_variant
from enrich2.libraries.variant import re_protein, re_coding, re_noncoding
from enrich2.constants import WILD_TYPE_VARIANT, SYNONYMOUS_VARIANT


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUtilitiesVariant)
    return suite


class TestUtilitiesVariant(unittest.TestCase):

    def test_mutation_count(self):
        # coding changes
        self.assertEqual(mutation_count("c.76A>C (p.Ile26Leu)"), 1)
        self.assertEqual(mutation_count("c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu)"), 2)
        self.assertEqual(mutation_count("c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu), c.80A>G (p.Tyr27Cys)"), 3)
        self.assertEqual(mutation_count("c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu), c.81C>T (p.=)"), 3)

        # noncoding changes
        self.assertEqual(mutation_count("n.76A>C"), 1)
        self.assertEqual(mutation_count("n.76A>C, n.78C>T"), 2)
        self.assertEqual(mutation_count("n.76A>C, n.78C>T, n.80A>G"), 3)

        # protein changes
        self.assertEqual(mutation_count("p.Ile26Leu"), 1)
        self.assertEqual(mutation_count("p.Ile26Leu, p.Tyr27Cys"), 2)
        self.assertEqual(mutation_count("p.Ile26Leu, p.Tyr27Cys, p.Ala28Leu"), 3)

        # special variants
        self.assertEqual(mutation_count(WILD_TYPE_VARIANT), 0)
        self.assertEqual(mutation_count(SYNONYMOUS_VARIANT), 0)

        # type checking
        with self.assertRaises(TypeError):
            mutation_count(None)
        with self.assertRaises(TypeError):
            mutation_count(2)
        with self.assertRaises(ValueError):
            mutation_count("")


    def test_has_indel(self):
        # coding changes
        self.assertTrue(has_indel("c.76_78del"))
        self.assertTrue(has_indel("c.76_78delACT"))
        self.assertTrue(has_indel("c.77_79dup"))
        self.assertTrue(has_indel("c.77_79dupCTG"))
        self.assertTrue(has_indel("c.76_77insT"))
        self.assertTrue(has_indel("c.112_117delinsTG"))
        self.assertTrue(has_indel("c.112_117delAGGTCAinsTG"))
        self.assertFalse(has_indel("c.76A>C"))

        # noncoding changes
        self.assertTrue(has_indel("n.76_78del"))
        self.assertTrue(has_indel("n.76_78delACT"))
        self.assertTrue(has_indel("n.77_79dup"))
        self.assertTrue(has_indel("n.77_79dupCTG"))
        self.assertTrue(has_indel("n.76_77insT"))
        self.assertTrue(has_indel("n.112_117delinsTG"))
        self.assertTrue(has_indel("n.112_117delAGGTCAinsTG"))
        self.assertFalse(has_indel("n.76A>C"))

        # protein changes
        self.assertTrue(has_indel("p.Gln8del"))
        self.assertTrue(has_indel("p.Gly4_Gln6dup"))
        self.assertTrue(has_indel("p.Lys2_Met3insGlnSerLys"))
        self.assertFalse(has_indel("p.Trp26Cys"))
        self.assertFalse(has_indel("p.="))

        # special variants
        self.assertFalse(has_indel(WILD_TYPE_VARIANT))
        self.assertFalse(has_indel(SYNONYMOUS_VARIANT))

        # type checking
        with self.assertRaises(TypeError):
            has_indel(None)
        with self.assertRaises(TypeError):
            has_indel(2)
        with self.assertRaises(ValueError):
            has_indel("")


    def test_protein_variant(self):
        # coding changes
        self.assertEqual(protein_variant("c.76A>C (p.Ile26Leu)"), "p.Ile26Leu")
        self.assertEqual(protein_variant("c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu)"), "p.Ile26Leu")
        self.assertEqual(protein_variant("c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu), c.80A>G (p.Tyr27Cys)"), "p.Ile26Leu, p.Tyr27Cys")
        self.assertEqual(protein_variant("c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu), c.81C>T (p.=)"), "p.Ile26Leu")
        
        # noncoding changes
        with self.assertRaises(ValueError):
            protein_variant("n.76A>C")
        with self.assertRaises(ValueError):
            protein_variant("n.76A>C, n.78C>T")
        with self.assertRaises(ValueError):
            protein_variant("n.76A>C, n.78C>T, n.80A>G")

        # protein changes
        with self.assertRaises(ValueError):
            protein_variant("p.Ile26Leu")
        with self.assertRaises(ValueError):
            protein_variant("p.Ile26Leu, p.Tyr27Cys")
        with self.assertRaises(ValueError):
            protein_variant("p.Ile26Leu, p.Tyr27Cys, p.Ala28Leu")

        # special variants
        self.assertEqual(protein_variant(WILD_TYPE_VARIANT), WILD_TYPE_VARIANT)
        self.assertEqual(protein_variant(SYNONYMOUS_VARIANT), SYNONYMOUS_VARIANT)

        # type checking
        with self.assertRaises(TypeError):
            mutation_count(None)
        with self.assertRaises(TypeError):
            mutation_count(2)
        with self.assertRaises(ValueError):
            mutation_count("")


    def test_re_protein(self):
        pass


    def test_re_coding(self):
        pass


    def test_re_noncoding(self):
        pass


if __name__ == "__main__":
    unittest.main()
