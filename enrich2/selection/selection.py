#  Copyright 2016-2017 Alan F Rubin
#
#  This file is part of Enrich2.
#
#  Enrich2 is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Enrich2 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Enrich2.  If not, see <http://www.gnu.org/licenses/>.


import logging

import numpy as np
import pandas as pd
import scipy.stats as stats

from ..base.constants import WILD_TYPE_VARIANT
from ..base.storemanager import StoreManager
from ..config.config_check import seqlib_type
from ..libraries.barcode import BarcodeSeqLib
from ..libraries.barcodeid import BcidSeqLib
from ..libraries.barcodevariant import BcvSeqLib
from ..libraries.basic import BasicSeqLib
from ..libraries.idonly import IdOnlySeqLib
from ..libraries.variant import protein_variant

globals()['BasicSeqLib'] = BasicSeqLib
globals()['BarcodeSeqLib'] = BarcodeSeqLib
globals()['BcvSeqLib'] = BcvSeqLib
globals()['BcidSeqLib'] = BcidSeqLib
globals()['IdOnlySeqLib'] = IdOnlySeqLib


class Selection(StoreManager):
    """
    Class for a single selection replicate, consisting of multiple 
    timepoints. This class coordinates :py:class:`~seqlib.seqlib.SeqLib` 
    objects.
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
        Return the :py:class:`~seqlib.seqlib.SeqLib` objects as a list, 
        sorted by timepoint and then by name.
        """
        libs = list()
        for tp in self.timepoints:
            libs.extend(sorted(self.libraries[tp], key=lambda x: x.name))
        return libs

    def remove_child_id(self, tree_id):
        """
        Remove the reference to a :py:class:`~seqlib.seqlib.SeqLib` with 
        Treeview id *tree_id*. Deletes empty time points.
        """
        empty = None
        for tp in self.libraries:
            tp_ids = [lib.treeview_id for lib in self.libraries[tp]]
            if tree_id in tp_ids:
                del self.libraries[tp][tp_ids.index(tree_id)]
                if len(self.libraries[tp]) == 0:
                    empty = tp
                break   # found the id, stop looking
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
                raise ValueError("Selection should not contain wild type "
                                 "sequence [{}]".format(self.name))
            else:
                return None

    def configure(self, cfg, configure_children=True):
        """
        Set up the :py:class:`~selection.Selection` using the *cfg* object, 
        usually from a ``.json`` configuration file.

        If *configure_children* is false, do not configure the children in 
        *cfg*.
        """

        StoreManager.configure(self, cfg)
        if configure_children:
            if 'libraries' not in cfg:
                raise KeyError("Missing required config value "
                               "{} [{}]".format('libraries', self.name))

            for lib_cfg in cfg['libraries']:
                libtype = seqlib_type(lib_cfg)
                if libtype is None:
                    raise ValueError("Unrecognized SeqLib config")
                elif libtype in ('BcvSeqLib', 'BcidSeqLib'):
                    lib = globals()[libtype]()
                    # don't re-parse the barcode maps if possible
                    mapfile = lib_cfg['barcodes']['map file']
                    if mapfile in list(self.barcode_maps.keys()):
                        lib.configure(
                            lib_cfg, barcode_map=self.barcode_maps[mapfile])
                    else:
                        lib.configure(lib_cfg)
                        self.barcode_maps[mapfile] = lib.barcode_map
                    self.add_child(lib)
                else:
                    # requires that the SeqLib derived classes be
                    # imported into the module namespace
                    # using "from x import y" style
                    lib = globals()[libtype]()
                    lib.configure(lib_cfg)
                    self.add_child(lib)

    def validate(self):
        """
        Raises an informative ``ValueError`` if the time points in the
        analysis are not suitable. Calls validate method on all child SeqLibs.
        """
        # check the time points
        if 0 not in self.timepoints:
            raise ValueError("Missing timepoint 0 [{}]".format(self.name))

        if self.timepoints[0] != 0:
            raise ValueError("Invalid negative "
                             "timepoint [{}]".format(self.name))

        if len(self.timepoints) < 2:
            raise ValueError("Multiple timepoints "
                             "required [{}]".format(self.name))

        elif len(self.timepoints) < 3 and self.scoring_method in ("WLS", "OLS"):
            raise ValueError("Insufficient number of timepoints for "
                             "regression scoring [{}]".format(self.name))
        
        # check the wild type sequences
        if self.has_wt_sequence():
            for child in self.children[1:]:
                if self.children[0].wt != child.wt:
                    logging.warning(
                        msg="Inconsistent wild type sequences",
                        extra={'oname' : self.name}
                    )
                    break
        
        # check that we're not doing wild type normalization
        # on something with no wild type
        if not self.has_wt_sequence() and self.logr_method == "wt":
            raise ValueError("No wild type sequence for wild "
                             "type normalization [{}]".format(self.name))

        # validate children
        for child in self.children:
            child.validate()

    def serialize(self):
        """
        Format this object (and its children) as a config object
        suitable for dumping to a config file.
        """
        cfg = StoreManager.serialize(self)
        cfg['libraries'] = [child.serialize() for child in self.children]
        return cfg

    def add_child(self, child):
        if child.name in self.child_names():
            raise ValueError("Non-unique sequencing library name "
                             "'{}' [{}]".format(child.name, self.name))
        child.parent = self
        try:
            self.libraries[child.timepoint].append(child)
        except KeyError:
            self.libraries[child.timepoint] = [child]

    def is_barcodevariant(self):
        """
        Return ``True`` if all :py:class:`~seqlib.seqlib.SeqLib` in the 
        :py:class:`~selection.Selection` are 
        :py:class:`~barcodevariant.BcvSeqLib` objects with 
        the same barcode map, else ``False``.
        """
        return all(isinstance(lib, BcvSeqLib) for lib in self.children) and \
            len(list(self.barcode_maps.keys())) == 1

    def is_barcodeid(self):
        """
        Return ``True`` if all :py:class:`~seqlib.SeqLib` in the 
        :py:class:`~selection.Selection` are 
        :py:class:`~barcodeid.BcidSeqLib` objects with 
        the same barcode map, else ``False``.
        """
        return all(isinstance(lib, BcidSeqLib) for lib in self.children) and \
            len(list(self.barcode_maps.keys())) == 1

    def is_coding(self):
        """
        Return ``True`` if the all :py:class:`~seqlib.seqlib.SeqLib` in the 
        :py:class:`~selection.Selection` count protein-coding variants, else 
        ``False``.
        """
        return all(x.is_coding() for x in self.children)

    def has_wt_sequence(self):
        """
        Return ``True`` if the all :py:class:`~seqlib.seqlib.SeqLib` in the 
        :py:class:`~selection.Selection` have a wild type sequence, else 
        ``False``.
        """
        return all(x.has_wt_sequence() for x in self.children)

    def merge_counts_unfiltered(self, label):
        """
        Counts :py:class:`~seqlib.seqlib.SeqLib` objects and tabulates counts 
        for each timepoint. :py:class:`~seqlib.seqlib.SeqLib` objects from 
        the same timepoint are combined by summing the counts.

        Stores the unfiltered counts under ``/main/label/counts_unfiltered``.
        """
        if self.check_store("/main/{}/counts_unfiltered".format(label)):
            return

        # calculate counts for each SeqLib
        logging.info(
            msg="Counting for each time point ({})".format(label),
            extra={'oname' : self.name}
        )
        for lib in self.children:
            lib.calculate()

        # combine all libraries for a given timepoint
        logging.info("Aggregating SeqLib data", extra={'oname' : self.name})

        destination = "/main/{}/counts_unfiltered".format(label)
        if destination in list(self.store.keys()):
            # need to remove the current destination table because we are
            # using append, append is required because it takes
            # the "min_itemsize" argument, and put doesn't
            logging.info(
                msg="Replacing existing '{}'".format(destination),
                extra={'oname' : self.name}
            )
            self.store.remove(destination)

        # seqlib count table name for this element type
        lib_table = "/main/{}/counts".format(label)

        # create an index of all elements in the analysis
        complete_index = pd.Index([])
        for tp in self.timepoints:
            for lib in self.libraries[tp]:
                complete_index = complete_index.union(
                    pd.Index(lib.store.select_column(lib_table, 'index'))
                )
        logging.info(
            "Created shared index for count data ({} {})".format(
                len(complete_index), label), extra={'oname' : self.name})

        # min_itemsize value
        max_index_length = complete_index.map(len).max()

        # perform operation in chunks
        for i in range(0, len(complete_index), self.chunksize):
            # don't duplicate the index if the chunksize is large
            if self.chunksize < len(complete_index):
                index_chunk = complete_index[i:i + self.chunksize]
            else:
                index_chunk = complete_index
            logging.info("Merging counts for chunk {} ({} rows)".format(
                i // self.chunksize + 1, len(index_chunk)),
                extra={'oname' : self.name}
            )

            for tp in self.timepoints:
                c = self.libraries[tp][0].store.select(
                    lib_table, "index = index_chunk"
                )
                for lib in self.libraries[tp][1:]:
                    c = c.add(lib.store.select(
                        lib_table, "index = index_chunk"), fill_value=0
                    )
                c.columns = ["c_{}".format(tp)]
                if tp == 0:
                    tp_frame = c
                else:
                    tp_frame = tp_frame.join(c, how="outer")

            # save the unfiltered counts
            if "/main/{}/counts_unfiltered".format(label) not in self.store:
                self.store.append(
                    "/main/{}/counts_unfiltered".format(label),
                    tp_frame.astype(float),
                    min_itemsize={'index' : max_index_length},
                    data_columns=list(tp_frame.columns)
                )
            else:
                self.store.append(
                    "/main/{}/counts_unfiltered".format(label),
                    tp_frame.astype(float)
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
        valid_type = (self.is_barcodeid() or self.is_barcodevariant())
        if valid_type and label != 'barcodes':
            # calculate proper combined counts
            # df = self.store.select("/main/barcodes/counts")
            # this should exist because of the order of label calculations
            # redo the barcode->variant/id mapping with the filtered counts
            # NOT YET IMPLEMENTED
            # TODO: just do this for now
            df = self.store.select("/main/{}/counts_unfiltered".format(label))
        else:
            df = self.store.select("/main/{}/counts_unfiltered".format(label))
        df.dropna(axis="index", how="any", inplace=True)
        self.store.put(
            "/main/{}/counts".format(label),
            df.astype(float),
            format="table",
            data_columns=df.columns
        )

    def combine_barcode_maps(self):
        if self.check_store("/main/barcodemap"):
            return

        bcm = None
        for lib in self.children:
            if bcm is None:
                bcm = lib.store['/raw/barcodemap']
            else:
                bcm = bcm.join(lib.store['/raw/barcodemap'],
                               rsuffix=".drop", how="outer")
                new = bcm.loc[pd.isnull(bcm)['value']]
                bcm.loc[new.index, 'value'] = new['value.drop']
                bcm.drop("value.drop", axis="columns", inplace=True)
        bcm.sort_values("value", inplace=True)
        self.store.put(
            "/main/barcodemap", bcm,
            format="table",
            data_columns=bcm.columns
        )

    def timepoint_indices_intersect(self):
        """
        Check to see if timepoints share all variants in common for all labels.
        Raises ValueError if not.

        Returns
        -------
        None

        """
        for label in self.labels:
            self.timepoint_indices_intersect_for_label(label)

    def timepoint_indices_intersect_for_label(self, label):
        """
        For a single label, check to see if timepoints share all variants
        in common. Raises ValueError if not.

        Returns
        -------
        None

        """
        from functools import reduce
        table_key = "/main/{}/counts".format(label)
        libs = [lib for tp in self.timepoints for lib in self.libraries[tp]]
        series_ls = [lib.store.select_column(table_key, 'index') for lib in libs]
        index_ls = [pd.Index(series.values) for series in series_ls]
        index_len_ls = [len(set(idx)) for idx in index_ls]
        common = reduce(lambda idx1, idx2: idx1.intersection(idx2), index_ls)
        common_len = len(common)
        all_good = all(common_len == idx_len for idx_len in index_len_ls)
        if not all_good:
            raise ValueError("Timepoints contain different variants"
                             " for label {}.".format(label))

    def timepoints_contain_variants(self):
        """
        For each label, check to see if timepoints share all variants in
        common. Raises ValueError if not.

        Returns
        -------
        None

        """
        for label in self.labels:
            self.timepoints_contain_variants_for_label(label)

    def timepoints_contain_variants_for_label(self, label):
        """
        For a single label, check to see if timepoints share all variants in
        common. Raises ValueError if not.

        Returns
        -------
        None

        """
        table_key = "/main/{}/counts".format(label)
        libs = [lib for tp in self.timepoints for lib in self.libraries[tp]]
        series_ls = [lib.store.select_column(table_key, 'index') for lib in libs]
        all_good = all(set(s.values) != set(["_wt"]) for s in series_ls)
        if not all_good:
            raise ValueError("Some timepoints do not contain any"
                             " variants for label {}.".format(label))

    def table_not_empty_for_key(self, key):
        """
        Checks to see if a table exists in a hdf5 store and is populated.

        Parameters
        ----------
        key : `str`, string key used to index a hdf5 store.

        Returns
        -------
        rtype: `bool`, True if table exists but is empty.

        """
        if not self.table_exists_for_key(key):
            raise ValueError("Required table {} does "
                             "not exist.".format(key))
        empty = self.store[key].empty
        return not empty


    def score_index_has_been_modified(self, label):
        """
        Check to see if the index of a dataframe has been modified when
        going from counts to scores dataframes.
        
        Parameters
        ----------
        label : `str`, label pointing to /main/{}/scores.

        Returns
        -------
        rtype: `bool`, True if index of scores matches counts for label.
        """
        scores_key = '/main/{}/scores'.format(label)
        counts_key = '/main/{}/counts'.format(label)
        if self.table_exists_for_key(scores_key):
            scores_index = self.get_table(scores_key).index
            counts_index = self.get_table(counts_key).index
            return scores_index.equals(counts_index)
        else:
            raise ValueError("Table {} does not exist [{}].".format(
                scores_key, self.name
            ))

    def table_exists_for_key(self, key):
        """
        Checks to see if a table exists in a hdf5 store.

        Parameters
        ----------
        key : `str`, string key used to index a hdf5 store.

        Returns
        -------
        rtype: `bool`, True if table exists but is empty.

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
                raise ValueError("Required table {} does "
                                 "not exist.".format(key))

            if not self.table_not_empty_for_key(key):
                raise ValueError("Required table {} does "
                                 "is empty.".format(key))

    def calculate(self):
        """
        Wrapper method to calculate counts and enrichment scores 
        for all data in the :py:class:`~selection.Selection`.
        """

        if len(self.labels) == 0:
            raise ValueError("No data present across all "
                             "sequencing libraries [{}]".format(self.name))

        for label in self.labels:
            self.merge_counts_unfiltered(label)
            self.filter_counts(label)

        if self.is_barcodevariant() or self.is_barcodeid():
            self.combine_barcode_maps()

        self.ensure_main_count_tables_exist_and_populated()
        self.timepoints_contain_variants()

        if self.scoring_method == "counts":
            pass

        if 'Demo' in self.scoring_class.__name__:
            raise ValueError('Invalid scoring method "{}" '
                             '[{}]'.format(self.scoring_method, self.name))

        if 'Regression' in self.scoring_method and len(self.timepoints) <= 2:
            raise ValueError("Regression-based scoring "
                             "requires three or more time points.")

        scorer = self.scoring_class(
            store_manager=self,
            options=self.scoring_class_attrs
        )
        scorer.run()

        # TODO: Write outlier computation as a plugin?
        allowed_methods = ("ratios" , "WLS", "OLS")
        if self.scoring_method in allowed_methods and self.component_outliers:
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
            logging.info(
                "Generating tab-separated output files",
                extra={'oname' : self.name}
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
            variants = self.store.select_column(
                "/main/variants/counts", "index"
            )
        except KeyError:
            raise KeyError(
                "No variant counts found [{}]".format(self.name)
            )
        for v in variants:
            pv = protein_variant(v)
            try:
                mapping[pv].append(v)
            except KeyError:
                mapping[pv] = [v]
        return mapping

    def barcodemap_mapping(self):
        mapping = dict()
        for bc, v in self.store['/main/barcodemap'].iterrows():
            v = v['value']
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

        Args:
            label (str): label for the component
            (``'variants'`` or ``'barcodes'``)

            minimum_components (int): minimum number of componenents required
            for any statistics to be calculated

            log_chunksize (int): will output a log message every *n* rows

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
                raise AttributeError("Failed to identify parent "
                                     "label when calculating "
                                     "barcode outliers [{}]".format(self.name))
        else:
            raise KeyError("Invalid label '{}' for calc_outliers [{}]".format(
                label,  self.name))

        logging.info(
            "Identifying outliers ({}-{})".format(label, label2),
            extra={'oname' : self.name}
        )
        logging.info(
            "Mapping {} to {}".format(label, label2),
            extra={'oname' : self.name}
        )
        if label == "variants":
            mapping = self.synonymous_variants()
        elif label == "barcodes":
            mapping = self.barcodemap_mapping()
        else:
            raise KeyError("Invalid label '{}' for calc_outliers [{}]".format(
                label,  self.name))

        # get the scores
        df1 = self.store.select(
            "/main/{}/scores".format(label), "columns=['score', 'SE']")
        df2 = self.store.select(
            "/main/{}/scores".format(label2), "columns=['score', 'SE']")

        # pre-calculate variances
        df1['var'] = df1['SE'] ** 2
        df1.drop('SE', axis=1, inplace=True)
        df2['var'] = df2['SE'] ** 2
        df2.drop('SE', axis=1, inplace=True)

        # set up empty results DF
        result_df = pd.DataFrame(
            np.nan,
            index=df1.index,
            columns=['z', 'pvalue_raw', 'parent']
        )

        # because this step can be slow, output chunk-style logging messages
        # pre-calculate the lengths for the log messages
        log_chunk = 1
        log_chunksize_list = [log_chunksize] * \
                             (len(df2) / log_chunksize) + \
                             [len(df2) % log_chunksize]

        for i, x in enumerate(df2.index):
            if i % log_chunksize == 0:
                logging.info(
                    "Calculating outlier p-values for "
                    "chunk {} ({} rows) ({}-{})".format(
                        log_chunk, log_chunksize_list[log_chunk - 1],
                        label, label2), extra={'oname' : self.name})
                log_chunk += 1
            try:
                components = df1.loc[mapping[x]].dropna(
                    axis="index", how="all"
                )
            except KeyError:
                # none of the components were in the index
                continue
            if len(components.index) >= minimum_components:
                for c in components.index:
                    zvalue = np.absolute(
                        df2.loc[x, 'score'] - df1.loc[c, 'score']) / \
                             np.sqrt(df2.loc[x, 'var'] + df1.loc[c, 'var'])
                    result_df.loc[c, 'z'] = zvalue
                    result_df.loc[c, 'pvalue_raw'] = 2 * stats.norm.sf(zvalue)
                    result_df.loc[c, 'parent'] = x
        if WILD_TYPE_VARIANT in result_df.index:
            result_df.loc[WILD_TYPE_VARIANT, 'z'] = np.nan
            result_df.loc[WILD_TYPE_VARIANT, 'pvalue_raw'] = np.nan
        result_df['z'] = result_df['z'].astype(float)
        result_df['pvalue_raw'] = result_df['pvalue_raw'].astype(float)

        self.store.put(
            "/main/{}/outliers".format(label), result_df,
            format="table", data_columns=result_df.columns
        )
