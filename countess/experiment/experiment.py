"""
Enrich2 experiment experiment module
====================================

This module contains the class used by ``Enrich2`` to represent an 
experiment. This class coordinates experimental conditions, and typically
sits at the top level of the tree structure.
"""


import logging
import numpy as np
import pandas as pd
import scipy.stats as stats

from ..base.config_constants import SCORER, SCORER_OPTIONS, SCORER_PATH
from ..base.config_constants import CONDITIONS
from ..base.utils import compute_md5, log_message

from ..base.constants import WILD_TYPE_VARIANT
from ..base.storemanager import StoreManager
from ..statistics.random_effects import partitioned_rml_estimator
from ..statistics.random_effects import nan_filter_generator
from .condition import Condition


__all__ = ["Experiment"]


class Experiment(StoreManager):
    """
    Class for a coordinating multiple 
    :py:class:`~enrich2.selection.selection.Selection` objects. Creating an
    :py:class:`~enrich2.experiment.experiment.Experiment` requires a valid 
    *config* object, usually from a ``.json`` configuration file.
    
    Attributes
    ----------
    conditions : `list`
        A list of :py:class:`~enrich2.experiment.condition.Condition` objects
    _wt : :py:class:`~enrich2.sequence.wildtype.WildTypeSequence`
    
    Methods
    -------
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
    _children 
        Concrete method returning sorted conditions.
    remove_child_id
        Removes the child with the specified ``treeview_id`` 
    add_child
        Adds a child to this instance's children.
    selection_list
        Return a list of selections managed by this instance.
    is_coding
        Returns a boolean indicating if all children have coding sequences.
    has_wt_sequence
        Returns a boolean indicating if all children have a wt sequence.
    calculate
        Calculates combined scores with statistics from selections 
        and conditions.
    combine_barcode_maps
        Combine all barcode maps for selections into a single dataframe.
    calc_counts
        Create a data frame of all counts in this Experiment.
    calc_shared_full
        Create a data frame containing all scores across all selections.
    calc_shared
        Get the subset of scores that are shared across all Selections.
    calc_scores
        Combine the scores and standard errors within each condition.
    calc_pvalues_wt
        Calculate uncorrected pvalue for each variant compared to wild type.
    calc_pvalues_pairwise
        Calculate pvalues for each variant in each pair of Conditions.
    write_tsv
        Write each table from the store to its own tab-separated file.
    
    See Also
    --------
    :py:class:`~enrich2.experiment.condition.Condition`
    :py:class:`~enrich2.selection.selection.Selection`
    
    """

    store_suffix = "exp"
    treeview_class_name = "Experiment"

    def __init__(self):
        StoreManager.__init__(self)
        self.conditions = list()
        self._wt = None

    @property
    def wt(self):
        """
        Property managing the wild type sequences of the 
        :py:class:`~enrich2.selection.selection.Selection` objects being
        managed.
        
        Returns
        -------
        :py:class:`~enrich2.sequence.wildtype.WildTypeSequence`
        """
        if self.has_wt_sequence():
            if self._wt is None:
                self._wt = self.selection_list()[0].wt.duplicate(self.name)
            return self._wt
        else:
            if self._wt is not None:
                raise ValueError(
                    "Experiment should not contain wild type "
                    "sequence [{}]".format(self.name)
                )
            else:
                return None

    def configure(self, cfg, configure_children=True, init_from_gui=False):
        """
        Set up the :py:class:`~enrich2.experiment.experiment.Experiment` 
        using the *cfg* object, usually from a ``.json`` configuration file.
        
        Parameters
        ----------
        cfg : `dict` or :py:class:`~enrich2.config.types.ExperimentConfiguration`
            The object used to configure this instance.
        configure_children : `bool`
            Traverse children and configure each one.
        init_from_gui : `bool` 
            Allow this instance to be configured from a GUI.
            
        """
        from ..config.types import ExperimentConfiguration

        if isinstance(cfg, dict):
            cfg = ExperimentConfiguration(cfg, init_from_gui)
        elif not isinstance(cfg, ExperimentConfiguration):
            raise TypeError("`cfg` was neither a " "ExperimentConfiguration or dict.")

        StoreManager.configure(self, cfg.store_cfg)
        if configure_children:
            if len(cfg.condition_cfgs) == 0:
                raise KeyError(
                    "Missing required config value {} [{}]"
                    "".format("conditions", self.name)
                )
            for cnd_cfg in cfg.condition_cfgs:
                cnd = Condition()
                cnd.configure(cnd_cfg)
                self.add_child(cnd)

    def serialize(self):
        """
        Format this object (and its children) as a config object suitable for
        dumping to a config file.
        
        Returns
        -------
        `dict`
            Dictionary of configuration options.
        """
        cfg = StoreManager.serialize(self)
        cfg[CONDITIONS] = [child.serialize() for child in self.children]
        if self.get_root().scorer_class is not None:
            cfg[SCORER] = {
                SCORER_PATH: self.get_root().scorer_path,
                SCORER_OPTIONS: self.get_root().scorer_class_attrs,
                SCORER_PATH + " md5": compute_md5(self.get_root().scorer_path),
            }
        return cfg

    def _children(self):
        """
        Method bound to the ``children`` property. Returns a list of all
        :py:class:`~enrich2.experiment.condition.Condition` objects 
        belonging to this object, sorted by name.
        
        Returns
        -------
        `list`
            List of sorted conditions.
        """
        return sorted(self.conditions, key=lambda x: x.name)

    def add_child(self, child):
        """
        Add a condition to children conditions.
        """
        if child.name in self.child_names():
            raise ValueError(
                "Non-unique condition name '{}' [{}]" "".format(child.name, self.name)
            )
        child.parent = self
        self.conditions.append(child)

    def remove_child_id(self, tree_id):
        """
        Remove the reference to a 
        :py:class:`~enrich2.experiment.condition.Condition` 
        with Treeview id *tree_id*.
        """
        self.conditions = [x for x in self.conditions if x.treeview_id != tree_id]

    def selection_list(self):
        """
        Return the :py:class:``~enrich2.selection.selection.Selection` 
        objects as a list.
        
        Returns
        -------
        `list`
            List of selection objects.
        """
        selections = list()
        for cnd in self.children:
            selections.extend(cnd.children)
        return selections

    def validate(self):
        """
        Calls validate on all child Conditions. Also checks the wild type
        sequence status.
        """
        # check the wild type sequences
        if self.has_wt_sequence():
            for child in self.selection_list()[1:]:
                if self.selection_list()[0].wt != child.wt:
                    log_message(
                        logging_callback=logging.warning,
                        msg="Inconsistent wild type sequences",
                        extra={"oname": self.name},
                    )
                    break

        for child in self.children:
            child.validate()

    def is_coding(self):
        """
        Return ``True`` if the all 
        :py:class:`~enrich2.selection.selection.Selection` in the 
        :py:class:`~enrich2.experiment.experiment.Experiment` 
        count protein-coding variants, else 
        ``False``.
        
        Returns
        -------
        `bool`
            `True` if all selections are coding.
        """
        return all(x.is_coding() for x in self.selection_list())

    def has_wt_sequence(self):
        """
        Return ``True`` if the all 
        :py:class:`~enrich2.selection.selection.Selection` in the 
        :py:class:`~enrich2.experiment.experiment.Experiment` 
        have a wild type sequence, else 
        ``False``.
                
        Returns
        -------
        `bool`
            `True` if all selections have a wildtype sequence.
        """
        return all(x.has_wt_sequence() for x in self.selection_list())

    def calculate(self):
        """
        Calculate scores for all 
        :py:class:`~enrich2.selection.selection.Selection` objects, then
        combine scores across selections within a condition to generate 
        score statistics.
        """
        if len(self.labels) == 0:
            raise ValueError(
                "No data present across all conditions [{}]" "".format(self.name)
            )
        for s in self.selection_list():
            s.calculate()
        self.combine_barcode_maps()
        for label in self.labels:
            self.calc_counts(label)
            if self.get_root().scorer_class.name != "Counts Only":
                self.calc_shared_full(label)
                self.calc_shared(label)
                self.calc_scores(label)
                if label != "barcodes":
                    self.calc_pvalues_wt(label)

    def combine_barcode_maps(self):
        """
        Combine all barcode maps for 
        :py:class:`~enrich2.selection.selection.Selection` objects
        into a single data frame and store it in ``'/main/barcodemap'``.

        If multiple variants or IDs map to the same barcode, only the first one
        will be present in the barcode map table.

        The ``'/main/barcodemap'`` table is not created if no
        :py:class:`~enrich2.selection.selection.Selection` 
        has barcode map information.
        """
        if self.check_store("/main/barcodemap"):
            return

        bcm = None
        for sel in self.selection_list():
            if "/main/barcodemap" in list(sel.store.keys()):
                if bcm is None:
                    bcm = sel.store["/main/barcodemap"]
                else:
                    bcm = bcm.join(
                        sel.store["/main/barcodemap"], rsuffix=".drop", how="outer"
                    )
                    new = bcm.loc[pd.isnull(bcm)["value"]]
                    bcm.loc[new.index, "value"] = new["value.drop"]
                    bcm.drop("value.drop", axis="columns", inplace=True)
        if bcm is not None:
            bcm.sort_values("value", inplace=True)
            self.store.put("/main/barcodemap", bcm, data_columns=bcm.columns)

    def calc_counts(self, label):
        """
        Create a data frame of all counts in this Experiment. This data frame
        is not used for any calculations, but is provided to facilitate
        exploration of the data set.
        
        Parameters
        ----------
        label : `str` {'barcodes', 'variants', 'identifiers', 'synonymous'}
            A valid table label.
            
        See Also
        --------
        :py:mod:`~enrich2.base.constants`
        """
        if self.check_store("/main/{}/counts".format(label)):
            return

        idx = pd.IndexSlice

        # create columns multi-index
        # has to be lex-sorted for multi-slicing to work
        log_message(
            logging_callback=logging.info,
            msg="Creating column multi-index for counts ({})".format(label),
            extra={"oname": self.name},
        )
        conditions_index = list()
        selections_index = list()
        values_index = list()

        for cnd in self.children:
            for sel in cnd.children:
                conditions_index.extend([cnd.name] * len(sel.timepoints))
                selections_index.extend([sel.name] * len(sel.timepoints))
                values_index.extend(["c_{}".format(x) for x in sorted(sel.timepoints)])
        columns = pd.MultiIndex.from_tuples(
            list(zip(conditions_index, selections_index, values_index)),
            names=["condition", "selection", "timepoint"],
        )

        # create union index
        log_message(
            logging_callback=logging.info,
            msg="Creating row index for counts ({})".format(label),
            extra={"oname": self.name},
        )
        combined = None
        first = True
        for s in self.selection_list():
            if first:
                combined = s.store.select(
                    key="/main/{}/counts_unfiltered".format(label), columns=["index"]
                ).index
                first = False
            else:
                combined = combined.join(
                    s.store.select(
                        key="/main/{}/counts_unfiltered".format(label),
                        columns=["index"],
                    ).index,
                    how="outer",
                )

        # create and fill the data frames
        log_message(
            logging_callback=logging.info,
            msg="Populating Experiment data frame with " "counts ({})".format(label),
            extra={"oname": self.name},
        )
        data = pd.DataFrame(index=combined, columns=columns)
        for cnd in self.children:
            for sel in cnd.children:
                sel_data = sel.store.select(
                    key="/main/{}/counts_unfiltered".format(label)
                )
                for tp in sel.timepoints:
                    data.loc[:, idx[cnd.name, sel.name, "c_{}".format(tp)]] = sel_data[
                        "c_{}".format(tp)
                    ]
        self.store.put("/main/{}/counts".format(label), data)

    def calc_shared_full(self, label):
        """
        Use joins to create a data frame containing all scores across all
        Selections in the Experiment.
        
        Parameters
        ----------
        label : `str` {'barcodes', 'variants', 'identifiers', 'synonymous'}
            A valid table label.
            
        See Also
        --------
        :py:mod:`~enrich2.base.constants`
        """
        if self.check_store("/main/{}/scores_shared_full".format(label)):
            return

        idx = pd.IndexSlice

        # create columns multi-index
        # has to be lex-sorted for multi-slicing to work
        log_message(
            logging_callback=logging.info,
            msg="Creating column multi-index for scores ({})".format(label),
            extra={"oname": self.name},
        )
        conditions_index = list()
        selections_index = list()
        values_index = list()

        if self.get_root().scorer_class.name == "Ratios (Old Enrich)":
            values_list = ["score"]
        else:
            values_list = ["score", "SE"]

        for cnd in self.children:
            for sel in cnd.children:
                conditions_index.extend([cnd.name] * len(values_list))
                selections_index.extend([sel.name] * len(values_list))
                values_index.extend(sorted(values_list))
        columns = pd.MultiIndex.from_tuples(
            list(zip(conditions_index, selections_index, values_index)),
            names=["condition", "selection", "value"],
        )
        # create union index
        log_message(
            logging_callback=logging.info,
            msg="Creating row index for scores ({})".format(label),
            extra={"oname": self.name},
        )
        combined = None
        first = True
        for s in self.selection_list():
            if first:
                combined = s.store.select(
                    key="/main/{}/scores".format(label), columns=["index"]
                ).index
                first = False
            else:
                combined = combined.join(
                    s.store.select(
                        key="/main/{}/scores".format(label), columns=["index"]
                    ).index,
                    how="outer",
                )

        # create and fill the data frames
        log_message(
            logging_callback=logging.info,
            msg="Populating Experiment data frame with " "scores ({})".format(label),
            extra={"oname": self.name},
        )
        data = pd.DataFrame(index=combined, columns=columns)
        for cnd in self.children:
            for sel in cnd.children:
                sel_data = sel.store.select("/main/{}/scores".format(label))
                for v in values_list:
                    data.loc[:, idx[cnd.name, sel.name, v]] = sel_data[v]
        self.store.put("/main/{}/scores_shared_full".format(label), data)

    def calc_shared(self, label):
        """
        Get the subset of scores that are shared across all Selections in each
        Condition.
        
        Parameters
        ----------
        label : `str` {'barcodes', 'variants', 'identifiers', 'synonymous'}
            A valid table label.
            
        See Also
        --------
        :py:mod:`~enrich2.base.constants`
        
        """
        if self.check_store("/main/{}/scores_shared".format(label)):
            return

        log_message(
            logging_callback=logging.info,
            msg="Identifying subset shared across all " "Selections ({})".format(label),
            extra={"oname": self.name},
        )

        data = self.store.select("/main/{}/scores_shared_full".format(label))

        # identify variants found in all selections in at least two conditions
        idx = pd.IndexSlice
        complete = np.full(len(data.index), False, dtype=bool)
        for cnd in data.columns.levels[0]:
            mask_score = (
                data.loc[:, idx[cnd, :, "score"]].notnull().sum(axis="columns") >= 2
            )
            complete = np.logical_or(complete, mask_score)

            # try:
            #     mask_se = (data.loc[:, idx[cnd, :, 'SE']].notnull().sum(
            #         axis='columns') >= 2
            #                )
            #     complete = np.logical_or(complete, mask_se)
            # except KeyError:
            #     pass

        data = data.loc[complete]
        self.store.put("/main/{}/scores_shared".format(label), data)

    def calc_scores(self, label):
        """
        Combine the scores and standard errors within each condition.
        
        Parameters
        ----------
        label : `str` {'barcodes', 'variants', 'identifiers', 'synonymous'}
            A valid table label.
            
        See Also
        --------
        :py:mod:`~enrich2.base.constants`
        
        """
        if self.check_store("/main/{}/scores".format(label)):
            return

        log_message(
            logging_callback=logging.info,
            msg="Calculating per-condition scores ({})".format(label),
            extra={"oname": self.name},
        )

        # set up new data frame
        shared_index = self.store.select(
            key="/main/{}/scores_shared".format(label), columns=["index"]
        ).index

        columns = pd.MultiIndex.from_product(
            [sorted(self.child_names()), sorted(["score", "SE", "epsilon"])],
            names=["condition", "value"],
        )

        data = pd.DataFrame(np.nan, index=shared_index, columns=columns)
        del shared_index
        del columns

        # set up local variables
        idx = pd.IndexSlice

        score_df = self.store.select("/main/{}/scores_shared".format(label))
        if self.get_root().scorer_class.name == "Ratios (Old Enrich)":
            # special case for simple ratios that have no SE
            # calculates the average score
            for cnd in score_df.columns.levels[0]:
                y = np.array(score_df.loc[:, idx[cnd, :, "score"]].values).T
                for y_k, num_reps in nan_filter_generator(y):
                    data.loc[:, idx[cnd, "score"]] = y_k.mean(axis=0)
                    # data.loc[:, idx[cnd, 'nreps']] = num_reps
        else:
            for cnd in score_df.columns.levels[0]:
                y = np.array(score_df.loc[:, idx[cnd, :, "score"]].values).T
                sigma2i = np.array(score_df.loc[:, idx[cnd, :, "SE"]].values ** 2).T

                # single replicate of the condition
                if y.shape[0] == 1:
                    data.loc[:, idx[cnd, "score"]] = y.ravel()
                    data.loc[:, idx[cnd, "SE"]] = np.sqrt(sigma2i).ravel()
                    data.loc[:, idx[cnd, "epsilon"]] = 0.0
                    # data.loc[:, idx[cnd, 'nreps']] = 1

                # multiple replicates
                else:
                    betaML, var_betaML, eps, reps = partitioned_rml_estimator(
                        y, sigma2i
                    )
                    data.loc[:, idx[cnd, "score"]] = betaML
                    data.loc[:, idx[cnd, "SE"]] = np.sqrt(var_betaML)
                    data.loc[:, idx[cnd, "epsilon"]] = eps

                    # TODO: uncomment these
                    # data.loc[:, idx[cnd, 'nreps']] = reps

                # special case for normalized wild type variant
                logr_method = self.get_root().scorer_class_attrs.get("logr_method", "")
                if logr_method == "wt" and WILD_TYPE_VARIANT in data.index:
                    data.loc[WILD_TYPE_VARIANT, idx[:, "SE"]] = 0.0
                    data.loc[WILD_TYPE_VARIANT, idx[:, "score"]] = 0.0
                    data.loc[WILD_TYPE_VARIANT, idx[:, "epsilon"]] = 0.0

        # store the data
        if data.empty:
            raise ValueError("All {} have a NaN score.".format(label))
        self.store.put("/main/{}/scores".format(label), data)

    def calc_pvalues_wt(self, label):
        """
        Calculate uncorrected pvalue for each variant compared to wild type.
        
        Parameters
        ----------
        label : `str` {'barcodes', 'variants', 'identifiers', 'synonymous'}
            A valid table label.
            
        See Also
        --------
        :py:mod:`~enrich2.base.constants`
        
        """
        if self.check_store("/main/{}/scores_pvalues_wt".format(label)):
            return

        idx = pd.IndexSlice

        wt = self.store.select(
            key="/main/{}/scores".format(label),
            where="index={}".format(WILD_TYPE_VARIANT),
        )
        if len(wt) == 0:  # no wild type score
            log_message(
                logging_callback=logging.info,
                msg="Failed to find wild type score, skipping wild type "
                "p-value calculations",
                extra={"oname": self.name},
            )
            return
        data = self.store.select(
            key="/main/{}/scores".format(label),
            where="index!={}".format(WILD_TYPE_VARIANT),
        )

        columns = pd.MultiIndex.from_product(
            [sorted(self.child_names()), sorted(["z", "pvalue_raw"])],
            names=["condition", "value"],
        )
        result_df = pd.DataFrame(index=data.index, columns=columns)

        condition_labels = data.columns.levels[0]
        for cnd in condition_labels:
            result_df.loc[:, idx[cnd, "z"]] = np.absolute(
                wt.loc[WILD_TYPE_VARIANT, idx[cnd, "score"]]
                - data.loc[:, idx[cnd, "score"]]
            ) / np.sqrt(
                wt.loc[WILD_TYPE_VARIANT, idx[cnd, "SE"]] ** 2
                + data.loc[:, idx[cnd, "SE"]] ** 2
            )
            result_df.loc[:, idx[cnd, "pvalue_raw"]] = 2 * stats.norm.sf(
                result_df.loc[:, idx[cnd, "z"]]
            )

        self.store.put("/main/{}/scores_pvalues_wt".format(label), result_df)

    def calc_pvalues_pairwise(self, label):
        """
        Calculate pvalues for each variant in each pair of Conditions.
        
        Parameters
        ----------
        label : `str` {'barcodes', 'variants', 'identifiers', 'synonymous'}
            A valid table label.
            
        See Also
        --------
        :py:mod:`~enrich2.base.constants`
        
        """
        if self.check_store("/main/{}/scores_pvalues".format(label)):
            return

        data = self.store["/main/{}/scores".format(label)]

        cnd1_index = list()
        cnd2_index = list()
        values_index = list()

        values_list = ["z", "pvalue_raw"]

        condition_labels = data.columns.levels[0]
        for i, cnd1 in enumerate(condition_labels):
            for cnd2 in condition_labels[i + 1 :]:
                cnd1_index.extend([cnd1] * len(values_list))
                cnd2_index.extend([cnd2] * len(values_list))
                values_index.extend(sorted(values_list))
        columns = pd.MultiIndex.from_tuples(
            list(zip(cnd1_index, cnd2_index, values_index)),
            names=["condition1", "condition2", "value"],
        )

        idx = pd.IndexSlice
        result_df = pd.DataFrame(np.nan, index=data.index, columns=columns)
        for i, cnd1 in enumerate(condition_labels):
            for cnd2 in condition_labels[i + 1 :]:
                result_df.loc[:, idx[cnd1, cnd2, "z"]] = np.absolute(
                    data.loc[:, idx[cnd1, "score"]] - data.loc[:, idx[cnd2, "score"]]
                ) / np.sqrt(
                    data.loc[:, idx[cnd1, "SE"]] ** 2
                    + data.loc[:, idx[cnd2, "SE"]] ** 2
                )
                result_df.loc[:, idx[cnd1, cnd2, "pvalue_raw"]] = 2 * stats.norm.sf(
                    result_df.loc[:, idx[cnd1, cnd2, "z"]]
                )

        self.store.put("/main/{}/scores_pvalues".format(label), result_df)

    def write_tsv(self, subdirectory=None, keys=None):
        """
        Write each table from the store to its own tab-separated file.

        Files are written to a ``tsv`` directory in the default output
        location. File names are the HDF5 key with ``'_'`` substituted for
        ``'/'``.
        """
        if self.tsv_requested:
            log_message(
                logging_callback=logging.info,
                msg="Generating tab-separated output files",
                extra={"oname": self.name},
            )
            for k in list(self.store.keys()):
                self.write_table_tsv(k)
        for s in self.selection_list():
            s.write_tsv()
