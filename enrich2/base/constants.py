"""
Enrich2 constants module
========================

This module contains all the constants used in the Enrich2 source code.
"""


import re
import collections


#: Variant string for counting wild type sequences
WILD_TYPE_VARIANT = "_wt"


#: Variant string for synonymous variants in 'synonymous' DataFrame
SYNONYMOUS_VARIANT = "_sy"


#: Logging constants
CALLBACK = "callback"
MESSAGE = "msg"
KWARGS = "kwargs"


#: HDFStore keys used by enrich2
GROUP_RAW = "raw"
GROUP_MAIN = "main"
BARCODEMAP_TABLE = "barcodemap"
IDENTIFIERS_TABLE = "identifiers"
SYNONYMOUS_TABLE = "synonymous"
VARIANTS_TABLE = "variants"
BARCODES_TABLE = "barcodes"
COUNTS_TABLE = "counts"
COUNTS_UNFILTERED_TABLE = "counts_unfiltered"
SCORES_TABLE = "scores"
SCORES_SHARED_TABLE = "scores_shared"
SCORES_SHARED_FULL_TABLE = "scores_shared_full"
SCORES_PVALUES_WT = "scores_pvalues_wt"
SCORES_PVALUES = "scores_pvalues"
OUTLIERS_TABLE = "outliers"
LOG_RATIOS_TABLE = "log_ratios"
WEIGHTS_TABLE = "weights"


#: Element types
VARIANTS = "variants"
BARCODES = "barcodes"
IDENTIFIERS = "identifiers"
SYNONYMOUS = "synonymous"


#: Dataframe columns used by Enrich2
PVALUE_RAW = "pvalue_raw"
Z_STAT = "z"
SCORE = "score"
COUNT = "count"
SE = "SE"
EPSILON = "epsilon"
INDEX = "index"
REPLICATES = "replicates"
VARIANCE = "var"
PARENT = "parent"


#: Standard codon table for translating wild type and variant DNA sequences
CODON_TABLE = {
    "TTT": "F",
    "TCT": "S",
    "TAT": "Y",
    "TGT": "C",
    "TTC": "F",
    "TCC": "S",
    "TAC": "Y",
    "TGC": "C",
    "TTA": "L",
    "TCA": "S",
    "TAA": "*",
    "TGA": "*",
    "TTG": "L",
    "TCG": "S",
    "TAG": "*",
    "TGG": "W",
    "CTT": "L",
    "CCT": "P",
    "CAT": "H",
    "CGT": "R",
    "CTC": "L",
    "CCC": "P",
    "CAC": "H",
    "CGC": "R",
    "CTA": "L",
    "CCA": "P",
    "CAA": "Q",
    "CGA": "R",
    "CTG": "L",
    "CCG": "P",
    "CAG": "Q",
    "CGG": "R",
    "ATT": "I",
    "ACT": "T",
    "AAT": "N",
    "AGT": "S",
    "ATC": "I",
    "ACC": "T",
    "AAC": "N",
    "AGC": "S",
    "ATA": "I",
    "ACA": "T",
    "AAA": "K",
    "AGA": "R",
    "ATG": "M",
    "ACG": "T",
    "AAG": "K",
    "AGG": "R",
    "GTT": "V",
    "GCT": "A",
    "GAT": "D",
    "GGT": "G",
    "GTC": "V",
    "GCC": "A",
    "GAC": "D",
    "GGC": "G",
    "GTA": "V",
    "GCA": "A",
    "GAA": "E",
    "GGA": "G",
    "GTG": "V",
    "GCG": "A",
    "GAG": "E",
    "GGG": "G",
}


