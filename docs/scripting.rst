Scripting
=========

.. _howto-script:

This section will describe how to create your own custom scoring script to
use with Enrich2. By default, Enrich2 ships with several default scoring
functions installed into the folder ``.enrich2`` in your home directory. To use
your own custom script, place the file into this directory.


Creating a scorer
-----------------
To begin, import the appropriate base class and create a new class:

.. code-block:: python
   :linenos:

    from enrich2.plugins.scoring import BaseScorerPlugin

    class ExampleScorer(BaseScorerPlugin):
        name = '...'
        author = '...'
        version = '...'

        def compute_scores(self):
            # Code for computing score

You will need to subclass the abstract class :py:class:`~enrich2.plugins.scoring.BaseScorerPlugin`
and provide an implmentation for the function ``compute_scores``. This function
needs to take the count information from tables ``/main/<type>/counts`` and
place the newly computed data into ``/main/<type>/scores``. If Enrich2 cannot
find these tables after running your script, an error will be thrown and analysis will be aborted.
You may also choose to store other information for later downstream analysis.

The token ``<type>`` is to be replaced with an appropriate element type. See
:ref:`_intro-elements:` for more information.

Additionally, your class will need to define the three class variables
``name``, ``author`` and ``version`` at the top level. Each scripting file
you create can only have one class subclassing :py:class:`~enrich2.plugins.scoring.BaseScorerPlugin`.


Accessing Enrich2 constants
---------------------------
Enrich2 uses the following constants that you might find useful:

.. code-block:: python
   :linenos:

    #: Variant string for counting wild type sequences
    WILD_TYPE_VARIANT = "_wt"


    #: Variant string for synonymous variants in 'synonymous' DataFrame
    SYNONYMOUS_VARIANT = "_sy"


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
    OUTLIERS_TABLE = 'outliers'


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
            'TTT':'F', 'TCT':'S', 'TAT':'Y', 'TGT':'C',
            'TTC':'F', 'TCC':'S', 'TAC':'Y', 'TGC':'C',
            'TTA':'L', 'TCA':'S', 'TAA':'*', 'TGA':'*',
            'TTG':'L', 'TCG':'S', 'TAG':'*', 'TGG':'W',
            'CTT':'L', 'CCT':'P', 'CAT':'H', 'CGT':'R',
            'CTC':'L', 'CCC':'P', 'CAC':'H', 'CGC':'R',
            'CTA':'L', 'CCA':'P', 'CAA':'Q', 'CGA':'R',
            'CTG':'L', 'CCG':'P', 'CAG':'Q', 'CGG':'R',
            'ATT':'I', 'ACT':'T', 'AAT':'N', 'AGT':'S',
            'ATC':'I', 'ACC':'T', 'AAC':'N', 'AGC':'S',
            'ATA':'I', 'ACA':'T', 'AAA':'K', 'AGA':'R',
            'ATG':'M', 'ACG':'T', 'AAG':'K', 'AGG':'R',
            'GTT':'V', 'GCT':'A', 'GAT':'D', 'GGT':'G',
            'GTC':'V', 'GCC':'A', 'GAC':'D', 'GGC':'G',
            'GTA':'V', 'GCA':'A', 'GAA':'E', 'GGA':'G',
            'GTG':'V', 'GCG':'A', 'GAG':'E', 'GGG':'G'
        }


    #: Conversions between single- and three-letter amino acid codes
    AA_CODES = {
            'Ala' : 'A', 'A' : 'Ala',
            'Arg' : 'R', 'R' : 'Arg',
            'Asn' : 'N', 'N' : 'Asn',
            'Asp' : 'D', 'D' : 'Asp',
            'Cys' : 'C', 'C' : 'Cys',
            'Glu' : 'E', 'E' : 'Glu',
            'Gln' : 'Q', 'Q' : 'Gln',
            'Gly' : 'G', 'G' : 'Gly',
            'His' : 'H', 'H' : 'His',
            'Ile' : 'I', 'I' : 'Ile',
            'Leu' : 'L', 'L' : 'Leu',
            'Lys' : 'K', 'K' : 'Lys',
            'Met' : 'M', 'M' : 'Met',
            'Phe' : 'F', 'F' : 'Phe',
            'Pro' : 'P', 'P' : 'Pro',
            'Ser' : 'S', 'S' : 'Ser',
            'Thr' : 'T', 'T' : 'Thr',
            'Trp' : 'W', 'W' : 'Trp',
            'Tyr' : 'Y', 'Y' : 'Tyr',
            'Val' : 'V', 'V' : 'Val',
            'Ter' : '*', '*' : 'Ter',
            '???' : '?', '?' : '???'
    }


    #: List of amino acids in row order for sequence-function maps.
    AA_LIST = ['H', 'K', 'R',                 # (+)
               'D', 'E',                      # (-)
               'C', 'M', 'N', 'Q', 'S', 'T',  # Polar-neutral
               'A', 'G', 'I', 'L', 'P', 'V',  # Non-polar
               'F', 'W', 'Y',                 # Aromatic
               '*']


    #: List of tuples for amino acid physiochemical property groups.
    #: Each tuple contains the label string and the corresponding start and end
    #: indices in :py:const:`aa_list` (inclusive).
    AA_LABEL_GROUPS = [("(+)", 0, 2),
                       ("(-)", 3, 4),
                       ("Polar-neutral", 5, 10),
                       ("Non-polar", 11, 16),
                       ("Aromatic", 17, 19)]


    #: List of nucleotides in row order for sequence-function maps.
    NT_LIST = ['A', 'C', 'G', 'T']


    #: Dictionary specifying available scoring methods for the analysis
    #: Key is the internal name of the method, value is the GUI label
    #: For command line options, internal name is used for the option string itself
    #: and the value is the help string
    SCORING_METHODS = collections.OrderedDict([
                                    ("WLS", "weighted least squares"),
                                    ("ratios", "log ratios (Enrich2)"),
                                    ("counts", "counts only"),
                                    ("OLS", "ordinary least squares"),
                                    ("simple", "log ratios (old Enrich)"),
                                    ])


    #: Dictionary specifying available scoring methods for the analysis
    #: Key is the internal name of the method, value is the GUI label
    #: For command line options, internal name is used for the option string itself
    #: and the value is the help string
    LOGR_METHODS = collections.OrderedDict([
                                ("wt", "wild type"),
                                ("complete", "library size (complete cases)"),
                                ("full", "library size (all reads)"),
                                ])


    #: List specifying valid labels in their sorted order
    #: Sorted order is the order in which they should be calculated in
    ELEMENT_LABELS = ['barcodes', 'identifiers', 'variants', 'synonymous']


    #: Default number of maximum mutation.
    #: Must be set to avoid data frame performance errors.
    DEFAULT_MAX_MUTATIONS = 10


    #: Matches a single amino acid substitution in HGVS_ format.
    re_protein = re.compile(
        "(?P<match>p\.(?P<pre>[A-Z][a-z][a-z])(?P<pos>-?\d+)"
        "(?P<post>[A-Z][a-z][a-z]))")


    #: Matches a single nucleotide substitution (coding or noncoding)
    #: in HGVS_ format.
    re_nucleotide = re.compile(
        "(?P<match>[nc]\.(?P<pos>-?\d+)(?P<pre>[ACGT])>(?P<post>[ACGT]))")


    #: Matches a single coding nucleotide substitution in HGVS_ format.
    re_coding = re.compile(
        "(?P<match>c\.(?P<pos>-?\d+)(?P<pre>[ACGT])>(?P<post>[ACGT]) "
        "\(p\.(?:=|[A-Z][a-z][a-z]-?\d+[A-Z][a-z][a-z])\))")


    #: Matches a single noncoding nucleotide substitution in HGVS_ format.
    re_noncoding = re.compile(
        "(?P<match>n\.(?P<pos>-?\d+)(?P<pre>[ACGT])>(?P<post>[ACGT]))")

