from enrich2.plugins.scoring import BaseScorerPlugin


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


class CountsScorerTwo(BaseScorerPlugin):

    name = "Counts Only"
    version = "1.0"
    author = "Alan Rubin, Daniel Esposito"

    def __init__(self, store_manager, options):
        super().__init__(store_manager, options)

    def compute_scores(self):
        return

    def row_apply_function(self, *args, **kwargs):
        return
