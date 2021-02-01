"""
Enrich2 libraries variant module
================================

Contains the abstract class ``VariantSeqLib`` common to all sequencing library
classes used in ``Enrich2`` that deal with coding/noncoding variants.
"""


import logging
import re

from ..base.constants import re_coding, re_noncoding, re_protein
from .seqlib import SeqLib
from ..base.constants import AA_CODES, CODON_TABLE, DEFAULT_MAX_MUTATIONS
from ..base.constants import SYNONYMOUS_VARIANT, WILD_TYPE_VARIANT
from ..sequence.aligner import Aligner
from ..sequence.wildtype import WildTypeSequence
from ..base.utils import log_message


__all__ = [
    "valid_variant",
    "hgvs2single",
    "single2hgvs",
    "get_variant_type",
    "mutation_count",
    "has_indel",
    "has_unresolvable",
    "protein_variant",
    "VariantSeqLib",
]


def _validate_str(s):
    """
    Checks if a string is valid. Internal use only.
    
    Parameters
    ----------
    s : `str`
        String to validate.
    """
    if not isinstance(s, str):
        raise TypeError("Expected string, got {}".format(type(s)))
    if len(s) == 0:
        raise ValueError("Empty variant string.")
    return


def valid_variant(s, is_coding=True):
    """
    Returns True if s is a valid coding or noncoding variant, else False.
    
    Parameters
    ----------
    s : `str`
        Variant string to validate.
    is_coding : `bool`
        Indicates if the variant string represents a coding variant.
    """
    _validate_str(s)
    if s == WILD_TYPE_VARIANT:
        return True
    else:
        if is_coding:
            for mut in s.split(", "):
                match = re_coding.match(mut)
                if match is None:
                    return False
            return True
        else:
            for mut in s.split(", "):
                match = re_noncoding.match(mut)
                if match is None:
                    return False
            return True


def hgvs2single(s):
    """
    Convert HGVS string from Enrich2 to <pre><pos><post>
    single-letter amino acid variant string.
    
    Parameters
    ----------
    s : `str`
        String in HGVS format to convert.
        
    Returns
    -------
    `list`
        Returns a list of single-letter variants.
    """
    _validate_str(s)
    t = re_protein.findall(s)
    return ["{}{}{}".format(AA_CODES[m[1]], m[2], AA_CODES[m[3]]) for m in t]


def single2hgvs(s):
    """
    Convert single-letter amino acid changes in the form
    <pre><pos><post> into HGVS strings that match Enrich2 
    output.

    Searches the string s for all instances of the above
    pattern and returns a list of Enrich2 variants.
    
    Parameters
    ----------
    s : `str`
        String in single-letter format to convert.
        
    Returns
    -------
    `list`
        Returns a list of HGVS variants.
    """
    _validate_str(s)
    t = re.findall("[A-Z*]\d+[A-Z*]", s)
    return ["p.{}{}{}".format(AA_CODES[x[0]], x[1:-1], AA_CODES[x[-1]]) for x in t]


def get_variant_type(variant):
    """
    Use regular expressions to determine whether the variant is protein,
    coding, or noncoding.
    
    Parameters
    ----------
    variant : `str`
        variant string
        
    Returns
    -------
    `str`
        ``'protein'``, ``'coding'``, or ``'noncoding'`` depending on which 
        regular expression matches, else ``None``. Note that both wild type 
        and synonymous special variants will return ``None``.
    """
    _validate_str(variant)
    v = variant.split(", ")[0]  # test first token of multi-mutant
    if re_protein.match(v) is not None:
        return "protein"
    elif re_coding.match(v) is not None:
        return "coding"
    elif re_noncoding.match(v) is not None:
        return "noncoding"
    else:
        return None


def mutation_count(variant):
    """
    Counts the number of mutations in the HGVS_ *variant*.
    
    Parameters
    ----------
    variant : `str`
        variant string
    
    Returns
    -------
    `int`
        Number of variants (0 if wild type or synonymous)
    """
    _validate_str(variant)
    if variant == WILD_TYPE_VARIANT:
        return 0
    elif variant == SYNONYMOUS_VARIANT:
        return 0
    else:
        result = [x.strip() for x in variant.split(",")]
        if len(set(result)) != len(result):
            raise ValueError("Duplicate mutant substrings found in variant")
        return len(result)


def has_indel(variant):
    """
    Tests if the HGVS_ *variant* contains an indel mutation.
    
    Parameters
    ----------
    variant : `str`
        variant string
    
    Returns
    -------
    `bool`
        ``True`` if there is an indel, else ``False``
    """
    _validate_str(variant)
    if variant == WILD_TYPE_VARIANT:
        return False
    elif variant == SYNONYMOUS_VARIANT:
        return False
    else:
        return any(x in variant for x in ("ins", "del", "dup"))