#: Conversions between single- and three-letter amino acid codes
AA_CODES = {
    "Ala": "A",
    "A": "Ala",
    "Arg": "R",
    "R": "Arg",
    "Asn": "N",
    "N": "Asn",
    "Asp": "D",
    "D": "Asp",
    "Cys": "C",
    "C": "Cys",
    "Glu": "E",
    "E": "Glu",
    "Gln": "Q",
    "Q": "Gln",
    "Gly": "G",
    "G": "Gly",
    "His": "H",
    "H": "His",
    "Ile": "I",
    "I": "Ile",
    "Leu": "L",
    "L": "Leu",
    "Lys": "K",
    "K": "Lys",
    "Met": "M",
    "M": "Met",
    "Phe": "F",
    "F": "Phe",
    "Pro": "P",
    "P": "Pro",
    "Ser": "S",
    "S": "Ser",
    "Thr": "T",
    "T": "Thr",
    "Trp": "W",
    "W": "Trp",
    "Tyr": "Y",
    "Y": "Tyr",
    "Val": "V",
    "V": "Val",
    "Ter": "*",
    "*": "Ter",
    "???": "?",
    "?": "???",
}


#: List of amino acids in row order for sequence-function maps.
AA_LIST = [
    "H",
    "K",
    "R",  # (+)
    "D",
    "E",  # (-)
    "C",
    "M",
    "N",
    "Q",
    "S",
    "T",  # Polar-neutral
    "A",
    "G",
    "I",
    "L",
    "P",
    "V",  # Non-polar
    "F",
    "W",
    "Y",  # Aromatic
    "*",
]


#: List of tuples for amino acid physiochemical property groups.
#: Each tuple contains the label string and the corresponding start and end
#: indices in :py:const:`aa_list` (inclusive).
AA_LABEL_GROUPS = [
    ("(+)", 0, 2),
    ("(-)", 3, 4),
    ("Polar-neutral", 5, 10),
    ("Non-polar", 11, 16),
    ("Aromatic", 17, 19),
]


#: List of nucleotides in row order for sequence-function maps.
NT_LIST = ["A", "C", "G", "T"]


#: Dictionary specifying available scoring methods for the analysis
#: Key is the internal name of the method, value is the GUI label
#: For command line options, internal name is used for the option string itself
#: and the value is the help string
SCORING_METHODS = collections.OrderedDict(
    [
        ("WLS", "weighted least squares"),
        ("ratios", "log ratios (Enrich2)"),
        ("counts", "counts only"),
        ("OLS", "ordinary least squares"),
        ("simple", "log ratios (old Enrich)"),
    ]
)


#: Dictionary specifying available scoring methods for the analysis
#: Key is the internal name of the method, value is the GUI label
#: For command line options, internal name is used for the option string itself
#: and the value is the help string
LOGR_METHODS = collections.OrderedDict(
    [
        ("wt", "wild type"),
        ("complete", "library size (complete cases)"),
        ("full", "library size (all reads)"),
    ]
)


#: List specifying valid labels in their sorted order
#: Sorted order is the order in which they should be calculated in
ELEMENT_LABELS = ["barcodes", "identifiers", "variants", "synonymous"]


#: Default number of maximum mutation.
#: Must be set to avoid data frame performance errors.
DEFAULT_MAX_MUTATIONS = 10


#: Matches a single amino acid substitution in HGVS_ format.
re_protein = re.compile(
    "(?P<match>p\.(?P<pre>[A-Z][a-z][a-z])(?P<pos>-?\d+)" "(?P<post>[A-Z][a-z][a-z]))"
)


#: Matches a single nucleotide substitution (coding or noncoding)
#: in HGVS_ format.
re_nucleotide = re.compile(
    "(?P<match>[nc]\.(?P<pos>-?\d+)(?P<pre>[ACGT])>(?P<post>[ACGT]))"
)


#: Matches a single coding nucleotide substitution in HGVS_ format.
re_coding = re.compile(
    "(?P<match>c\.(?P<pos>-?\d+)(?P<pre>[ACGT])>(?P<post>[ACGT]) "
    "\(p\.(?:=|[A-Z][a-z][a-z]-?\d+[A-Z][a-z][a-z])\))"
)


#: Matches a single noncoding nucleotide substitution in HGVS_ format.
re_noncoding = re.compile(
    "(?P<match>n\.(?P<pos>-?\d+)(?P<pre>[ACGT])>(?P<post>[ACGT]))"
)
