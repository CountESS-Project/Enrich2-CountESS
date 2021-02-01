import unittest

from ..libraries.barcodevariant import BcvSeqLib
from .utilities import load_config_data, create_file_path
from .methods import HDF5TestComponent


CFG_FILE = "barcodevariant_coding.json"
CFG_DIR = "data/config/barcodevariant/"
READS_DIR = create_file_path("barcodevariant/", "data/reads/")
RESULT_DIR = "data/result/barcodevariant/"

LIBTYPE = "barcodevariant"
FILE_EXT = "tsv"
FILE_SEP = "\t"
CODING_STR = "c"


# -------------------------------------------------------------------------- #
#
#                   Integrated Filter and Settings Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibCountsIntegrated(unittest.TestCase):
    """
    Integrated tests of all of the libraries config settings at once.
    """

    def setUp(self):
        prefix = "integrated"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/{}_barcode_map.txt".format(READS_DIR, prefix)

        # Set all filter parameters
        cfg["fastq"]["filters"]["max N"] = 0
        cfg["fastq"]["filters"]["chastity"] = True
        cfg["fastq"]["filters"]["avg quality"] = 38
        cfg["fastq"]["filters"]["min quality"] = 20

        # Set trim parameters
        cfg["fastq"]["start"] = 4
        cfg["fastq"]["length"] = 3
        cfg["fastq"]["reverse"] = True

        # Set barcode parameters
        cfg["barcodes"]["min count"] = 2

        # # Set Variant parameters
        cfg["variants"]["wild type"]["sequence"] = "TTTTTT"
        cfg["variants"]["wild type"]["reference offset"] = 3
        cfg["variants"]["min count"] = 3
        cfg["variants"]["max mutations"] = 1
        cfg["variants"]["use aligner"] = True

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                   Barcode Min Conut Filter Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibCountsBarcodesMinCountFilter(unittest.TestCase):
    """
    Test that barcodes with a minimum count under 2 are correctly removed
    """

    def setUp(self):
        prefix = "barcodes_mincount"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/barcode_map.txt".format(READS_DIR)

        # Set barcode parameters
        cfg["barcodes"]["min count"] = 2

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          Counts Only Mode Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibCountsCountsOnlyMode(unittest.TestCase):
    """
    Test counts only mode correctly reads barcodes in from a tsv with
    count values column.
    """

    def setUp(self):
        prefix = "counts_only"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["counts file"] = "{}/{}.tsv".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/barcode_map.txt".format(READS_DIR)

        # Set barcode parameters
        cfg["barcodes"]["min count"] = 4

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          FQ Filter Avg Quality Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibCountsAvgQFQFilter(unittest.TestCase):
    """
    Test that the FQ Filter average quality setting works at removing
    barcodes with average base quality less than 39 (H)
    """

    def setUp(self):
        prefix = "filter_avgq"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/barcode_map.txt".format(READS_DIR)

        # Set barcode parameters
        cfg["fastq"]["filters"]["avg quality"] = 39

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          FQ Filter Min Quality Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibCountsMinQFQFilter(unittest.TestCase):
    """
    Test that the FQ Filter average quality setting works at removing
    barcodes with containing any base qualities less than 39 (H)
    """

    def setUp(self):
        prefix = "filter_minq"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/barcode_map.txt".format(READS_DIR)

        # Set barcode parameters
        cfg["fastq"]["filters"]["min quality"] = 39

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          FQ Filter Max N Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibCountsMaxNFQFilter(unittest.TestCase):
    """
    Test that the FQ Filter average quality setting works at removing
    barcodes with more than 0 N bases.
    """

    def setUp(self):
        prefix = "filter_maxn"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/barcode_map.txt".format(READS_DIR)

        # Set barcode parameters
        cfg["fastq"]["filters"]["max N"] = 0

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          FQ Filter Chastity Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibCountsNotChasteFQFilter(unittest.TestCase):
    """
    Test that the FQ Filter average quality setting works at removing
    barcodes that are not chaste.
    """

    def setUp(self):
        prefix = "filter_chastity"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/barcode_map.txt".format(READS_DIR)

        # Set barcode parameters
        cfg["fastq"]["filters"]["chastity"] = True

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          Detect Multi-Mutation Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibDetectMultiMutations(unittest.TestCase):
    """
    Test that barcodes with multiple mutations in the barcode map value
    are displayed correctly.
    """

    def setUp(self):
        prefix = "multi_mut"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/{}_barcode_map.txt".format(READS_DIR, prefix)

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          Detect Single-Mutation Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibDetectSingleMutations(unittest.TestCase):
    """
    Test that barcodes with only a single mutation in the barcode map value
    are displayed correctly, as well as those with multiple mutations within
    a single codon.
    """

    def setUp(self):
        prefix = "single_mut"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/{}_barcode_map.txt".format(READS_DIR, prefix)

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          FQ Reverse Complement Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibWithRevcomp(unittest.TestCase):
    """
    Test that the reverse complement function correctly applies to each barcode
    so that they can map to a barcode map and be counted properly.
    """

    def setUp(self):
        prefix = "revcomp"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/{}_barcode_map.txt".format(READS_DIR, prefix)

        # Set barcode parameters
        cfg["fastq"]["reverse"] = True

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                         FQ Trim Length Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibWithTrimLengthAt3(unittest.TestCase):
    """
    Test that fq reads are trimmed to the correct length (3) beginning at the
    start of the fq read (pos 1).
    """

    def setUp(self):
        prefix = "trim_len"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/{}_barcode_map.txt".format(READS_DIR, prefix)

        # Set barcode parameters
        cfg["fastq"]["length"] = 3

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          FQ Trim Start Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibWithTrimStartAt4(unittest.TestCase):
    """
    Test that fq reads are trimmed at the correct starting position (pos 4)
    """

    def setUp(self):
        prefix = "trim_start"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/{}_barcode_map.txt".format(READS_DIR, prefix)

        # Set barcode parameters
        cfg["fastq"]["start"] = 4

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          Synonymous Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibDetectSynonymous(unittest.TestCase):
    """
    Test that synonymous mutations are correctly detected
    """

    def setUp(self):
        prefix = "synonymous"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/{}_barcode_map.txt".format(READS_DIR, prefix)

        # Set barcode parameters
        cfg["variants"]["wild type"]["sequence"] = "CCTCCT"

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          Detect WildType Test
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibDetectWildtype(unittest.TestCase):
    """
    Test that non-variants are correctly detected
    """

    def setUp(self):
        prefix = "wildtype"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/barcode_map.txt".format(READS_DIR)

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          Variant Max mutations filter
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibWithVariantMaxMutationsFilter(unittest.TestCase):
    """
    Test that variants with more than one mutation are filtered out, even
    those with multiple mutations on a single codon.
    """

    def setUp(self):
        prefix = "variant_maxmutations"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/barcode_map.txt".format(READS_DIR)

        # Set barcode parameters
        cfg["variants"]["max mutations"] = 1

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          Variant Min Count Filter
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibWithVariantMinCountFilter(unittest.TestCase):
    """
    Test that variants with less than a count of 2 are removed.
    """

    def setUp(self):
        prefix = "variant_mincount"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/barcode_map.txt".format(READS_DIR)

        # Set barcode parameters
        cfg["variants"]["min count"] = 2

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                          Variant With Reference Offset
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibWithReferenceOffset(unittest.TestCase):
    """
    Test that variants are reported with the offset added correctly to
    nucleotide and residue locations.
    """

    def setUp(self):
        prefix = "variant_refoffset"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/barcode_map.txt".format(READS_DIR)

        # Set barcode parameters
        cfg["variants"]["wild type"]["reference offset"] = 3

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                     Variant With Use Aligner Setting
#
# -------------------------------------------------------------------------- #
class TestBcvSeqLibWithUseAlignerSetting(unittest.TestCase):
    """
    Test that variants are reported correctly wrt the wildtype sequence
    when using alignment.
    """

    def setUp(self):
        prefix = "variant_use_aligner"
        cfg = load_config_data(CFG_FILE, CFG_DIR)
        cfg["fastq"]["reads"] = "{}/{}.fq".format(READS_DIR, prefix)
        cfg["barcodes"]["map file"] = "{}/{}_barcode_map.txt".format(READS_DIR, prefix)

        # Set barcode parameters
        cfg["variants"]["use aligner"] = True

        self.test_component = HDF5TestComponent(
            store_constructor=BcvSeqLib,
            cfg=cfg,
            result_dir=RESULT_DIR,
            file_ext=FILE_EXT,
            file_sep=FILE_SEP,
            save=False,
            verbose=False,
            libtype=prefix,
            scoring_method="",
            logr_method="",
            coding="coding",
        )
        self.test_component.setUp()

    def tearDown(self):
        self.test_component.tearDown()

    def test_all_hdf5_dataframes(self):
        self.test_component.runTest()


# -------------------------------------------------------------------------- #
#
#                                   MAIN
#
# -------------------------------------------------------------------------- #
if __name__ == "__main__":
    unittest.main()