def has_unresolvable(variant):
    """
    Tests if the HGVS_ *variant* has an unresolvable amino acid change.

    Unresolvable amino acid changes are most commonly caused by the presence
    of N or X nucleotides, resulting in a non-translatable codon. They are
    also found when a frameshift causes the last part of the coding sequence
    to not have three nucleotides.
    
    Parameters
    ----------
    variant : `str`
        The variant string
    
    Returns
    -------
    `bool`
        ``True`` if there is an unresolvable change, else ``False``
    """
    _validate_str(variant)
    if AA_CODES["?"] in variant:
        return True
    else:
        return False


def protein_variant(variant):
    """
    Return an HGVS_ variant string containing only the protein changes in a
    coding HGVS_ variant string. If all variants are synonymous, returns the
    synonymous variant code. If the variant is wild type, returns the wild
    type variant.
    
    Parameters
    ----------
    variant : `str`
        The coding variant string
    
    Returns
    -------
    `str`
        Protein variant string (or synonymous or wild type)    
    """
    _validate_str(variant)
    if variant == WILD_TYPE_VARIANT:
        return WILD_TYPE_VARIANT
    elif variant == SYNONYMOUS_VARIANT:
        return SYNONYMOUS_VARIANT
    else:
        matches = re.findall("\((p\.\S*)\)", variant)
        if len(matches) == 0:
            raise ValueError("Invalid coding variant string.")
        # uniqify and remove synonymous
        seen = {"p.=": True}
        unique_matches = list()
        for v in matches:
            if v in seen:
                continue
            else:
                seen[v] = True
                unique_matches.append(v)
        if len(unique_matches) == 0:
            return SYNONYMOUS_VARIANT
        else:
            return ", ".join(unique_matches)


