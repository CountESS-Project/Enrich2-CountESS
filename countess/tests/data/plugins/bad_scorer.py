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
import statsmodels.api as sm
import scipy.stats as stats
from countess.plugins.scoring import BaseScorerPlugin
from countess.base.constants import WILD_TYPE_VARIANT


class RegressionScorer(BaseScorerPlugin):
    def __init__(self, store_manager, options):
        super().__init__(store_manager, options)

    def compute_scores(self):
        for label in self.store_labels():
            self.calc_log_ratios(label)
            if self.weighted:
                self.calc_weights(label)
            self.calc_regression(label)

    def row_apply_function(self, *args, **kwargs):
        """
        :py:meth:`pandas.DataFrame.apply` apply function for calculating 
        enrichment using linear regression. If *weighted* is ``True`` perform
        weighted least squares; else perform ordinary least squares.

        Weights for weighted least squares are included in *row*.

        Returns a :py:class:`pandas.Series` containing regression coefficients,
        residuals, and statistics.
        """
        row, timepoints, weighted = args

        # retrieve log ratios from the row
        y = row[["L_{}".format(t) for t in timepoints]]

        # re-scale the x's to fall within [0, 1]
        xvalues = [x / float(max(timepoints)) for x in timepoints]

        # perform the fit
        X = sm.add_constant(xvalues)  # fit intercept
        if weighted:
            W = row[["W_{}".format(t) for t in timepoints]]
            fit = sm.WLS(y, X, weights=W).fit()
        else:
            fit = sm.OLS(y, X).fit()

        # re-format as a data frame row
        values = np.concatenate(
            [
                fit.params,
                [fit.bse["x1"], fit.tvalues["x1"], fit.pvalues["x1"]],
                fit.resid,
            ]
        )
        index = ["intercept", "slope", "SE_slope", "t", "pvalue_raw"] + [
            "e_{}".format(t) for t in timepoints
        ]
        return pd.Series(data=values, index=index)

    def calc_log_ratios(self, label):
        """
        Calculate the log ratios that will be fit using the linear models.
        """
        if self.store_check("/main/{}/log_ratios".format(label)):
            return

        logging.info(
            "Calculating log ratios ({})".format(label), extra={"oname": self.name}
        )
        ratios = self.store_select("/main/{}/counts".format(label))
        index = ratios.index
        c_n = ["c_{}".format(x) for x in self.store_timepoints()]
        ratios = np.log(ratios + 0.5)

        # perform operations on the numpy values of the data
        # frame for easier broadcasting
        ratios = ratios[c_n].values
        if self.logr_method == "wt":
            if "variants" in self.store_labels():
                wt_label = "variants"
            elif "identifiers" in self.store_labels():
                wt_label = "identifiers"
            else:
                raise ValueError(
                    "Failed to use wild type log ratio method, "
                    "suitable data table not "
                    "present [{}]".format(self.name)
                )

            wt_counts = self.store_select(
                "/main/{}/counts".format(wt_label),
                "columns={} & index=='{}'".format(c_n, WILD_TYPE_VARIANT),
            )

            if len(wt_counts) == 0:  # wild type not found
                raise ValueError(
                    "Failed to use wild type log ratio method, "
                    "wild type sequence not "
                    "present [{}]".format(self.name)
                )
            ratios = ratios - np.log(wt_counts.values + 0.5)

        elif self.logr_method == "complete":
            ratios = ratios - np.log(
                self.store_select(
                    "/main/{}/counts".format(label), "columns={}".format(c_n)
                )
                .sum(axis="index")
                .values
                + 0.5
            )
        elif self.logr_method == "full":
            ratios = ratios - np.log(
                self.store_select(
                    "/main/{}/counts_unfiltered".format(label), "columns={}".format(c_n)
                )
                .sum(axis="index", skipna=True)
                .values
                + 0.5
            )
        else:
            raise ValueError(
                'Invalid log ratio method "{}" [{}]'.format(self.logr_method, self.name)
            )

        # make it a data frame again
        columns = ["L_{}".format(x) for x in self.store_timepoints()]
        ratios = pd.DataFrame(data=ratios, index=index, columns=columns)
        self.store_put(
            key="/main/{}/log_ratios".format(label),
            value=ratios,
            columns=ratios.columns,
            format="table",
        )

    def calc_weights(self, label):
        """
        Calculate the regression weights (1 / variance).
        """
        if self.store_check("/main/{}/weights".format(label)):
            return

        logging.info(
            "Calculating regression weights ({})".format(label),
            extra={"oname": self.name},
        )
        variances = self.store_select("/main/{}/counts".format(label))
        c_n = ["c_{}".format(x) for x in self.store_timepoints()]
        index = variances.index

        # perform operations on the numpy values of the
        # data frame for easier broadcasting
        # var_left = 1.0 / (variances[c_n].values + 0.5)
        # var_right = 1.0 / (variances[['c_0']].values + 0.5)
        # variances = var_left + var_right
        variances = 1.0 / (variances[c_n].values + 0.5)

        # -------------------------- WT NORM ----------------------------- #
        if self.logr_method == "wt":
            if "variants" in self.store_labels():
                wt_label = "variants"
            elif "identifiers" in self.store_labels():
                wt_label = "identifiers"
            else:
                raise ValueError(
                    "Failed to use wild type log ratio method, "
                    "suitable data table not present [{}]".format(self.name)
                )
            wt_counts = self.store_select(
                key="/main/{}/counts".format(wt_label),
                where="columns={} & index='{}'".format(c_n, WILD_TYPE_VARIANT),
            )

            # wild type not found
            if len(wt_counts) == 0:
                raise ValueError(
                    "Failed to use wild type log ratio method, wild type "
                    "sequence not present [{}]".format(self.name)
                )
            variances = variances + 1.0 / (wt_counts.values + 0.5)

        # ---------------------- COMPLETE NORM ----------------------------- #
        elif self.logr_method == "complete":
            variances = variances + 1.0 / (
                self.store_select(
                    key="/main/{}/counts".format(label), where="columns={}".format(c_n)
                )
                .sum(axis="index")
                .values
                + 0.5
            )

        # ------------------------- FULL NORM ----------------------------- #
        elif self.logr_method == "full":
            variances = variances + 1.0 / (
                self.store_select(
                    key="/main/{}/counts_unfiltered".format(label),
                    where="columns={}".format(c_n),
                )
                .sum(axis="index", skipna=True)
                .values
                + 0.5
            )

        # ---------------------------- WUT? ------------------------------- #
        else:
            raise ValueError(
                'Invalid log ratio method "{}" [{}]'.format(self.logr_method, self.name)
            )

        # weights are reciprocal of variances
        variances = 1.0 / variances

        # make it a data frame again
        variances = pd.DataFrame(
            data=variances,
            index=index,
            columns=["W_{}".format(x) for x in self.store_timepoints()],
        )
        self.store_put(
            key="/main/{}/weights".format(label),
            value=variances,
            columns=variances.columns,
            format="table",
        )

    def calc_regression(self, label):
        """
        Calculate least squares regression for *label*. If *weighted* is
        ``True``, calculates weighted least squares; else ordinary least
        squares.

        Regression results are stored in ``'/main/label/scores'``

        """
        req_tables = ["/main/{}/log_ratios".format(label)]
        if self.weighted:
            req_tables.append("/main/{}/weights".format(label))

        for req_table in req_tables:
            if not self.store_check(req_table):
                raise ValueError(
                    "Required table {} does not "
                    "exist [{}].".format(req_table, self.name)
                )

        if self.store_check("/main/{}/scores".format(label)):
            return
        elif "/main/{}/scores".format(label) in list(self.store_keys()):
            # need to remove the current keys because we are using append
            self.store_remove("/main/{}/scores".format(label))

        method = "WLS" if self.weighted else "OLS"
        logging.info(
            "Calculating {} regression coefficients ({})".format(method, label),
            extra={"oname": self.name},
        )

        longest = (
            self.store_select(
                key="/main/{}/log_ratios".format(label), where="columns='index'"
            )
            .index.map(len)
            .max()
        )
        chunk = 1

        # -------------------- REG COMPUTATION --------------------------- #
        selection = ["/main/{}/log_ratios".format(label)]
        if self.weighted:
            selection.append("/main/{}/weights".format(label))

        selection = self.store_select_as_multiple(
            selection, chunksize=self.store_default_chunksize()
        )

        for data in selection:
            logging.info(
                "Calculating {} for chunk {} ({} rows)".format(
                    method, chunk, len(data.index)
                ),
                extra={"oname": self.name},
            )
            result = data.apply(
                self.row_apply_function,
                axis="columns",
                args=[self.store_timepoints(), self.weighted],
            )
            # append is required because it takes the
            # "min_itemsize" argument, and put doesn't
            self.store_append(
                key="/main/{}/scores".format(label),
                value=result,
                min_itemsize={"index": longest},
            )
            chunk += 1

        # ----------------------- POST ------------------------------------ #
        # need to read from the file, calculate percentiles, and rewrite it
        logging.info(
            "Calculating slope standard error percentiles ({})".format(label),
            extra={"oname": self.name},
        )
        data = self.store_get("/main/{}/scores".format(label))
        data["score"] = data["slope"]
        data["SE"] = data["SE_slope"]
        data["SE_pctile"] = [
            stats.percentileofscore(data["SE"], x, "weak") for x in data["SE"]
        ]

        # reorder columns
        reorder_selector = [
            "score",
            "SE",
            "SE_pctile",
            "slope",
            "intercept",
            "SE_slope",
            "t",
            "pvalue_raw",
        ]
        data = data[reorder_selector]
        self.store_put(
            key="/main/{}/scores".format(label),
            value=data,
            columns=data.columns,
            format="table",
        )
