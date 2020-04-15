from enrich2.plugins.scoring import BaseScorerPlugin


class CountsScorer(BaseScorerPlugin):

    name = "Counts Only"
    version = "1.0"
    author = "Alan Rubin, Daniel Esposito"

    def compute_scores(self):
        return
