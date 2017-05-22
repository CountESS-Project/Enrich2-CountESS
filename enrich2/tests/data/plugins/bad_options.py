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


from enrich2.plugins.scoring import BaseScorerPlugin
from enrich2.plugins.options import Options

options = Options()
options.add_option(
    name="Normalization Method",
    varname="logr_method",
    dtype=bool,
    default='Wild Type',
    choices={'Wild Type': 'wt', 'Full': 'full', 'Complete': 'complete'},
    hidden=False
)
options.add_option(
    name="Weighted",
    varname="logr_method",
    dtype=str,
    default=True,
    choices=None,
    hidden=False
)


class CountsScorer(BaseScorerPlugin):

    name = 'Counts Only'
    version = '1.0'
    author = 'Alan Rubin, Daniel Esposito'

    def __init__(self, store_manager, options):
        super().__init__(store_manager, options)

    def compute_scores(self):
        return

    def row_apply_function(self, *args, **kwargs):
        return