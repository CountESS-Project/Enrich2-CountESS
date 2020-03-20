from enrich2.plugins.scoring import BaseScorerPlugin
from enrich2.plugins.options import Options


# Options that will be rendered to the GUI for easy access
options = Options()
options.add_option(
    name="Normalization Method",
    varname="logr_method",
    dtype=str,
    default="Wild Type",
    choices={"Wild Type": "wt", "Full": "full", "Complete": "complete"},
    hidden=False,
)
options.add_option(
    name="Weighted",
    varname="weighted",
    dtype=bool,
    default=True,
    choices={},
    hidden=False,
)
options.add_option(
    name="Example String Input",
    varname="ex_string",
    dtype=str,
    default="Default String...",
    choices={},
    hidden=False,
)
options.add_option(
    name="Alpha", varname="alpha", dtype=int, default=0, choices={}, hidden=False
)
options.add_option(
    name="Beta", varname="beta", dtype=float, default=0.0, choices={}, hidden=False
)
options.add_option(
    name="Use threading",
    varname="threading",
    dtype=bool,
    default=False,
    choices={},
    hidden=False,
)

# Advanced options that are found in configuration files only
options.add_option(
    name="h_string",
    varname="h_string",
    dtype=str,
    default="This is a hidden string",
    choices={},
    hidden=True,
)
options.add_option(
    name="h_float", varname="h_float", dtype=float, default=6.0, choices={}, hidden=True
)
options.add_option(
    name="h_int", varname="h_int", dtype=int, default=5, choices={}, hidden=True
)
options.add_option(
    name="h_list",
    varname="h_list",
    dtype=list,
    default=[1, 2, 3, 4],
    choices={},
    hidden=True,
)


class DemoScorer(BaseScorerPlugin):

    name = "Demo"
    version = "1.0"
    author = "Alan Rubin, Daniel Esposito"

    def compute_scores(self):
        pass
