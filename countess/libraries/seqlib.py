"""
Enrich2 libraries seqlib module
===============================

Contains the abstract class ``SeqLib`` common to all sequencing library
classes used in ``Enrich2``.
"""


import logging
import os.path
import sys
from collections import OrderedDict
import numpy as np
import pandas as pd

from ..base.storemanager import StoreManager
from ..base.utils import fix_filename, compute_md5, log_message
from ..base.constants import ELEMENT_LABELS
from countess.store.hdf import HdfStore


__all__ = ["SeqLib"]


class SeqLib(StoreManager):
    """
    Abstract class for handling count data from a single se  quencing library.
    
    Class Attributes
    ----------------
    filter_messages : `OrderedDict`
        Mapping of ``json`` fastq configuration filter keys to dataframe
        keys used to create a more readable output.
    store_suffix : `str`
        Default suffix for the base class
        :py:class:`~enrich2.base.storemanager.StoreManager` `name` attribute.
        
    Attributes
    ----------
    timepoint :  int
        The point in time the sequencing library came from. Typically 
        configured via a config file.
    counts_file : str
        File path pointing to a valid counts file.
    _filters : `dict`
        Configured FASTQ filters used during read parsing.
    filter_stats : `dict`
        Statistics regarding outcome of reads filtering.
    default_filters : `dict`
        The default FASTQ filters.
    
    Methods
    -------
    filters
        Getter/Setter property for FASTQ filters.
    serialize_filters
        Returns FASTQ filters in a `dict`.
    _children 
        Overrides :py:class:`~enrich2.base.storemanager.StoreManager` method 
        and returns None, since a seqlib cannot have children.
    add_children
        Cannot add children. Will raise an `AttributeError`.
    remove_child_id
        Cannot remove children. Will raise an `AttributeError`.
    has_wt_sequence
        Base method to be overriden by inheriting classes. Returns False.
    configure
        Configures the object from an dictionary loaded from a configuration 
        file.
    serialize
        Returns a `dict` with all configurable attributes stored that can
        be used to reconfigure a new instance.
    validate
        Validates the attributes of this instance.
    
    report_filtered_read
        Writes a filtered read and it's associated stats to the log.
    save_counts
         Convert count data in a `dict` into a :py:class:`pandas.DataFrame`
    save_filtered_counts
        Filter the counts in ``"/raw/label/counts"`` using the *query* string
        and store the result in ``"/main/label/counts"``
    report_filter_stats
        Create report file for the number of filtered reads.
    save_filter_stats
        Save a DataFrame containing the number of filtered reads under
        ``'/raw/filter'``.
    read_quality_filter
        Check the quality of the FQRead object *fq*.
    write_tsv
        Write each table from the store to its own tab-separated file.
    counts_from_file_h5
        If an HDF store containing raw counts has been specified, open the
        store, copy those counts into this store, and close the counts store
    counts_from_file_tsv
        If a counts file in tsv format has been specified, read the counts 
        into a new dataframe and save as raw counts
    counts_from_file
        Get raw counts from a counts file instead of FASTQ_ file
    
    See Also
    --------
    :py:class:`~enrich2.base.storemanager.StoreManager`
    :py:class:`~.barcode.BarcodeSeqLib`
    :py:class:`~.idonly.IdOnlySeqLib`
    :py:class`~.variant.VariantSeqLib`
    
    """

    # Note: the following block is referenced by line number above
    # When adding new messages, update the documentation line numbers also!
    filter_messages = OrderedDict(
        [
            ("min quality", "single-base quality"),
            ("avg quality", "average quality"),
            ("max N", "excess N bases"),
            ("chastity", "not chaste"),
            ("remove unresolvable", "unresolvable mismatch"),
            ("merge failure", "unable to merge reads"),
            ("total", "total"),
        ]
    )

    store_suffix = "lib"

    def __init__(self):
        StoreManager.__init__(self)
        self.timepoint = None
        self.counts_file = None
        self.report_filtered = None
        self._filters = dict()
        self.filter_stats = dict()
        self.default_filters = dict()
        self.default_filters.update({"min quality": 0})
        self.default_filters.update({"max N": sys.maxsize})
        self.default_filters.update({"avg quality": 0})
        self.default_filters.update({"chastity": False})

    # ---------------------------------------------------------------------- #
    #                           Tree Operations
    # ---------------------------------------------------------------------- #
    def _children(self):
        """
        These objects have no children.
        
        Returns
        -------
        None
        """
        return None

    def add_child(self, child):
        """
        No children, raises an AttributeError.
        """
        raise AttributeError("SeqLib objects do not support adding children")

    def remove_child_id(self, tree_id):
        """
        No children, raises an AttributeError.
        """
        raise AttributeError("SeqLib objects do not support removing children")

    # ---------------------------------------------------------------------- #
    #                     Configuration/Validation
    # ---------------------------------------------------------------------- #
    def validate(self):
        """
        Validates paramaters for a configured SeqLib. Currently does nothing.
        """
        pass

    def has_wt_sequence(self):
        """
        Returns whether or not the object has a wild type sequence. Returns
        ``False`` unless overloaded by a derived class (such as
        :py:class:`~.variant.VariantSeqLib`).
        
        Returns
        -------
        bool
            Returns ``False``
        """
        return False

    def configure(self, cfg):
        """
        Set up the object using the config object *cfg*, usually derived from
        a ``.json`` file.
        
        Parameters
        ----------
        cfg : `dict` or :py:class:`~enrich2.config.types.BaseLibraryConfiguration`
            The object to configure this instance with.
            
        """
        from ..config.types import BaseLibraryConfiguration

        if isinstance(cfg, dict):
            init_fastq = bool(cfg.get("fastq", {}).get("reads", ""))
            cfg = BaseLibraryConfiguration(cfg, init_fastq)
        elif not isinstance(cfg, BaseLibraryConfiguration):
            raise TypeError("`cfg` was neither a " "BaseLibraryConfiguration or dict.")

        StoreManager.configure(self, cfg.store_cfg)
        self.timepoint = cfg.timepoint
        self.report_filtered = cfg.report_filtered_reads
        self.counts_file = cfg.counts_file

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
        cfg = StoreManager.serialize(self)
        cfg["timepoint"] = self.timepoint
        cfg["report filtered reads"] = self.report_filtered
        if self.counts_file is not None:
            cfg["counts file"] = self.counts_file
            cfg["counts file md5"] = compute_md5(self.counts_file)
        return cfg

    def calculate(self):
        """
        Pure virtual method that defines how the data are counted.
        """
        raise NotImplementedError("must be implemented by subclass")

    # ---------------------------------------------------------------------- #
    #                       Counts/Filter Functions
    # ---------------------------------------------------------------------- #
    def report_filtered_read(self, fq, filter_flags):
        """
        Write the :py:class:`~enrich2.sequence.fqread.FQRead` object *fq* to 
        the ``DEBUG`` logging . The dictionary *filter_flags* contains ``True``
        values for each filtering option that applies to *fq*. Keys in
        *filter_flags* are converted to messages using the
        ``StoreManager.filter_messages`` dictionary.
        
        Parameters
        ----------
        fq : :py:class:`~enrich2.sequence.fqread.FQRead`
            The ``FQRead`` object that was filtered.
        filter_flags : `dict`
            Dictionary of flags that applying to *fq*.

        """
        messages = ", ".join(
            StoreManager.filter_messages[x] for x in filter_flags if filter_flags[x]
        )
        log_message(
            logging_callback=logging.debug,
            msg="Filtered read ({messages})\n{read!s}".format(
                messages=messages, name=self.name, read=fq
            ),
            extra={"oname": self.name},
        )

    def save_counts(self, label, df_dict, raw):
        """
        Convert the counts in the dictionary *df_dict* into a DataFrame object
        and save it to the data store.

        If *raw* is ``True``, the counts are stored under
        ``"/raw/label/counts"``; else ``"/main/label/counts"``.
        
        Parameters
        ----------
        label : `str`
            The table's group label to save counts to.
        df_dict : `dict`
            The count data to store, with an index containing 
            variant/barcode/identifier/synonymous entries.
        raw : `bool`
            Set to ``True`` to store under the root group ``'raw'``.
        
        """
        if len(list(df_dict.keys())) == 0:
            raise ValueError("Failed to count {} [{}]".format(label, self.name))
        df = pd.DataFrame.from_dict(df_dict, orient="index", dtype=np.int32)
        df.columns = ["count"]
        df.sort_values("count", ascending=False, inplace=True)
        log_message(
            logging_callback=logging.info,
            msg="Counted {n} {label} ({u} unique)".format(
                n=df["count"].sum(), u=len(df.index), label=label
            ),
            extra={"oname": self.name},
        )
        if raw:
            key = "/raw/{}/counts".format(label)
        else:
            key = "/main/{}/counts".format(label)
        self.store.put(key, df, data_columns=df.columns)
        del df

    def save_filtered_counts(self, label, query):
        """
        Filter the counts in ``"/raw/label/counts"`` using the *query* string
        and store the result in ``"/main/label/counts"``
        
        Parameters
        ----------
        label : `str`
            The table's group label to save counts to.
        query : `str`
            Query string used by ``StoreManager.map_table``.
        
        See Also
        --------
        For more information on building query strings, see
        http://pandas.pydata.org/pandas-docs/stable/io.html#querying-a-table
        
        """
        log_message(
            logging_callback=logging.info,
            msg="Converting raw {} counts to main counts".format(label),
            extra={"oname": self.name},
        )

        raw_table = "/raw/{}/counts".format(label)
        main_table = "/main/{}/counts".format(label)

        self.map_table(source=raw_table, destination=main_table, source_query=query)

        msg = "Counted {n} {label} ({u} unique) after query".format(
            n=self.store[main_table]["count"].sum(),
            u=len(self.store[main_table].index),
            label=label,
        )
        log_message(logging_callback=logging.info, msg=msg, extra={"oname": self.name})

    def report_filter_stats(self):
        """
        Create report file for the number of filtered reads.

        The report file is located in the output directory, named
        ``SeqLibName.filter.txt``. It contains the number of reads filtered 
        for each category, plus the total number filtered.

        Notes
        -----
        .. note:: Reads are checked for all quality-based criteria before
        filtering.
        
        """
        path = os.path.join(self.output_dir, fix_filename(self.name) + ".filter.txt")
        with open(path, "wt") as handle:
            elements = list()
            for key in sorted(
                self.filter_stats, key=self.filter_stats.__getitem__, reverse=True
            ):
                if key != "total" and self.filter_stats[key] > 0:
                    print(
                        SeqLib.filter_messages[key],
                        self.filter_stats[key],
                        sep="\t",
                        file=handle,
                    )
            print("total", self.filter_stats["total"], sep="\t", file=handle)
        log_message(
            logging_callback=logging.info,
            msg="Wrote filtering statistics",
            extra={"oname": self.name},
        )

    def save_filter_stats(self):
        """
        Save a DataFrame containing the number of filtered reads under
        ``'/raw/filter'``.

        This DataFrame contains the same information as ``report_filter_stats``
        """
        df = pd.DataFrame(
            index=list(SeqLib.filter_messages.values()), columns=["count"]
        )
        for key in list(self.filter_stats.keys()):
            if self.filter_stats[key] > 0 or key == "total":
                df.loc[SeqLib.filter_messages[key], "count"] = self.filter_stats[key]
        df.dropna(inplace=True)
        if self.override_filter_stats:
            self.store.put("/raw/filter", df.astype(int), data_columns=df.columns)
        else:
            log_message(
                logging.info,
                msg="Keeping old filter stats from previous store file.",
                extra={"oname": self.name},
            )

    def read_quality_filter(self, fq):
        """
        Check the quality of the FQRead object *fq*.

        Checks ``'chastity'``, ``'min quality'``, ``'avg quality'``,
        ``'max N'``, and ``'remove unresolvable'``. Counts failed reads for 
        later output and reports the filtered read if desired.
        
        Parameters
        ----------
        fq : :py:class:`~enrich2.sequence.fqread.FQRead`
            The read object to check.
        
        Returns
        -------
        `bool`
            Returns ``True`` if the read passes all filters, else ``False``.
        """
        filter_flags = dict()
        for key in self.filters:
            filter_flags[key] = False

        if self.filters["chastity"]:
            if not fq.is_chaste():
                self.filter_stats["chastity"] += 1
                filter_flags["chastity"] = True

        if self.filters["min quality"] > 0:
            if fq.min_quality() < self.filters["min quality"]:
                self.filter_stats["min quality"] += 1
                filter_flags["min quality"] = True

        if self.filters["avg quality"] > 0:
            if fq.mean_quality() < self.filters["avg quality"]:
                self.filter_stats["avg quality"] += 1
                filter_flags["avg quality"] = True

        if self.filters["max N"] >= 0:
            if fq.sequence.upper().count("N") > self.filters["max N"]:
                self.filter_stats["max N"] += 1
                filter_flags["max N"] = True

        if "remove unresolvable" in self.filters:  # OverlapSeqLib only
            if self.filters["remove unresolvable"]:
                if "X" in fq.sequence:
                    self.filter_stats["remove unresolvable"] += 1
                    filter_flags["remove unresolvable"] = True

        # update total and report if failed
        if any(filter_flags.values()):
            self.filter_stats["total"] += 1
            if self.report_filtered:
                self.report_filtered_read(fq, filter_flags)
            return False
        else:
            return True

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, config_filters):
        """
        Set up the filters dictionary using the options selected in
        *config_filters*, filling in missing entries with defaults.

        Parameters
        ----------
        config_filters : `dict`
            Updates the filters `dict` with values in *config_filters*.

        """
        self._filters.clear()
        self._filters.update(self.default_filters)

        unused = list()
        for key in config_filters:
            if key in self._filters:
                if config_filters[key] is not None:
                    self._filters[key] = config_filters[key]
            else:
                unused.append(key)
        if len(unused) > 0:
            log_message(
                logging_callback=logging.warning,
                msg="Unused filter parameters ({})".format(", ".join(unused)),
                extra={"oname": self.name},
            )

        self.filter_stats.clear()
        for key in self._filters:
            self.filter_stats[key] = 0
        self.filter_stats["total"] = 0

    def serialize_filters(self):
        """
        Serialize this object's FASTQ_ file handling and filtering options.
        
        Returns
        -------
        `dict`
            Return a `dict` of filtering options that have non-default values.
        """
        cfg = dict()
        for key in self.filters.keys():
            if self.filters[key] != self.default_filters[key]:
                cfg[key] = self.filters[key]
        return cfg

    # ---------------------------------------------------------------------- #
    #                           File I/O
    # ---------------------------------------------------------------------- #
    def write_tsv(self, **kwargs):
        """
        Write each table from the store to its own tab-separated file.

        Files are written to a ``tsv`` directory in the default output
        location. File names are the HDF5 key with ``'_'`` substituted 
        for ``'/'``.

        Parameters
        ----------
        **kwargs : 
        """
        if self.tsv_requested:
            log_message(
                logging_callback=logging.info,
                msg="Generating tab-separated output files",
                extra={"oname": self.name},
            )
            for k in list(self.store.keys()):
                self.write_table_tsv(k)

    def counts_from_file_h5(self, fname):
        """
        If an HDF store containing raw counts has been specified, open the
        store, copy those counts into this store, and close the counts store.

        Copies all tables in the ``'/raw'`` group along with their metadata.
        
        Parameters
        ----------
        fname : `str`
            The file name of the H5 store to load.
        """
        store = HdfStore(fname)
        log_message(
            logging_callback=logging.info,
            msg="Using existing HDF5 data store '{}' for raw data".format(fname),
            extra={"oname": self.name},
        )
        # this could probably be much more efficient, but the PyTables docs
        # don't explain copying subsets of files adequately
        raw_keys = [key for key in store.keys() if key.startswith("/raw/")]
        if len(raw_keys) == 0:
            raise ValueError(
                "No raw counts found in '{}' [{}]".format(fname, self.name)
            )
        else:
            for k in raw_keys:
                # Copy the data table
                raw = store[k]
                self.store.put(k, raw, data_columns=raw.columns)
                # copy the metadata
                self.set_metadata(k, self.get_metadata(k, store=store), update=False)

                # Copy the metadata
                log_message(
                    logging_callback=logging.info,
                    msg="Copied raw data '{}'".format(k),
                    extra={"oname": self.name},
                )
        store.close()

    def counts_from_file_tsv(self, fname):
        """
        If a counts file in tsv format has been specified, read the counts into
        a new dataframe and save as raw counts.
        
        Parameters
        ----------
        fname : `str`
            The file name of the H5 store to save to.
        """
        df = pd.read_table(fname, sep="\t", header=0, index_col=0)
        if df.columns != ["count"]:
            raise ValueError(
                "Invalid column names for counts file [{}]" "".format(self.name)
            )
        if len(df) == 0:
            raise ValueError("Empty counts file [{}]".format(self.name))
        label = None
        for elem in ELEMENT_LABELS:
            if elem in self.labels:
                label = elem
                break
        if label is None:
            raise ValueError("No valid element labels [{}]".format(self.name))
        key = "/raw/{}/counts".format(label)
        self.store.put(key, df.astype(np.int32), data_columns=df.columns)

    def counts_from_file(self, fname):
        """
        Get raw counts from a counts file instead of FASTQ_ file.

        The ``'/raw/<element>/counts'`` table will be populated using the given
        input file. The input file should be a two-column file readable by
        ``pandas`` as a series or two-column dataframe or an Enrich2 HDF5 file.

        If the input file is a two-column file, the index will be checked using
        the SeqLib's ``validate_index()`` method.

        If the input file is an HDF5 file, the entire set of ``'/raw'`` tables
        will be copied over, with the metadata intact.
        
        Parameters
        ----------
        fname : `str`
            The file name to read from.
        """
        if not os.path.exists(fname):
            raise IOError("Counts file '{}' not found [{}]" "".format(fname, self.name))
        elif os.path.splitext(fname)[-1].lower() in [".h5"]:
            self.counts_from_file_h5(self.counts_file)
        elif os.path.splitext(fname)[-1].lower() in (".txt", ".tsv", ".csv"):
            self.counts_from_file_tsv(self.counts_file)
        else:
            raise ValueError(
                "Unrecognized counts file extension for '{}' "
                "[{}]".format(fname, self.name)
            )
