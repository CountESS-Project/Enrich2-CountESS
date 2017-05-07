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
from enrich2.plugins.scoring import BaseScorerPlugin


class SimpleScorer(BaseScorerPlugin):

    name = 'Ratios (Old Enrich)'
    version = '1.0'
    author = 'Alan Rubin, Daniel Esposito'

    def __init__(self, store_manager, options):
        super().__init__(store_manager, options)

    def compute_scores(self):
        for label in self.store_labels():
            self.calc_simple_ratios(label)

    def row_apply_function(self, *args, **kwargs):
        pass

    def calc_simple_ratios(self, label):
        """
        Calculate simplified (original Enrich) ratios scores.
        This method does not produce standard errors.
        """
        if self.store_check("/main/{}/scores".format(label)):
            return

        logging.info("Calculating simple ratios "
                     "({})".format(label), extra={'oname' : self.name})

        c_last = 'c_{}'.format(self.store_timepoints()[-1])
        df = self.store_select(
            "/main/{}/counts".format(label),
            "columns in ['c_0', {}]".format(c_last))

        # perform operations on the numpy values of the
        # dataframe for easier broadcasting
        num = df[c_last].values.astype("float") / df[c_last].sum(axis="index")
        denom = df['c_0'].values.astype("float") / df['c_0'].sum(axis="index")
        ratios =  num / denom

        # make it a data frame again
        ratios = pd.DataFrame(data=ratios, index=df.index, columns=['ratio'])
        ratios['score'] = np.log2(ratios['ratio'])
        ratios['SE'] = np.nan
        ratios = ratios[['score', 'SE', 'ratio']]   # re-order columns

        self.store_put(
            key="/main/{}/scores".format(label),
            value=ratios,
            format="table",
            data_columns=ratios.columns
        )