import unittest
from ..libraries.variant import mutation_count, has_indel
from ..libraries.variant import protein_variant, get_variant_type
from ..libraries.variant import hgvs2single, single2hgvs
from ..libraries.variant import valid_variant, has_unresolvable
from ..base.constants import WILD_TYPE_VARIANT, SYNONYMOUS_VARIANT


class TestUtilitiesVariant(unittest.TestCase):
    """
    The purpose of this tests class is to tests if the utility functions in the
    variant submodule are correct.
    """

    def test_mutation_count(self):
        mutation_1 = "c.76A>C (p.Ile26Leu)"
        mutation_2 = "c.78C>T (p.Ile26Leu)"
        mutation_3 = "c.80A>G (p.Tyr27Cys)"
        wild_type = "_wt"
        synonymous = "_sy"

        one_mutation = mutation_count(mutation_1)
        two_mutations = mutation_count(", ".join([mutation_1, mutation_2]))
        three_mutations = mutation_count(
            ", ".join([mutation_1, mutation_2, mutation_3])
        )
        zero_mutations_wt = mutation_count(wild_type)
        zero_mutations_sy = mutation_count(synonymous)

        self.assertEqual(one_mutation, 1)
        self.assertEqual(two_mutations, 2)
        self.assertEqual(three_mutations, 3)
        self.assertEqual(zero_mutations_wt, 0)
        self.assertEqual(zero_mutations_sy, 0)

        # type checking
        with self.assertRaises(TypeError):
            mutation_count(None)
        with self.assertRaises(TypeError):
            mutation_count(2)
        with self.assertRaises(TypeError):
            mutation_count(b"c.76A>C (p.Ile26Leu)")
        with self.assertRaises(ValueError):
            mutation_count("")
        with self.assertRaises(ValueError):
            mutation_count("c.76A>C (p.Ile26Leu), c.76A>C (p.Ile26Leu)")
        with self.assertRaises(ValueError):
            mutation_count("c.76A>C (p.Ile26Leu),c.76A>C (p.Ile26Leu)")

    def test_noncoding_count(self):
        mutation_1 = "n.76A>C"
        mutation_2 = "n.76A>C, n.78C>T"
        mutation_3 = "n.76A>C, n.78C>T, n.80A>G"
        self.assertEqual(mutation_count(mutation_1), 1)
        self.assertEqual(mutation_count(mutation_2), 2)
        self.assertEqual(mutation_count(mutation_3), 3)

    def test_protein_counts(self):
        mutation_1 = "p.Ile26Leu"
        mutation_2 = "p.Ile26Leu, p.Tyr27Cys"
        mutation_3 = "p.Ile26Leu, p.Tyr27Cys, p.Ala28Leu"
        self.assertEqual(mutation_count(mutation_1), 1)
        self.assertEqual(mutation_count(mutation_2), 2)
        self.assertEqual(mutation_count(mutation_3), 3)

    def test_special_variant_counts(self):
        self.assertEqual(mutation_count(WILD_TYPE_VARIANT), 0)
        self.assertEqual(mutation_count(SYNONYMOUS_VARIANT), 0)

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
        with self.assertRaises(TypeError):
            has_indel(b"p.Gln8del")
        with self.assertRaises(ValueError):
            has_indel("")

    def test_get_protein_variant(self):
        variant_1 = "c.76A>C (p.Ile26Leu)"
        variant_2 = "c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu)"
        variant_3 = "c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu), c.80A>G (p.Tyr27Cys)"
        variant_4 = "c.76A>C (p.Ile26Leu), c.78C>T (p.Ile26Leu), c.81C>T (p.=)"
        self.assertEqual(protein_variant(variant_1), "p.Ile26Leu")
        self.assertEqual(protein_variant(variant_2), "p.Ile26Leu")
        self.assertEqual(protein_variant(variant_3), "p.Ile26Leu, p.Tyr27Cys")
        self.assertEqual(protein_variant(variant_4), "p.Ile26Leu")

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
            protein_variant(None)
        with self.assertRaises(TypeError):
            protein_variant(2)
        with self.assertRaises(TypeError):
            protein_variant(b"p.Ile26Leu")
        with self.assertRaises(ValueError):
            protein_variant("")

    def test_get_variant_type(self):
        self.assertEqual(get_variant_type("p.Ile26Leu"), "protein")
        self.assertEqual(get_variant_type("p.Ile26Leu, p.Ile26Val"), "protein")
        self.assertEqual(get_variant_type("c.76A>C"), None)
        self.assertEqual(get_variant_type("c.76A>C (p.Ile76Leu)"), "coding")
        self.assertEqual(get_variant_type("n.76>C"), None)
        self.assertEqual(get_variant_type("n.76A>C"), "noncoding")
        self.assertEqual(get_variant_type("n.76A>C (p.Ile26Leu)"), "noncoding")

    def test_hgvs2single_output(self):
        self.assertEqual(hgvs2single("p.Ile26Leu"), ["I26L"])
        self.assertEqual(hgvs2single("p.IleSerLeu"), [])
        self.assertEqual(hgvs2single("p.Ter26Leu"), ["*26L"])
        self.assertEqual(hgvs2single("p.Ter26???"), [])

    def test_single2hgvs_output(self):
        self.assertEqual(single2hgvs("I26L"), ["p.Ile26Leu"])
        self.assertEqual(single2hgvs("?26L"), [])
        self.assertEqual(single2hgvs("I2626L"), ["p.Ile2626Leu"])

    def test_valid_variant(self):
        self.assertTrue(valid_variant("c.76A>C (p.Ile26Leu)", is_coding=True))
        self.assertTrue(valid_variant("n.76A>C", is_coding=False))
        self.assertFalse(valid_variant("c.76 >C (p.Ile26Leu)", is_coding=True))
        self.assertFalse(valid_variant("c.76A>C (p.Ile26Leu)", is_coding=False))

    def test_if_has_unresolvable_aa_change(self):
        self.assertFalse(has_unresolvable("p.Ile26Leu"))
        self.assertTrue(has_unresolvable("p.???26Leu"))
        self.assertTrue(has_unresolvable("p.???26???"))


# -------------------------------------------------------------------------- #
#
#                                   MAIN

# -------------------------------------------------------------------------- #
if __name__ == "__main__":
    unittest.main()
