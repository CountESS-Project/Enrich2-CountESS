"""
Enrich2 libraries basic module
==============================

Contains the concrete class ``BasicSeqLib`` which represents a sequencing
library with variants that must be aligned to wild type sequence.
"""


import sys
import logging

from ..sequence.fqread import read_fastq
from .variant import VariantSeqLib
from ..base.utils import compute_md5, log_message


__all__ = ["BasicSeqLib"]


class BasicSeqLib(VariantSeqLib):
    """
    Class for count data from sequencing libraries with a single read for
    each variant. Creating a :py:class:`~enrich2.libraries.basic.BasicSeqLib` 
    requires a valid *config* object, usually from a ``.json`` configuration 
    file.
    
    Class Attributes
    ----------------
    treeview_class_name :  `str`
        String used to render object in the GUI.
    
    Attributes
    ----------
    reads : `str`
        File path of reads file to parse.
    revcomp_reads : `bool`
        ``True`` to reverse complement reads.
    trim_start : `int`
        Position to start the read trim from.
    trim_length : `int`
        Number of bases to keep starting from `trim_start`
    
    Methods
    -------
    configure
        Configures the object from an dictionary loaded from a configuration 
        file.
    serialize
        Returns a `dict` with all configurable attributes stored that can
        be used to reconfigure a new instance.
    configure_fastq
        Configures the fastq options following the `configure` method
    serialize_fastq
        Returns a `dict` with all configurable fastq options and their
        settings for this instance.
    calculate
        Counts variants from counts file or FASTQ.
    
    See Also
    --------
    :py:class:`~enrich2.libraries.variant.VariantSeqLib`
    """

    treeview_class_name = "Basic SeqLib"

    def __init__(self):
        VariantSeqLib.__init__(self)
        self.reads = None
        self.revcomp_reads = None
        self.trim_start = 0
        self.trim_length = sys.maxsize

    def configure(self, cfg):
        """
        Set up the object using the config object *cfg*, usually derived from
        a ``.json`` file.

        Parameters
        ----------
        cfg : `dict` or :py:class:`~enrich2.config.types.BasicSeqLibConfiguration`
            The object to configure this instance with.
        """
        from ..config.types import BasicSeqLibConfiguration

        if isinstance(cfg, dict):
            init_fastq = bool(cfg.get("fastq", {}).get("reads", ""))
            cfg = BasicSeqLibConfiguration(cfg, init_fastq)
        elif not isinstance(cfg, BasicSeqLibConfiguration):
            raise TypeError("`cfg` was neither a " "BcidSeqLibConfiguration or dict.")

        VariantSeqLib.configure(self, cfg)

        # if counts are specified, copy them later
        # else handle the FASTQ config options and check the files
        if self.counts_file is None:
            self.configure_fastq(cfg.fastq_cfg)

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
        cfg = VariantSeqLib.serialize(self)
        cfg["fastq"] = self.serialize_fastq()
        return cfg

    def configure_fastq(self, cfg):
        """
        Set up the object's FASTQ_ file handling and filtering options.
        
        Parameters
        ----------
        cfg : :py:class:`~enrich2.config.types.FASTQConfiguration`
            Configures the fastq options of this instance.
        """
        self.reads = cfg.reads
        self.revcomp_reads = cfg.reverse
        self.trim_start = cfg.trim_start
        self.trim_length = cfg.trim_length
        self.filters = cfg.filters_cfg.to_dict()

    def serialize_fastq(self):
        """
        Serialize this object's FASTQ_ file handling and filtering options.

        Returns
        -------
        `dict`
            Return a `dict` of filtering options that have non-default values.
        """
        fastq = dict(filters=self.serialize_filters())
        fastq["reads"] = self.reads
        fastq["read md5"] = compute_md5(self.reads)

        if self.revcomp_reads:
            fastq["reverse"] = True
        else:
            fastq["reverse"] = False

        if self.trim_start > 1:
            fastq["start"] = self.trim_start

        if self.trim_length < sys.maxsize:
            fastq["length"] = self.trim_length

        return fastq

    def counts_from_reads(self):
        """
        Reads the forward or reverse FASTQ_ file (reverse reads are
        reverse-complemented), performs quality-based filtering, and counts
        the variants.
        """
        df_dict = dict()
        log_message(
            logging_callback=logging.info,
            msg="Counting variants",
            extra={"oname": self.name},
        )

        max_mut_variants = 0
        for fq in read_fastq(self.reads):
            fq.trim_length(self.trim_length, start=self.trim_start)
            if self.revcomp_reads:
                fq.revcomp()

            if self.read_quality_filter(fq):
                mutations = self.count_variant(fq.sequence)
                if mutations is None:  # too many mutations
                    max_mut_variants += 1
                    if self.report_filtered:
                        self.report_filtered_variant(fq.sequence, 1)
                else:
                    try:
                        df_dict[mutations] += 1
                    except KeyError:
                        df_dict[mutations] = 1

        self.save_counts("variants", df_dict, raw=True)
        del df_dict

        if self.aligner is not None:
            log_message(
                logging_callback=logging.info,
                msg="Aligned {} variants".format(self.aligner.calls),
                extra={"oname": self.name},
            )
            self.aligner_cache = None

        log_message(
            logging_callback=logging.info,
            msg="Removed {} total variants with excess "
            "mutations".format(max_mut_variants),
            extra={"oname": self.name},
        )
        self.save_filter_stats()

    def calculate(self):
        """
        Counts variants from counts file or FASTQ.
        """
        if not self.check_store("/main/variants/counts"):
            if not self.check_store("/raw/variants/counts"):
                if self.counts_file is not None:
                    self.counts_from_file(self.counts_file)
                else:
                    self.counts_from_reads()
            self.save_filtered_counts(
                "variants", "count >= {}".format(self.variant_min_count)
            )
        self.count_synonymous()
