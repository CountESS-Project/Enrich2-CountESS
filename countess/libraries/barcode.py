"""
Enrich2 libraries barcode module
================================

Contains the concrete class ``BarcodeSeqLib`` which represents a sequencing
library which only contains barcoded sequences.
"""


import logging
import sys

from ..sequence.fqread import read_fastq
from .seqlib import SeqLib
from ..base.utils import compute_md5, log_message


__all__ = ["BarcodeSeqLib"]


class BarcodeSeqLib(SeqLib):
    """
    Class for count data from barcoded sequencing libraries. Designed for
    barcode-only scoring or as a parent class for
    :py:class:`~enrich2.libraries.barcodevariant.BcvSeqLib` and
    :py:class:`~enrich2.libraries.barcodeid.BcidSeqLib`.
    
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
    barcode_min_count : `int`
        Minimum count a barcode must have to pass the filtering phase.
    
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
    counts_from_reads
        Reads the forward or reverse FASTQ_ file (reverse reads are
        reverse-complemented), performs quality-based filtering, and counts
        the barcodes.
        
    See Also
    --------
    :py:class:`~enrich2.libraries.seqlib.SeqLib`
    """

    treeview_class_name = "Barcode SeqLib"

    def __init__(self):
        # Init step handled by VariantSeqLib's init for Barcode-variant
        if type(self).__name__ != "BcvSeqLib":
            SeqLib.__init__(self)
        self.reads = None
        self.revcomp_reads = None
        self.trim_start = None
        self.trim_length = None
        self.barcode_min_count = 0
        self.add_label("barcodes")

    def configure(self, cfg):
        """
        Set up the object using the config object *cfg*, usually derived from
        a ``.json`` file.

        Parameters
        ----------
        cfg : `dict` or :py:class:`~enrich2.config.types.BcidSeqLibConfiguration`
            The object to configure this instance with.
        """
        from ..config.types import BarcodeSeqLibConfiguration

        if isinstance(cfg, dict):
            init_fastq = bool(cfg.get("fastq", {}).get("reads", ""))
            cfg = BarcodeSeqLibConfiguration(cfg, init_fastq)
        elif not isinstance(cfg, BarcodeSeqLibConfiguration):
            raise TypeError(
                "`cfg` was neither a " "BarcodeSeqLibConfiguration or dict."
            )

        SeqLib.configure(self, cfg)
        self.barcode_min_count = cfg.barcodes_cfg.min_count

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
        cfg = SeqLib.serialize(self)
        cfg["barcodes"] = dict()
        if self.barcode_min_count > 0:
            cfg["barcodes"]["min count"] = self.barcode_min_count
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
        fastq = {
            "reads": self.reads,
            "reverse": self.revcomp_reads,
            "filters": self.serialize_filters(),
            "reads md5": compute_md5(self.reads),
        }
        if self.trim_start is not None and self.trim_start > 1:
            fastq["start"] = self.trim_start

        if self.trim_length is not None and self.trim_length < sys.maxsize:
            fastq["length"] = self.trim_length

        return fastq

    def counts_from_reads(self):
        """
        Reads the forward or reverse FASTQ_ file (reverse reads are
        reverse-complemented), performs quality-based filtering, and counts
        the barcodes.

        Barcode counts after read-level filtering are stored under
        ``"/raw/barcodes/counts"``.
        """
        df_dict = dict()

        filter_flags = dict()
        for key in self.filters:
            filter_flags[key] = False

        # count all the barcodes
        log_message(
            logging_callback=logging.info,
            msg="Counting Barcodes",
            extra={"oname": self.name},
        )
        for fqr in read_fastq(self.reads):
            fqr.trim_length(self.trim_length, start=self.trim_start)
            if self.revcomp_reads:
                fqr.revcomp()

            if self.read_quality_filter(fqr):  # passed filtering
                try:
                    df_dict[fqr.sequence.upper()] += 1
                except KeyError:
                    df_dict[fqr.sequence.upper()] = 1

        self.save_counts(label="barcodes", df_dict=df_dict, raw=True)
        del df_dict

    def calculate(self):
        """
        Counts the barcodes from the FASTQ file or from the provided counts
        file depending on the config.

        Barcodes that pass the minimum count
        filtering are stored under ``"/main/barcodes/counts"``.

        If ``"/main/barcodes/counts"`` already exists, those will be used
        instead of re-counting.
        """
        if self.check_store("/main/barcodes/counts"):
            return

        # no raw counts present
        if not self.check_store("/raw/barcodes/counts"):
            if self.counts_file is not None:
                self.counts_from_file(self.counts_file)
            else:
                self.counts_from_reads()

        if len(self.labels) == 1:  # only barcodes
            self.save_filtered_counts(
                label="barcodes", query="count >= {}".format(self.barcode_min_count)
            )
            self.save_filter_stats()
