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
from .scoring import BaseScorerPlugin
from .options import ScoringOptions
from ..base.constants import WILD_TYPE_VARIANT


options = ScoringOptions()
options.add_option(
    name="Normalization Method",
    varname="logr_method",
    dtype=str,
    default='wt',
    choices=['wt', 'full', 'complete'],
    tooltip="Method used to normalise count data in the ratios."
)


class RatiosScorer(BaseScorerPlugin):

    def __init__(self, store_manager, options):
        super().__init__(store_manager, options)

    def compute_scores(self):
        for label in self.store_labels():
            self.calc_ratios(label)

    def row_apply_function(self, *args, **kwargs):
        pass

    def calc_ratios(self, label):
        """
        Calculate frequency ratios and standard errors between the
        last timepoint and the input. Ratios can be calculated using
        one of three methods:
            - wt
            - complete
            - full
        """
        if self.store_check("/main/{}/scores".format(label)):
            return

        logging.info(
            "Calculating ratios ({})".format(label),
            extra={'oname' : self.name}
        )
        c_last = 'c_{}'.format(self.store_timepoints()[-1])
        df = self.store_select(
            "/main/{}/counts".format(label),
            "columns in ['c_0', {}]".format(c_last)
        )

        if self.logr_method == "wt":
            if "variants" in self.store_labels():
                wt_label = "variants"
            elif "identifiers" in self.store_labels():
                wt_label = "identifiers"
            else:
                raise ValueError('Failed to use wild type log '
                                 'ratio method, suitable data '
                                 'table not present [{}]'.format(self.name))

            shared_counts = self.store_select(
                "/main/{}/counts".format(wt_label),
                "columns in ['c_0', {}] & index='{}'".format(
                    c_last, WILD_TYPE_VARIANT))

            # wild type not found
            if len(shared_counts) == 0:
                raise ValueError('Failed to use wild type log '
                                 'ratio method, wild type '
                                 'sequence not present [{}]'.format(self.name))

            shared_counts = shared_counts.values + 0.5

        elif self.logr_method == "complete":
            shared_counts = self.store_select(
                "/main/{}/counts".format(label),
                "columns in ['c_0', {}]".format(c_last)
            ).sum(axis="index").values + 0.5

        elif self.logr_method == "full":
            shared_counts = self.store_select(
                "/main/{}/counts_unfiltered".format(label),
                "columns in ['c_0', {}]".format(c_last)
            ).sum(axis="index", skipna=True).values + 0.5
        else:
            raise ValueError('Invalid log ratio method "{}" '
                             '[{}]'.format(self.logr_method, self.name))

        ratios = np.log(df[['c_0', c_last]].values + 0.5) - \
                 np.log(shared_counts)
        ratios = ratios[:, 1] - ratios[:, 0]    # selected - input
        ratios = pd.DataFrame(ratios, index=df.index, columns=['logratio'])

        shared_variance = np.sum(1. / shared_counts)
        summed = np.sum(1. / (df[['c_0', c_last]].values + 0.5), axis=1)

        ratios['variance'] = summed + shared_variance
        ratios['score'] = ratios['logratio']
        ratios['SE'] = np.sqrt(ratios['variance'])

        # re-order columns
        ratios = ratios[['score', 'SE', 'logratio', 'variance']]
        self.store_put(
            key="/main/{}/scores".format(label),
            value=ratios,
            format="table",
            data_columns=ratios.columns
        )