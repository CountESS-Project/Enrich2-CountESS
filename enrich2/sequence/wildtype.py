"""
Enrich2 sequence wildtype module
================================
This module contains the ``WildTypeSequence`` class which represents a
reference sequence.
"""


import logging
import re

from ..base.constants import CODON_TABLE
from ..base.utils import log_message


__all__ = ["WildTypeSequence"]


class WildTypeSequence(object):
    """
    Container class for wild type sequence information. 
    Used by :py:class:`~enrich2.libraries.seqlib.VariantSeqLib` objects and 
    :py:class:`~enrich2.selection.selection.Selection` 
    or :py:class:`~enrich2.experiment.experiment.Experiment` objects 
    that contain variant information.

    Requires a *parent_name* that associates this object with a 
    StoreManager object for the purposes of error reporting and logging.
    
    Parameters
    ----------
    parent_name : `str`
        Associates this object with a StoreManager object for the purposes of 
        error reporting and logging.
    
    Attributes
    ----------
    parent_name : `str`
        Associates this object with a StoreManager object for the purposes of 
        error reporting and logging.
    dna_seq : `str`
        A valid DNA sequence.
    protein_seq : `str`
        If this instance is coding, the protein sequence is a sequence of
        amino acid single letters.
    dna_offset : `int`
        Genomic coordinates within reference are reported relative to this 
        offset
    protein_offset : `int`
        Coordinates within protein reference are reported relative to this 
        offset. Derived from `dna_offset` modulo 3. If this is not a multiple
        of 3, it will be set to 0.
        
    Methods
    -------
    configure
        Configures the object from an dictionary loaded from a configuration 
        file.
    serialize
        Returns a `dict` with all configurable attributes stored that can
        be used to reconfigure a new instance.
    is_coding
        Returns ``True`` if reference is protein coding.
    duplicate
        Create a copy of this object with the *new_parent_name*.
    position_tuples
        Return a list of tuples containing the position number 
        (after offset adjustment) and single-letter symbol 
        (nucleotide or amino acid) for each position the wild type sequence.
    
    See Also
    --------
    :py:class:`~enrich2.libraries.seqlib.VariantSeqLib`
    
    """

    def __init__(self, parent_name):
        self.parent_name = parent_name
        self.dna_seq = None
        self.protein_seq = None
        self.dna_offset = None
        self.protein_offset = None

    def __eq__(self, other):
        # note we don't need to check protein_offset,
        # since it depends on dna_offset and protein_seq
        return (
            self.dna_seq == other.dna_seq
            and self.protein_seq == other.protein_seq
            and self.dna_offset == other.dna_offset
        )

    def __ne__(self, other):
        return not self == other

    def configure(self, cfg):
        """
        Set up the object using the config object *cfg*, usually derived from
        a ``.json`` file.

        Parameters
        ----------
        cfg : :class:`~enrich2.config.types.WildTypeConfiguration` or `dict`
            Either a configuration object or a dictionary to initialise
            a configuration object.
        """
        from ..config.types import WildTypeConfiguration

        if isinstance(cfg, dict):
            cfg = WildTypeConfiguration(cfg)
        elif not isinstance(cfg, WildTypeConfiguration):
            raise TypeError("`cfg` was neither a " "WildTypeConfiguration or dict.")

        self.dna_offset = cfg.reference_offset
        self.dna_seq = cfg.sequence.upper()
        if not re.match("^[ACGT]+$", self.dna_seq):
            raise ValueError(
                "WT DNA sequence contains unexpected "
                "characters [{}]".format(self.parent_name)
            )

        if cfg.coding:
            # require coding sequences are in-frame
            if len(self.dna_seq) % 3 != 0:
                raise ValueError(
                    "WT DNA sequence contains incomplete "
                    "codons [{}]".format(self.parent_name)
                )

            # perform translation
            self.protein_seq = ""
            for i in range(0, len(self.dna_seq), 3):
                self.protein_seq += CODON_TABLE[self.dna_seq[i : i + 3]]

            # set the reference offset if it's a multiple of three
            if self.dna_offset % 3 == 0:
                self.protein_offset = self.dna_offset // 3
            else:
                log_message(
                    logging_callback=logging.warning,
                    msg="Ignoring reference offset for protein "
                    "changes (not a multiple of three)",
                    extra={"oname": self.parent_name},
                )
                self.protein_offset = 0
        else:
            self.protein_seq = None
            self.protein_offset = None

    def serialize(self):
        """
        Format this object as a config object suitable for dumping to a config 
        file.

        Returns
        -------
        `dict`
            Attributes of this instance and that of inherited classes
            in a dictionary.
        """
        cfg = {
            "sequence": self.dna_seq,
            "coding": self.is_coding(),
            "reference offset": self.dna_offset,
        }
        return cfg

    def is_coding(self):
        """
        Returns the coding status of the reference sequence.
        
        Returns
        -------
        `bool`
            ``True`` if protein coding.
        """
        return self.protein_seq is not None

    def duplicate(self, new_parent_name):
        """
        Create a copy of this object with the *new_parent_name*.

        Uses the configure and serialize methods to perform the copy.
        
        Parameters
        ----------
        new_parent_name : `str`
            Associates this object with a StoreManager object for the purposes 
            of error reporting and logging.
            
        Returns
        -------
        :py:class:`~enrich2.sequence.wildtype.WildType`
        """
        new = WildTypeSequence(new_parent_name)
        new.configure(self.serialize())

        if new != self:
            raise ValueError(
                "Failed to duplicate wild type "
                "sequence [{}]".format(self.parent_name)
            )
        else:
            return new

    def position_tuples(self, protein=False):
        """
        Return a list of tuples containing the position number 
        (after offset adjustment) and single-letter symbol 
        (nucleotide or amino acid) for each position the wild type sequence.
        
        Parameters
        ----------
        protein : `bool`
            ``True`` to convert `protein_seq` to position tuples, otherwise
            use `dna_seq`
            
        Returns
        -------
        `list`
            List of (position number, single-letter) tuples
        """
        if protein:
            if not self.is_coding():
                raise AttributeError(
                    "Cannot return wild type protein "
                    "position tuples for non-coding wild "
                    "type [{}]".format(self.parent_name)
                )
            else:
                seq = self.protein_seq
                offset = self.protein_offset
        else:
            seq = self.dna_seq
            offset = self.dna_offset

        return [(i + offset + 1, seq[i]) for i in range(len(seq))]
