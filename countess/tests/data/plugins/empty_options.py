from countess.plugins.scoring import BaseScorerPlugin
from countess.plugins.options import Options


options_1 = Options()


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
