"""
Enrich2 selection module
========================

This module contains the class used by ``Enrich2`` to represent a selection
of sequencing libraries, which manages libraries.
"""


import logging
import numpy as np
import pandas as pd
import scipy.stats as stats

from ..base.constants import WILD_TYPE_VARIANT
from ..base.utils import compute_md5, log_message
from ..base.storemanager import StoreManager
from ..base.config_constants import SCORER, SCORER_OPTIONS, SCORER_PATH
from ..base.config_constants import LIBRARIES

from ..libraries.barcode import BarcodeSeqLib
from ..libraries.barcodeid import BcidSeqLib
from ..libraries.barcodevariant import BcvSeqLib
from ..libraries.basic import BasicSeqLib
from ..libraries.idonly import IdOnlySeqLib
from ..libraries.variant import protein_variant

globals()["BasicSeqLib"] = BasicSeqLib
globals()["BarcodeSeqLib"] = BarcodeSeqLib
globals()["BcvSeqLib"] = BcvSeqLib
globals()["BcidSeqLib"] = BcidSeqLib
globals()["IdOnlySeqLib"] = IdOnlySeqLib


__all__ = ["Selection"]


class Selection(StoreManager):
    """
    Class for a single selection replicate, consisting of multiple 
    timepoints. This class coordinates 
    :py:class:`~enrich2.libraries.seqlib.SeqLib` objects.
    
    Attributes
    ----------
    libraries : `dict`
        Dictionary of libraries where the keys are the keys are the 
        library timepoints.
    barcode_maps : `dict`
        Dictionary of :py:class:`~enrich2.libraries.barcodemap.BarcodeMap`
        where the keys are the keys are the library timepoints.
    _wt : :py:class:`~enrich2.sequence.wildtype.WildTypeSequence`
        Wild-type sequence managed by children.
    
    Methods
    -------
    _children 
        Returns all libraries managed by this instance.
    remove_child_id
        Removes the child with the specified ``treeview_id`` 
    timepoints
        Returns all timepoints in this instance.
    wt
        Property returning the wildtype sequence object.
    configure
        Configures the object from an dictionary loaded from a configuration 
        file.
    serialize
        Returns a `dict` with all configurable attributes stored that can
        be used to reconfigure a new instance.
    validate
        Validates the attributes of this instance.
    add_child
        Adds a child to this instance's children.
    is_barcodevariant
        Returns a boolean indicating if all children are barcodevariant libs
    is_barcodeid
        Returns a boolean indicating if all children are barcodeid libs
    is_coding
        Returns a boolean indicating if all children have coding sequences.
    has_wt_sequence
        Returns a boolean indicating if all children have a wt sequence.
    merge_counts_unfiltered
        Counts :py:class:`~enrich2.libraries.seqlib.SeqLib` objects and 
        tabulates counts for each timepoint.
    filter_counts
        Filter unfiltered raw counts by dropping missing counts.
    combine_barcode_maps
        Combine all barcode maps for selections into a single dataframe.
    timepoint_indices_intersect
        Check to see if timepoints share all variants in common for all labels.
    timepoint_indices_intersect_for_label
        For a single label, check to see if timepoints share all variants.
    timepoints_contain_variants
        For each label, check to see if timepoints share all variants in
        common.
    timepoints_contain_variants_for_label
        For a single label, check to see if timepoints share all variants in
        common.
    table_not_empty_for_key
        Checks to see if a table exists in a :py:class:`pd.HDFStore` 
        store and is populated.
    score_index_has_been_modified
        Check to see if the index of a dataframe has been modified when
        going from counts to scores dataframes.
    table_exists_for_key
        Checks to see if a table exists in a :py:class:`pd.HDFStore`
    ensure_main_count_tables_exist_and_populated
        Before the main computations are performed, checks to see if the
        required count tables in main exist and are populated.
    calculate
        Calculate counts and enrichment scores for all labels in this instance.
    write_tsv
        Write each table from the store to its own tab-separated file.
    synonymous_variants
        Populate and return a dictionary mapping synonymous variants to the 
        list of associated variants in ``/main/variants/counts``.
    barcodemap_mapping
        Return a `dict` representation of the ``'/main/barcodemap'`` table.
    calc_outliers
        Computes outlier statistics for elements within each label.
    
    See Also
    --------
    :py:class:`~enrich2.experiment.experiment.Experiment`
    :py:class:`~enrich2.experiment.condition.Condition`
    :py:class:`~enrich2.base.storemanager.StoreManager`
    """

    store_suffix = "sel"
    treeview_class_name = "Selection"

    def __init__(self):
        StoreManager.__init__(self)
        self.libraries = dict()
        self.barcode_maps = dict()
        self._wt = None

    def _children(self):
        """
        Return the :py:class:`~enrich2.libraries.seqlib.SeqLib` objects 
        as a list, sorted by timepoint and then by name.
        """
        libs = list()
        for tp in self.timepoints:
            libs.extend(sorted(self.libraries[tp], key=lambda x: x.name))
        return libs

    def remove_child_id(self, tree_id):
        """
        Remove the reference to a :py:class:`~enrich2.libraries.seqlib.SeqLib` 
        with Treeview id *tree_id*. Deletes empty time points.
        """
        empty = None
        for tp in self.libraries:
            tp_ids = [lib.treeview_id for lib in self.libraries[tp]]
            if tree_id in tp_ids:
                del self.libraries[tp][tp_ids.index(tree_id)]
                if len(self.libraries[tp]) == 0:
                    empty = tp
                break  # found the id, stop looking
        if empty is not None:
            del self.libraries[empty]

    @property
    def timepoints(self):
        return sorted(self.libraries.keys())

    @property
    def wt(self):
        if self.has_wt_sequence():
            if self._wt is None:
                self._wt = self.children[0].wt.duplicate(self.name)
            return self._wt
        else:
            if self._wt is not None:
                raise ValueError(
                    "Selection should not contain wild type "
                    "sequence [{}]".format(self.name)
                )
            else:
                return None

    def configure(self, cfg, configure_children=True, init_from_gui=False):
        """
        Set up the :py:class:`~enrich2.selection.selection.Selection` 
        using the *cfg* object, usually from a ``.json`` configuration file.

        If *configure_children* is false, do not configure the children in 
        *cfg*.
        """
        from ..config.types import SelectionConfiguration

        if isinstance(cfg, dict):
            has_scorer = True
            if init_from_gui:
                has_scorer = False
            cfg = SelectionConfiguration(cfg, has_scorer, init_from_gui)
        elif not isinstance(cfg, SelectionConfiguration):
            raise TypeError("`cfg` was neither a " "SelectionConfiguration or dict.")

        StoreManager.configure(self, cfg.store_cfg)
        if configure_children:
            if len(cfg.lib_cfgs) == 0:
                raise KeyError(
                    "Missing required config value "
                    "{} [{}]".format("libraries", self.name)
                )

            for lib_cfg in cfg.lib_cfgs:
                if lib_cfg.seqlib_type in ("BcvSeqLib", "BcidSeqLib"):
                    lib = globals()[lib_cfg.seqlib_type]()
                    mapfile = lib_cfg.barcodes_cfg.map_file
                    if mapfile in list(self.barcode_maps.keys()):
                        lib.configure(lib_cfg, barcode_map=self.barcode_maps[mapfile])
                    else:
                        lib.configure(lib_cfg)
                        self.barcode_maps[mapfile] = lib.barcode_map
                    self.add_child(lib)
                else:
                    lib = globals()[lib_cfg.seqlib_type]()
                    lib.configure(lib_cfg)
                    self.add_child(lib)

    def validate(self):
        """
        Raises an informative ``ValueError`` if the time points in the
        analysis are not suitable. Calls validate method on all child SeqLibs.
        """
        # check the time points
        scoring_method = self.get_root().scorer_class.name

        if 0 not in self.timepoints:
            raise ValueError("Missing timepoint 0 [{}]".format(self.name))

        if self.timepoints[0] != 0:
            raise ValueError("Invalid negative " "timepoint [{}]".format(self.name))

        if len(self.timepoints) < 2:
            raise ValueError("Multiple timepoints " "required [{}]".format(self.name))

        elif len(self.timepoints) < 3 and "Regression" in scoring_method:
            raise ValueError(
                "Insufficient number of timepoints for "
                "regression scoring [{}]".format(self.name)
            )

        # check the wild type sequences
        if self.has_wt_sequence():
            for child in self.children[1:]:
                if self.children[0].wt != child.wt:
                    log_message(
                        logging_callback=logging.warning,
                        msg="Inconsistent wild type sequences",
                        extra={"oname": self.name},
                    )
                    break

        # check that we're not doing wild type normalization
        # on something with no wild type
        logr_method = self.get_root().scorer_class_attrs.get("logr_method", "")
        if not self.has_wt_sequence() and logr_method == "wt":
            raise ValueError(
                "No wild type sequence for wild "
                "type normalization [{}]".format(self.name)
            )

        # validate children
        for child in self.children:
            child.validate()

    def serialize(self):
        """
        Format this object (and its children) as a config object
        suitable for dumping to a config file.
        """
        cfg = StoreManager.serialize(self)
        cfg[LIBRARIES] = [child.serialize() for child in self.children]
        cfg[SCORER] = {
            SCORER_PATH: self.get_root().scorer_path,
            SCORER_OPTIONS: self.get_root().scorer_class_attrs,
            SCORER_PATH + " md5": compute_md5(self.get_root().scorer_path),
        }
        return cfg

    def add_child(self, child):
        if child.name in self.child_names():
            raise ValueError(
                "Non-unique sequencing library name "
                "'{}' [{}]".format(child.name, self.name)
            )
        child.parent = self
        try:
            self.libraries[child.timepoint].append(child)
        except KeyError:
            self.libraries[child.timepoint] = [child]

    def is_barcodevariant(self):
        """
        Return ``True`` if all :py:class:`~enrich2.libraries.seqlib.SeqLib` 
        in the :py:class:`~enrich2.selection.selection.Selection` are 
        :py:class:`~barcodevariant.BcvSeqLib` objects with 
        the same barcode map, else ``False``.
        """
        return (
            all(isinstance(lib, BcvSeqLib) for lib in self.children)
            and len(list(self.barcode_maps.keys())) == 1
        )

    def is_barcodeid(self):
        """
        Return ``True`` if all :py:class:`~enrich2.libraries.seqlib.SeqLib` 
        in the :py:class:`~enrich2.selection.selection.Selection` are 
        :py:class:`~barcodeid.BcidSeqLib` objects with 
        the same barcode map, else ``False``.
        """
        return (
            all(isinstance(lib, BcidSeqLib) for lib in self.children)
            and len(list(self.barcode_maps.keys())) == 1
        )

    def is_coding(self):
        """
        Return ``True`` if the all :py:class:`~enrich2.libraries.seqlib.SeqLib` 
        in the :py:class:`~enrich2.selection.selection.Selection` 
        count protein-coding variants, else ``False``.
        """
        return all(x.is_coding() for x in self.children)

    def has_wt_sequence(self):
        """
        Return ``True`` if the all :py:class:`~enrich2.libraries.seqlib.SeqLib` 
        in the :py:class:`~enrich2.selection.selection.Selection` have a 
        wild type sequence, else ``False``.
        """
        return all(x.has_wt_sequence() for x in self.children)

    def merge_counts_unfiltered(self, label):
        """
        Counts :py:class:`~enrich2.libraries.seqlib.SeqLib` objects and 
        tabulates counts for each timepoint. 
        :py:class:`~enrich2.libraries.seqlib.SeqLib` objects from 
        the same timepoint are combined by summing the counts.

        Stores the unfiltered counts under ``/main/label/counts_unfiltered``.
        """
        if self.check_store("/main/{}/counts_unfiltered".format(label)):
            return

        # calculate counts for each SeqLib
        log_message(
            logging_callback=logging.info,
            msg="Counting for each time point ({})".format(label),
            extra={"oname": self.name},
        )
        for lib in self.children:
            lib.calculate()

        # combine all libraries for a given timepoint
        log_message(
            logging_callback=logging.info,
            msg="Aggregating SeqLib data",
            extra={"oname": self.name},
        )

        destination = "/main/{}/counts_unfiltered".format(label)
        if destination in list(self.store.keys()):
            # need to remove the current destination table because we are
            # using append, append is required because it takes
            # the "min_itemsize" argument, and put doesn't
            log_message(
                logging_callback=logging.info,
                msg="Replacing existing '{}'".format(destination),
                extra={"oname": self.name},
            )
            self.store.remove(destination)

        # seqlib count table name for this element type
        lib_table = "/main/{}/counts".format(label)

        # create an index of all elements in the analysis
        complete_index = pd.Index([])
        for tp in self.timepoints:
            for lib in self.libraries[tp]:
                complete_index = complete_index.union(
                    pd.Index(lib.store.get_column(lib_table, "index"))
                )
        log_message(
            logging_callback=logging.info,
            msg="Created shared index for count data ({} {})".format(
                len(complete_index), label
            ),
            extra={"oname": self.name},
        )

        # min_itemsize value
        max_index_length = complete_index.map(len).max()

        # perform operation in chunks
        for i in range(0, len(complete_index), self.chunksize):
            # don't duplicate the index if the chunksize is large
            if self.chunksize < len(complete_index):
                index_chunk = complete_index[i : i + self.chunksize]
            else:
                index_chunk = complete_index

            log_message(
                logging_callback=logging.info,
                msg="Merging counts for chunk {} ({} rows)".format(
                    i // self.chunksize + 1, len(index_chunk)
                ),
                extra={"oname": self.name},
            )

            for tp in self.timepoints:
                c = self.libraries[tp][0].store.select(
                    key=lib_table, where="index={}".format(list(index_chunk))
                )
                for lib in self.libraries[tp][1:]:
                    c = c.add(
                        lib.store.select(
                            key=lib_table, where="index={}".format(list(index_chunk))
                        ),
                        fill_value=0,
                    )
                c.columns = ["c_{}".format(tp)]
                if tp == 0:
                    tp_frame = c
                else:
                    tp_frame = tp_frame.join(c, how="outer")

            # save the unfiltered counts
            if "/main/{}/counts_unfiltered".format(label) not in self.store:
                self.store.append(
                    key="/main/{}/counts_unfiltered".format(label),
                    value=tp_frame.astype(float),
                    min_itemsize={"index": max_index_length},
                    data_columns=list(tp_frame.columns),
                )
            else:
                self.store.append(
                    key="/main/{}/counts_unfiltered".format(label),
                    value=tp_frame.astype(float),
                )

    def filter_counts(self, label):
        """
        Converts unfiltered counts stored in ``/main/label/counts_unfiltered`` 
        into filtered counts calculated from complete cases (elements with a 
        non-zero count in each time point).

        For the most basic element type (variant or barcode, depending on the 
        experimental design), the result of this operation simply drops any 
        rows that have missing counts. For other element types, such as 
        synonymous variants, the counts are re-aggregated using only the 
        complete cases in the underlying element type.
        """
        valid_type = self.is_barcodeid() or self.is_barcodevariant()
        if valid_type and label != "barcodes":
            # calculate proper combined counts
            # df = self.store._store.select("/main/barcodes/counts")
            # this should exist because of the order of label calculations
            # redo the barcode->variant/id mapping with the filtered counts
            # NOT YET IMPLEMENTED
            # TODO: just do this for now
            df = self.store.select("/main/{}/counts_unfiltered".format(label))
        else:
            df = self.store.select("/main/{}/counts_unfiltered".format(label))
        df.dropna(axis="index", how="any", inplace=True)
        self.store.put(
            "/main/{}/counts".format(label), df.astype(float), data_columns=df.columns
        )

    def combine_barcode_maps(self):
        """
        Combine all barcode maps for 
        :py:class:`~enrich2.libraries.seqlib.SeqLib` implementations
        into a single data frame and store it in ``'/main/barcodemap'``.

        If multiple variants or IDs map to the same barcode, only the first one
        will be present in the barcode map table.

        The ``'/main/barcodemap'`` table is not created if no
        :py:class:`~enrich2.libraries.seqlib.SeqLib` has barcode map 
        information.
        """
        if self.check_store("/main/barcodemap"):
            return

        bcm = None
        for lib in self.children:
            if bcm is None:
                bcm = lib.store["/raw/barcodemap"]
            else:
                bcm = bcm.join(
                    lib.store["/raw/barcodemap"], rsuffix=".drop", how="outer"
                )
                new = bcm.loc[pd.isnull(bcm)["value"]]
                bcm.loc[new.index, "value"] = new["value.drop"]
                bcm.drop("value.drop", axis="columns", inplace=True)
        bcm.sort_values("value", inplace=True)
        self.store.put(key="/main/barcodemap", value=bcm, data_columns=bcm.columns)

    def timepoint_indices_intersect(self):
        """
        Check to see if timepoints share all variants in common for all labels.
        Raises ValueError if not.
        """
        for label in self.labels:
            self.timepoint_indices_intersect_for_label(label)

    def timepoint_indices_intersect_for_label(self, label):
        """
        For a single label, check to see if timepoints share all variants
        in common. Raises ValueError if not.
        """
        from functools import reduce

        table_key = "/main/{}/counts".format(label)
        libs = [lib for tp in self.timepoints for lib in self.libraries[tp]]
        series_ls = [lib.store.get_column(table_key, "index") for lib in libs]
        index_ls = [pd.Index(series.values) for series in series_ls]
        index_len_ls = [len(set(idx)) for idx in index_ls]
        common = reduce(lambda idx1, idx2: idx1.intersection(idx2), index_ls)
        common_len = len(common)
        all_good = all(common_len == idx_len for idx_len in index_len_ls)
        if not all_good:
            raise ValueError(
                "Timepoints contain different variants" " for label {}.".format(label)
            )

    def timepoints_contain_variants(self):
        """
        For each label, check to see if timepoints share all variants in
        common. Raises ValueError if not.
        """
        for label in self.labels:
            self.timepoints_contain_variants_for_label(label)

    def timepoints_contain_variants_for_label(self, label):
        """
        For a single label, check to see if timepoints share all variants in
        common. Raises ValueError if not.
        """
        table_key = "/main/{}/counts".format(label)
        libs = [lib for tp in self.timepoints for lib in self.libraries[tp]]
        series_ls = [lib.store.get_column(table_key, "index") for lib in libs]
        all_good = all(set(s.values) != set(["_wt"]) for s in series_ls)
        if not all_good:
            raise ValueError(
                "Some timepoints do not contain any"
                " variants for label {}.".format(label)
            )

    def table_not_empty_for_key(self, key):
        """
        Checks to see if a table exists in a hdf5 store and is populated.

        Parameters
        ----------
        key : `str`
            string key used to index a :py:class:`pd.HDFStore` store._store.

        Returns
        -------
        `bool`
            ``True`` if table exists but is empty.

        """
        if not self.table_exists_for_key(key):
            raise ValueError("Required table {} does " "not exist.".format(key))
        empty = self.store[key].empty
        return not empty

    def score_index_has_been_modified(self, label):
        """
        Check to see if the index of a dataframe has been modified when
        going from counts to scores dataframes.
        
        Parameters
        ----------
        label : `str`
            label pointing to /main/{}/scores.

        Returns
        -------
        `bool`
            ``True`` if index of scores matches counts for label.
        """
        scores_key = "/main/{}/scores".format(label)
        counts_key = "/main/{}/counts".format(label)
        if self.table_exists_for_key(scores_key):
            scores_index = self.get_table(scores_key).index
            counts_index = self.get_table(counts_key).index
            return scores_index.equals(counts_index)
        else:
            raise ValueError(
                "Table {} does not exist [{}].".format(scores_key, self.name)
            )

    def table_exists_for_key(self, key):
        """
        Checks to see if a table exists in a hdf5 store._store.

        Parameters
        ----------
        key : `str` 
            String key used to index a :py:class:`pd.HDFStore` store._store.

        Returns
        -------
        `bool`
            ``True`` if table exists but is empty.

        """
        exists = self.check_store(key)
        return exists

    def ensure_main_count_tables_exist_and_populated(self):
        """
        Before the main computations are performed, checks to see if the
        required count tables in main exist and are populated.
        """
        for label in self.labels:
            key = "/main/{}/counts".format(label)

            if not self.table_exists_for_key(key):
                raise ValueError("Required table {} does " "not exist.".format(key))

            if not self.table_not_empty_for_key(key):
                raise ValueError("Required table {} does " "is empty.".format(key))

    def calculate(self):
        """
        Wrapper method to calculate counts and enrichment scores 
        for all data in the :py:class:`~enrich2.selection.selection.Selection`.
        """
        scorer_class_name = self.get_root().scorer_class.name

        if len(self.labels) == 0:
            raise ValueError(
                "No data present across all "
                "sequencing libraries [{}]".format(self.name)
            )

        for label in self.labels:
            self.merge_counts_unfiltered(label)
            self.filter_counts(label)

        if self.is_barcodevariant() or self.is_barcodeid():
            self.combine_barcode_maps()

        self.ensure_main_count_tables_exist_and_populated()
        self.timepoints_contain_variants()

        if "Demo" in scorer_class_name:
            raise ValueError(
                'Invalid scoring method "{}" '
                "[{}]".format(scorer_class_name, self.name)
            )

        if "Regression" in scorer_class_name and len(self.timepoints) <= 2:
            raise ValueError(
                "Regression-based scoring " "requires three or more time points."
            )

        scorer = self.get_root().scorer_class(
            store_manager=self, options=self.get_root().scorer_class_attrs
        )
        scorer.run()

        # TODO: Write outlier computation as a plugin?
        non_allowed_methods = ("Counts Only", "Demo")
        scoring_method = scorer_class_name

        if scoring_method not in non_allowed_methods and self.component_outliers:
            if self.is_barcodevariant() or self.is_barcodeid():
                self.calc_outliers("barcodes")
            if self.is_coding():
                self.calc_outliers("variants")

    def write_tsv(self):
        """
        Write each table from the store to its own tab-separated file.

        Files are written to a ``tsv`` directory in the default output
        location.
        File names are the HDF5 key with ``'_'`` substituted for ``'/'``.
        """
        if self.tsv_requested:
            log_message(
                logging_callback=logging.info,
                msg="Generating tab-separated output files",
                extra={"oname": self.name},
            )
            for k in self.store.keys():
                self.write_table_tsv(k)
        for lib in self.children:
            lib.write_tsv()

    def synonymous_variants(self):
        """
        Populate and return a dictionary mapping synonymous variants to the 
        list of associated variants in ``/main/variants/counts``.
        """
        mapping = dict()
        try:
            variants = self.store.get_column(
                key="/main/variants/counts", column="index"
            )
        except KeyError:
            raise KeyError("No variant counts found [{}]".format(self.name))
        for v in variants:
            pv = protein_variant(v)
            try:
                mapping[pv].append(v)
            except KeyError:
                mapping[pv] = [v]
        return mapping

    def barcodemap_mapping(self):
        """
        Return a `dict` representation of the ``'/main/barcodemap'`` table.
        
        Returns
        -------
        `dict`
            Mapping of barcode keys to barcode map values.
        """
        mapping = dict()
        for bc, v in self.store["/main/barcodemap"].iterrows():
            v = v["value"]
            try:
                mapping[v].update([bc])
            except KeyError:
                mapping[v] = set([bc])
        return mapping

    def calc_outliers(self, label, minimum_components=4, log_chunksize=20000):
        """
        Test whether an element's individual components have significantly
        different scores from the element. Results are stored
        in ``'/main/<label>/outliers'``.

        Parameters
        ----------
        label : `str`
            label for the component (``'variants'`` or ``'barcodes'``)
        minimum_components : `int`
            minimum number of componenents required for any statistics 
            to be calculated
        log_chunksize : `int` 
            will output a log message every *n* rows
        """
        if self.check_store("/main/{}/outliers".format(label)):
            return

        if label == "variants":
            label2 = "synonymous"
        elif label == "barcodes":
            if self.is_barcodevariant():
                label2 = "variants"
            elif self.is_barcodeid():
                label2 = "identifiers"
            else:
                # this should never happen
                raise AttributeError(
                    "Failed to identify parent "
                    "label when calculating "
                    "barcode outliers [{}]".format(self.name)
                )
        else:
            raise KeyError(
                "Invalid label '{}' for calc_outliers [{}]".format(label, self.name)
            )

        log_message(
            logging_callback=logging.info,
            msg="Identifying outliers ({}-{})".format(label, label2),
            extra={"oname": self.name},
        )
        log_message(
            logging_callback=logging.info,
            msg="Mapping {} to {}".format(label, label2),
            extra={"oname": self.name},
        )

        if label == "variants":
            mapping = self.synonymous_variants()
        elif label == "barcodes":
            mapping = self.barcodemap_mapping()
        else:
            raise KeyError(
                "Invalid label '{}' for calc_outliers [{}]".format(label, self.name)
            )

        # get the scores
        df1 = self.store.select(
            "/main/{}/scores".format(label), columns=["score", "SE"]
        )
        df2 = self.store.select(
            "/main/{}/scores".format(label2), columns=["score", "SE"]
        )

        # pre-calculate variances
        df1["var"] = df1["SE"] ** 2
        df1.drop("SE", axis=1, inplace=True)
        df2["var"] = df2["SE"] ** 2
        df2.drop("SE", axis=1, inplace=True)

        # set up empty results DF
        result_df = pd.DataFrame(
            np.nan, index=df1.index, columns=["z", "pvalue_raw", "parent"]
        )

        # because this step can be slow, output chunk-style logging messages
        # pre-calculate the lengths for the log messages
        log_chunk = 1
        log_chunksize_list = [log_chunksize] * (len(df2) / log_chunksize) + [
            len(df2) % log_chunksize
        ]

        for i, x in enumerate(df2.index):
            if i % log_chunksize == 0:
                log_message(
                    logging_callback=logging.info,
                    msg="Calculating outlier p-values for "
                    "chunk {} ({} rows) ({}-{})".format(
                        log_chunk, log_chunksize_list[log_chunk - 1], label, label2
                    ),
                    extra={"oname": self.name},
                )
                log_chunk += 1
            try:
                components = df1.loc[mapping[x]].dropna(axis="index", how="all")
            except KeyError:
                # none of the components were in the index
                continue
            if len(components.index) >= minimum_components:
                for c in components.index:
                    zvalue = np.absolute(
                        df2.loc[x, "score"] - df1.loc[c, "score"]
                    ) / np.sqrt(df2.loc[x, "var"] + df1.loc[c, "var"])
                    result_df.loc[c, "z"] = zvalue
                    result_df.loc[c, "pvalue_raw"] = 2 * stats.norm.sf(zvalue)
                    result_df.loc[c, "parent"] = x
        if WILD_TYPE_VARIANT in result_df.index:
            result_df.loc[WILD_TYPE_VARIANT, "z"] = np.nan
            result_df.loc[WILD_TYPE_VARIANT, "pvalue_raw"] = np.nan
        result_df["z"] = result_df["z"].astype(float)
        result_df["pvalue_raw"] = result_df["pvalue_raw"].astype(float)

        self.store.put(
            key="/main/{}/outliers".format(label),
            value=result_df,
            data_columns=result_df.columns,
        )