class VariantSeqLib(SeqLib):
    """
    Abstract :py:class:`~enrich2.libraries.seqlib.SeqLib` class for for Enrich 
    libraries containing variants. Implements core functionality for assessing 
    variants, either coding or noncoding. Subclasess must evaluate the variant 
    DNA sequences that are being counted.
    
    Attributes
    ----------
    wt : :py:class:`~enrich2.sequence.wildtype.WildType`
        WildType sequence object variants are called against.
    aligner : :py:class:`~enrich2.sequence.aligner.Aligner`
        The aligner object used to align reads to a reference.
    aligner_cache : `dict`
        Cache of aligned reads.
    variant_min_count : `int`
        Minimum count of a variant to use during filtering.
    max_mutations : `int`
        Max mutations in a variant to use during filtering.
    
    Methods
    -------
    configure
        Configures the object from an dictionary loaded from a configuration 
        file.
    serialize
        Returns a `dict` with all configurable attributes stored that can
        be used to reconfigure a new instance.
    is_coding
        Return ``True`` if the variants are protein-coding, else ``False``.
    has_wt_sequence
        Returns ``True``
    align_variant
        Align a variant sequence to the wild type sequence
    count_variant
        Count the number of times a specific variant occurs.
    count_synonymous
        Count the number of synonymous variants.
    report_filtered_variant
        Report a variant that was filtered to the log.
    
    See Also
    --------
    :py:class:`~enrich2.libraries.seqlib.SeqLib`
    :py:class:`~enrich2.libraries.basic.BasicSeqLib`
    :py:class:`~enrich2.libraries.barcodevariant.BcvSeqLib`
    
    """

    def __init__(self):
        SeqLib.__init__(self)
        self.wt = WildTypeSequence(self.name)
        self.aligner = None
        self.aligner_cache = None
        self.variant_min_count = 0
        self.max_mutations = None

        # 'synonymous' label may be added in configure() if wt is coding
        self.add_label("variants")

    def configure(self, cfg):
        """
        Set up the object using the config object *cfg*, usually derived from
        a ``.json`` file.
        
        Parameters
        ----------
        cfg : `dict` or :py:class:`~enrich2.config.types.BaseVariantSeqLibConfiguration`
            The object to configure this instance with.
            
        """
        from ..config.types import BaseVariantSeqLibConfiguration

        if isinstance(cfg, dict):
            init_fastq = bool(cfg.get("fastq", {}).get("reads", ""))
            cfg = BaseVariantSeqLibConfiguration(cfg, init_fastq)
        elif not isinstance(cfg, BaseVariantSeqLibConfiguration):
            raise TypeError(
                "`cfg` was neither a " "BaseVariantSeqLibConfiguration or dict."
            )

        SeqLib.configure(self, cfg)
        self.wt.configure(cfg.variants_cfg.wildtype_cfg)

        if self.is_coding():
            self.add_label("synonymous")

        self.variant_min_count = cfg.variants_cfg.min_count
        self.max_mutations = cfg.variants_cfg.max_mutations
        if cfg.variants_cfg.use_aligner:
            self.aligner = Aligner()
            self.aligner_cache = dict()
        else:
            self.aligner = None
            self.aligner_cache = None

    def serialize(self):
        """
        Format this object (and its children) as a config object suitable for
        dumping to a config file.
        
        Returns
        -------
        `dict`
            Attributes of this instance and that of inherited classes
            in a dictionary.
        """
        cfg = SeqLib.serialize(self)

        cfg["variants"] = dict()
        cfg["variants"]["wild type"] = self.wt.serialize()
        cfg["variants"]["use aligner"] = self.aligner is not None
        if self.max_mutations != DEFAULT_MAX_MUTATIONS:
            cfg["variants"]["max mutations"] = self.max_mutations
        if self.variant_min_count > 0:
            cfg["variants"]["min count"] = self.variant_min_count

        return cfg

    def is_coding(self):
        """
        Return ``True`` if the variants are protein-coding, else ``False``.
        
        Returns
        -------
        `bool`
        """
        return self.wt.is_coding()

    def has_wt_sequence(self):
        """
        Returns ``True``, because 
        :py:class:`~enrich2.libraries.variant.VariantSeqLib` objects have a 
        wild type sequence. Raises a ValueError if the wild type
        sequence is not set properly.
        
        Returns
        -------
        `bool`
        """
        if self.wt is not None:
            return True
        else:
            raise ValueError("Wild type not set properly [{}]".format(self.name))

    def align_variant(self, variant_dna):
        """
        Use the local :py:class:`~enrich2.sequence.aligner.Aligner` instance 
        to align the *variant_dna* to the wild type sequence. Returns a list 
        of HGVS_ variant strings.

        Aligned variants are stored in a local dictionary to avoid recomputing
        alignments. This dictionary should be cleared after all variants are
        counted, to save memory.
        
        Parameters
        ----------
        variant_dna : `str`
            DNA sequence to align to reference.
            
        Returns
        -------
        `list`
            Returns a list of HGVS_ variant strings.
        
        Warnings
        --------
        .. warning:: Using the :py:class:`~enrich2.sequence.aligner.Aligner` 
        dramatically increases runtime.
        """
        if variant_dna in list(self.aligner_cache.keys()):
            return self.aligner_cache[variant_dna]

        mutations = list()
        traceback = self.aligner.align(self.wt.dna_seq, variant_dna)
        for x, y, cat, length in traceback:
            if cat == "match":
                continue
            elif cat == "mismatch":
                mut = "{pre}>{post}".format(pre=self.wt.dna_seq[x], post=variant_dna[y])
            elif cat == "insertion":
                if y > length:
                    dup = variant_dna[y : y + length]
                    if dup == variant_dna[y - length : y]:
                        mut = "dup{seq}".format(seq=dup)
                    else:
                        mut = "_{pos}ins{seq}".format(pos=x + 2, seq=dup)
                else:
                    mut = "_{pos}ins{seq}".format(
                        pos=x + 2, seq=variant_dna[y : y + length]
                    )
            elif cat == "deletion":
                mut = "_{pos}del".format(pos=x + length)
            mutations.append((x, mut))

        self.aligner_cache[variant_dna] = mutations
        return mutations

    def count_variant(self, variant_dna, include_indels=True):
        """
        Identifies mutations and counts the *variant_dna* sequence.
        The algorithm attempts to call variants by comparing base-by-base.
        If the *variant_dna* and wild type DNA are different lengths, or if
        there are an excess of mismatches (indicating a possible indel), local
        alignment is performed using :py:meth:`align_variant` if this option
        has been selected in the configuration.

        Each variant is stored as a tab-delimited string of mutations in HGVS_
        format. Returns a list of HGVS_ variant strings. Returns an empty list
        if the variant is wild type. Returns None if the variant was discarded
        due to excess mismatches.
        
        Parameters
        ----------
        variant_dna : `str`
            DNA sequence to align to reference.
        include_indels : `bool`, default: ``True``
            Include indels in the counts.
            
        Returns
        -------
        `list`
            Returns an empty list if the variant is wild type. Returns None 
            if the variant was discarded due to excess mismatches.
        """
        if not re.match("^[ACGTNXacgtnx]+$", variant_dna):
            raise ValueError(
                "Variant DNA sequence contains unexpected "
                "characters [{}]".format(self.name)
            )

        variant_dna = variant_dna.upper()

        if len(variant_dna) != len(self.wt.dna_seq):
            if self.aligner is not None:
                mutations = self.align_variant(variant_dna)
            else:
                return None
        else:
            mutations = list()
            for i in range(len(variant_dna)):
                if variant_dna[i] != self.wt.dna_seq[i]:
                    mutations.append(
                        (
                            i,
                            "{pre}>{post}".format(
                                pre=self.wt.dna_seq[i], post=variant_dna[i]
                            ),
                        )
                    )
                    if len(mutations) > self.max_mutations:
                        if self.aligner is not None:
                            mutations = self.align_variant(variant_dna)
                            if len(mutations) > self.max_mutations:
                                # too many mutations post-alignment
                                return None
                            else:
                                # stop looping over this variant
                                break
                        else:
                            # too many mutations and not using aligner
                            return None

        mutation_strings = list()
        if self.is_coding():
            variant_protein = ""
            for i in range(0, len(variant_dna), 3):
                try:
                    variant_protein += CODON_TABLE[variant_dna[i : i + 3]]
                except KeyError:  # garbage codon due to indel, X, or N
                    variant_protein += "?"

            for pos, change in mutations:
                ref_dna_pos = pos + self.wt.dna_offset + 1
                ref_pro_pos = pos // 3 + self.wt.protein_offset + 1
                mut = "c.{pos}{change}".format(pos=ref_dna_pos, change=change)
                if has_indel(change):
                    mut += " (p.{pre}{pos}fs)".format(
                        pre=AA_CODES[self.wt.protein_seq[pos // 3]], pos=ref_pro_pos
                    )
                elif variant_protein[pos // 3] == self.wt.protein_seq[pos // 3]:
                    mut += " (p.=)"
                else:
                    mut += " (p.{pre}{pos}{post})".format(
                        pre=AA_CODES[self.wt.protein_seq[pos // 3]],
                        pos=ref_pro_pos,
                        post=AA_CODES[variant_protein[pos // 3]],
                    )
                mutation_strings.append(mut)
        else:
            for pos, change in mutations:
                ref_dna_pos = pos + self.wt.dna_offset + 1
                mut = "n.{pos}{change}".format(pos=ref_dna_pos, change=change)
                mutation_strings.append(mut)

        if len(mutation_strings) > 0:
            variant_string = ", ".join(mutation_strings)
        else:
            variant_string = WILD_TYPE_VARIANT
        return variant_string

    def count_synonymous(self):
        """
        Combine counts for synonymous variants (defined as variants that differ
        at the nucleotide level but not at the amino acid level) and store them 
        under the ``synonymous`` label.

        This method should be called only after ``variants`` have been counted.
        
        Notes
        -----
        .. note:: The total number of ``synonymous`` variants may be greater \
        than the total number of ``variants`` after filtering. This is \
        because ``variants`` are combined into ``synonymous`` entries at the \
        :py:class:`~enrich2.libraries.seqlib.SeqLib` level before count-based 
        filtering, allowing filtered ``variants`` to contribute counts to 
        their ``synonymous`` entry.
        """
        if not self.is_coding():
            log_message(
                logging_callback=logging.warning,
                msg="Cannot count synonymous mutations in noncoding data",
                extra={"oname": self.name},
            )
            return

        if self.check_store("/main/synonymous/counts"):
            return

        log_message(
            logging_callback=logging.info,
            msg="Counting synonymous variants",
            extra={"oname": self.name},
        )
        df_dict = dict()

        for variant, count in self.store["/main/variants/counts"].iterrows():
            if variant == WILD_TYPE_VARIANT:
                df_dict[variant] = count["count"]
            else:
                variant = protein_variant(variant)
                if len(variant) == 0:
                    variant = SYNONYMOUS_VARIANT
                try:
                    df_dict[variant] += count["count"]
                except KeyError:
                    df_dict[variant] = count["count"]

        self.save_counts("synonymous", df_dict, raw=False)
        del df_dict

    def report_filtered_variant(self, variant, count):
        """
        Outputs a summary of the filtered variant to *handle*. Internal filter
        names are converted to messages using the ``SeqLib.filter_messages``
        dictionary. Related to :py:meth:`SeqLib.report_filtered`.
        
        Parameters 
        ----------
        variant : :py:class:`~enrich2.sequence.fqread.FQRead`
            The ``FQRead`` object that represents the variant.
        count : `int`
            Count of the variant.
        """
        log_message(
            logging_callback=logging.debug,
            msg="Filtered variant (quantity={n}) (excess mutations)"
            "\n{read!s}".format(n=count, read=variant),
            extra={"oname": self.name},
        )
