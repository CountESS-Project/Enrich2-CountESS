"""
Enrich2 plugin module
=====================

:py:mod:`~enrich2.plugins` is a module providing classes and methods
required to import modules, subclass a scoring plugin, define scripting options
and option configuration files.
"""


import os
import importlib

from .options import Options, OptionsFile


__all__ = ["ModuleLoader", "load_scorer_class_and_options", "implements_methods"]


class ModuleLoader(object):
    """
    A generic class for importing functions and classes from external
    python code.
    
    The purpose of this class is to do all the heavy lifting when loading
    a python class from source, and to throw appropriate errors upon
    unexpected behaviour.
    
    Parameters
    ----------
    path : str
        The path pointing to the python file to be imported.
        
    Methods
    -------
    get_module_attrs
        Returns items from the ``__dict__`` attribute of the imported file  
    get_attr_from_module
        Returns a specified attribute from the imported module if it exists.
        
    Raises
    ------
    TypeError
        Raises a ``TypeError`` if *path* is not a string.
    IOError
        Raises ``IOError`` upon failure to locate file or open a file handle.
    ImportError
        Raises an ``ImportError`` if the module could not be loaded by
        :py:mod:`importlib` or if the file is not a correct python file.
    AttributeError
        Raises ``AttributeError`` if a non-existent attribute is requested.
    """

    def __init__(self, path):
        if not isinstance(path, str):
            raise TypeError("Argument `path` needs to be a string.")
        if not os.path.exists(path):
            raise IOError("Invalid plugin path {}.".format(path))

        path = os.path.join(path, "")[:-1]
        path_to_module_folder = "/".join(path.split("/")[:-1])
        module_folder = path_to_module_folder.split("/")[-1]
        module_name, ext = os.path.splitext(path.split("/")[-1])
        if ext != ".py":
            raise IOError("Plugin must be a python file.")

        try:
            spec = importlib.util.spec_from_file_location("module.name", path)
            self.module = importlib.util.module_from_spec(spec)
            self.module_name = module_name
            self.module_folder = module_folder
            spec.loader.exec_module(self.module)
        except BaseException as err:
            raise ImportError(err)

    def get_module_attrs(self):
        """
        Return the dictionary items of the loaded module.
        
        Returns
        -------
        `dict`
        """
        return self.module.__dict__.items()

    def get_attr_from_module(self, name):
        """
        Returns the object attribute at key *name* using :py:func:`getattr`.
        
        Parameters
        ----------
        name : str  
            String name of the attribute

        Returns
        -------
        `object`
            Returns the object under the *name* key.
        """
        if not hasattr(self.module, name):
            raise AttributeError(
                "Module {} does not have attribute "
                "{}.".format(self.module_name, name)
            )
        return getattr(self.module, name)


def load_scorer_class_and_options(path):
    """
    A utility function to import an ``Enrich2`` plugin 
    :py:class:`~enrich2.plugins.scoring.BaseScorerPlugin` class along with
    its associated :py:class:`~enrich2.plugins.options.Options` and 
    :py:class:`~enrich2.plugins.options.OptionsFile`
    
    Parameters
    ----------
    path : str
        Path pointing the to python file to import.

    Returns
    -------
    tuple
        Containing the class, Options and OptionsFile. The latter two may
        be ``None``.
        
    Raises
    ------
    ImportError
        Raises an ``ImportError`` if more/less than one scorer class is found,
        more than one ``Options`` class is found or an empty ``Options`` 
        instantiation is found.
    """
    loader = ModuleLoader(path)
    scorers = []
    for attr_name, attr in loader.get_module_attrs():
        if implements_methods(attr):
            scorers.append(attr)
    if len(scorers) < 1:
        raise ImportError(
            "Could not find any classes implementing "
            "the required BaseScorerPlugin interface."
        )
    if len(scorers) > 1:
        raise ImportError(
            "Found Multiple classes implementing "
            "the required BaseScorerPlugin interface."
        )

    options_ = None
    options_file = None
    for attr_name, attr in loader.get_module_attrs():
        if isinstance(attr, Options):
            if options_ is not None:
                raise ImportError(
                    "Two Options classes found. Expecting only" "one instantiation."
                )
            if not attr.has_options():
                raise ImportError("Options class must contain options.")
            options_ = attr

    if options_ is not None and options_.has_options():
        options_file = OptionsFile.default_json_options_file()

    scorer_class = scorers[-1]
    if options_ is None:
        options_ = Options()

    return scorer_class, options_, options_file


def implements_methods(class_):
    """
    Utility function that checks a class to see if it is a correctly 
    implemented :py:class:`~enrich2.plugins.scoring.BaseScorerPlugin` subclass.
    
    Parameters
    ----------
    class_ : object
        The class to check.

    Returns
    -------
    bool
        True if it implements the Abstract plugin class. False otherwise.
    """
    if not hasattr(class_, "_base_name"):
        return False
    if not getattr(class_, "_base_name") == "BaseScorerPlugin":
        return False
    if not hasattr(class_, "compute_scores"):
        return False
    if hasattr(getattr(class_, "compute_scores"), "__isabstractmethod__"):
        return False
    return True