Import the module ``contstants`` to use these in your scoring function:

.. code-block:: python
   :linenos:

   from enrich2.base import contants


Accessing Enrich2 information
-----------------------------
The class :py:class:`~enrich2.plugins.scoring.BaseScorerPlugin` provides
a thin layer for interacting with the tables in Enrich2 memory:

.. code-block:: python
   :linenos:

    self.store_get(key)
    self.store_put(...)
    self.store_remove(...)
    self.store_append(...)
    self.store_check(key)
    self.store_select(...)
    self.store_select_as_multiple(...)

You will also have for obtaining information about sequencing libraries,
such as the coding status, timepoints and wildtype sequence:

.. code-block:: python
   :linenos:

    self.store_has_wt_sequence()
    self.store_wt_sequence()
    self.store_is_coding()
    self.store_timepoint_keys()
    self.store_timepoints()
    self.store_keys()
    self.store_key_roots()
    self.store_labels()

See :py:class:`~enrich2.plugins.scoring.BaseScorerPlugin` for more information
regarding these methods.

Defining options
----------------
Your script might need to define parameters that can be set in a configuration
file or be edited in the GUI. The following code block shows an example
of importing and creating an options.

.. code-block:: python
   :linenos:

    from enrich2.plugins.options import Options

    options = Options()
    options.add_option(
        name="Normalization Method",
        varname="logr_method",
        dtype=str,
        default='Wild Type',
        choices={'Wild Type': 'wt', 'Full': 'full', 'Complete': 'complete'},
        hidden=False
    )
    options.add_option(
        name="Weighted",
        varname="weighted",
        dtype=bool,
        default=True,
        choices={},
        hidden=False
    )

To create your own options, create a new instance of the ``Options`` class.
This class takes no arguments. To add an option, call the ``add_option`` method
and fill out the parameters with appropriate information:

The ``name`` argument represents the string to be rendered to the GUI.

The ``varname`` argument represents the name the variable is referenced by
in your script. Each option must have a unique ``varname``.

The ``dtype`` parameters represents the expected data-type of the option.
If someone tries to set a non-matching data-type, an error will be thrown
either in the GUI or at run-time.

The ``default`` argument should be the default value of your option.

The ``choices`` argument is a dictionary for representing pre-defined selection
of choices for the variable. The key should be a human-readable string for
rendering in the GUI and the value should be the allowed values. If your
option does not have any choices, pass an empty dictionary.

The ``hidden`` argument signifies if the option should be rendered in the GUI.
Set this to false if your option is something more advanced than a ``float``,
``int``, ``string`` or ``bool``.

You can only define `one` instance of ``Options`` in a script.


Logging Messages
----------------
In order to log messages to the Enrich2 terminal, import the ``log_message``
function and the logging module:

.. code-block:: python
   :linenos:

    import logging
    from enrich2.base.utils import log_message

In order to use this function, supply a function to use from the logging
module, a message and a dictionary with the key ``oname`` for the ``extra``
parameter:

.. code-block:: python
   :linenos:

    log_message(
        logging_callback=logging.info,
        msg='Hello World!',
        extra={'oname': 'name of object'}
    )