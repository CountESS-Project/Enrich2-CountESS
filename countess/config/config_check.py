"""
Enrich2 config_check module
===========================

Functions for identifying the type of 
:py:class:`~enrich2.base.storemanager.StoreManager` derived object associated 
with a given configuration object (decoded from a JSON file as described `here
<https://docs.python.org/2/library/json.html>`_).

"""


from ..base.config_constants import CONDITIONS, SELECTIONS, LIBRARIES
from ..base.config_constants import FASTQ, IDENTIFIERS, BARCODES, VARIANTS
from ..base.config_constants import BARCODE_MAP_FILE, OVERLAP


__all__ = [
    "is_experiment",
    "is_condition",
    "is_selection",
    "is_seqlib",
    "seqlib_type",
    "element_type",
]


def is_experiment(cfg):
    """
    Check if the given configuration object specifies an 
    :py:class:`~enrich2.experiment.experiment.Experiment`.

    Parameters
    ----------
    cfg : dict 
        Decoded JSON object

    Returns
    -------
    bool
        True if `cfg` if specifies a 
        :py:class:`~enrich2.experiment.experiment.Experiment`, else False.

    """
    if CONDITIONS in list(cfg.keys()):
        return True
    else:
        return False


def is_condition(cfg):
    """
    Check if the given configuration object specifies a 
    :py:class:`~enrich2.expierment.condition.Condition`.

    Parameters
    ----------
    cfg : dict 
        Decoded JSON object

    Returns
    -------
    bool
        True if `cfg` if specifies a 
        :py:class:`~enrich2.experiment.condition.Condition`, else False.
    """
    if SELECTIONS in list(cfg.keys()):
        return True
    else:
        return False


def is_selection(cfg):
    """
    Check if the given configuration object specifies a 
    :py:class:`~enrich2.selection.selection.Selection`.

    Parameters
    ----------
    cfg : dict 
        Decoded JSON object

    Returns
    -------
    bool
        True if `cfg` if specifies a 
        :py:class:`~enrich2.selection.selection.Selection`, else False.
    """
    if LIBRARIES in list(cfg.keys()):
        return True
    else:
        return False


def is_seqlib(cfg):
    """
    Check if the given configuration object specifies a 
    :py:class:`enrich2.libraries.seqlib.SeqLib` derived object.

    Parameters
    ----------
    cfg : dict 
        Decoded JSON object

    Returns
    -------
    bool
        True if `cfg` if specifies a :py:class:`enrich2.libraries.seqlib.SeqLib` 
        derived object, else False.

    """
    keys = list(cfg.keys())
    if FASTQ in keys or IDENTIFIERS in keys:
        return True
    else:
        return False


def seqlib_type(cfg):
    """
    Get the type of :py:class:`enrich2.libraries.seqlib.SeqLib` derived object 
    specified by the configuration object.

    Parameters
    ----------
    cfg : dict 
        Decoded JSON object

    Returns
    -------
    str 
        The class name of the :py:class:`enrich2.libraries.seqlib.SeqLib`
        derived object specified by `cfg`.

    Raises
    ------
    ValueError
        If the class name cannot be determined.
    """
    if BARCODES in cfg:
        if BARCODE_MAP_FILE in cfg[BARCODES]:
            if VARIANTS in cfg and IDENTIFIERS in cfg:
                raise ValueError("Unable to determine SeqLib type.")
            elif VARIANTS in cfg:
                return "BcvSeqLib"
            elif IDENTIFIERS in cfg:
                return "BcidSeqLib"
            else:
                raise ValueError("Unable to determine SeqLib type.")
        else:
            return "BarcodeSeqLib"
    elif VARIANTS in cfg and OVERLAP in cfg:
        raise ValueError("OverlapSeqLib no longer supported.")
    elif VARIANTS in cfg:
        return "BasicSeqLib"
    elif IDENTIFIERS in cfg:
        return "IdOnlySeqLib"
    else:
        raise ValueError("Unable to determine SeqLib type for configuration " "object.")


def element_type(cfg):
    """
    Get the type of :py:class:`~enrich2.storemanager.StoreManager` derived 
    object specified by the configuration object.

    Parameters
    ----------
    cfg : dict 
        Decoded JSON object

    Returns
    -------
    str 
        Class name of the :py:class:`~enrich2.base.storemanager.StoreManager`
        derived object specified by `cfg`.

    Raises
    ------
    ValueError
        If the class name cannot be determined.
    """
    if is_experiment(cfg):
        return "Experiment"
    elif is_condition(cfg):
        return "Condition"
    elif is_selection(cfg):
        return "Selection"
    elif is_seqlib(cfg):
        return seqlib_type(cfg)
    else:
        raise ValueError("Unable to determine type for configuration object.")
