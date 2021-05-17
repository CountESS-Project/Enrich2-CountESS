from countess.plugins.scoring import BaseScorerPlugin
from countess.plugins.options import Options


options = Options()
options.add_option(
    name="Normalization Method",
    varname="logr_method",
    dtype=bool,
    default="Wild Type",
    choices={"Wild Type": "wt", "Full": "full", "Complete": "complete"},
    hidden=False,
)
options.add_option(
    name="Weighted",
    varname="logr_method",
    dtype=str,
    default=True,
    choices=None,
    hidden=False,
)


class CountsScorer(BaseScorerPlugin):

    name = "Counts Only"
    version = "1.0"
    author = "Alan Rubin, Daniel Esposito"

    def __init__(self, store_manager, options):
        super().__init__(store_manager, options)

    def compute_scores(self):
        return

    def row_apply_function(self, *args, **kwargs):
        return
