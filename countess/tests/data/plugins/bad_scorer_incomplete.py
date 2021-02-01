from countess.plugins.scoring import BaseScorerPlugin


class CountsScorer(BaseScorerPlugin):

    name = "Counts Only Incomplete"
    version = "1.0"
    author = "Alan Rubin, Daniel Esposito"

    def __init__(self, store_manager, options):
        super().__init__(store_manager, options)

    def computing_scores(self):
        return

    def row_apply_function(self, *args, **kwargs):
        return
