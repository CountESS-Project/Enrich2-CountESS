"""
Enrich2 plugin option module
============================

:py:mod:`~enrich2.options` is a module providing classes and methods
required for defining Option objects for use by plugin authors. It provides 
additional container classes Options to define a collection of options with
associated utility methods. The OptionsFile class defines a representation
of an Enrich2 options configuration. Several utility functions are provided
for basic operations over an Options object.
"""


import json
import yaml
from collections.abc import Mapping

from ..base.config_constants import SCORER, SCORER_OPTIONS


__all__ = [
    "BaseOption",
    "Option",
    "BaseOptions",
    "Options",
    "OptionsFile",
    "parse",
    "validate",
    "get_unused_options",
    "get_unused_options_ls",
    "option_names_not_in_cfg",
    "option_varnames_not_in_cfg",
    "options_not_in_config",
    "apply_cfg_to_options",
]


# -------------------------------------------------------------------------- #
#                           Option Types
# -------------------------------------------------------------------------- #
class BaseOption(object):
    """
    This class represents the base of an Option, containing all
    common attributes and methods.
    
    Parameters
    ----------
    name : str 
        GUI name of the option.
    varname : str
        Variable name used by the script it is defined in.
    dtype : 
        Data-type of the option value.
    default : ``dtype``
        Default value option assumes upon instantiation.
    hidden : bool
        Inidcate if the option should be rendered by the GUI.
        
    Methods
    -------
    _validate
        Must be called by the subclass to validate the base attributes.
    _set_value
        Must be called bu the subclass to set the base attributes.
    get_value
        Returns the value of an option.
    get_default_value
        Returns the default value of an option.
    visible
        Returns a boolean indicating if the option is rendered by the GUI.
        
    See Also
    --------
    :py:class:`~enrich2.plugins.options.Option`
    """

    def __init__(self, name, varname, dtype, default, hidden):
        if not isinstance(name, str):
            raise TypeError(
                "Parameter 'name' in option '{}' must be a " "string.".format(name)
            )
        if not isinstance(varname, str):
            raise TypeError(
                "Parameter 'varname' in option '{}' must be a " "string.".format(name)
            )
        if not isinstance(hidden, bool):
            raise TypeError(
                "Parameter 'hidden' in option '{}' must be a " "boolean.".format(name)
            )

        if not name:
            raise ValueError(
                "Parameter 'name' in option '{}' must be a "
                "non-empty string.".format(name)
            )
        if not varname:
            raise ValueError(
                "Parameter 'varname' in option '{}' must be a "
                "non-empty string.".format(name)
            )
        if dtype is None:
            raise TypeError(
                "Parameter 'dtype' in option '{}' cannot be " "NoneType.".format(name)
            )

        self.name = name
        self.varname = varname
        self.dtype = dtype
        self.hidden = hidden

        self._validate(default)
        self._default = default
        self._value = default

    def __eq__(self, other):
        name_eq = self.name == other.name
        varname_eq = self.varname == other.varname
        dtype_eq = self.dtype == other.dtype
        hidden_eq = self.hidden == other.hidden
        default_eq = self.get_default_value() == other.get_default_value()
        value_eq = self.get_value() == other.get_value()
        return (
            name_eq
            and varname_eq
            and dtype_eq
            and hidden_eq
            and default_eq
            and value_eq
        )

    def __ne__(self, other):
        return not self == other

    def _validate(self, value):
        """
        Validate a potential value that will be set as in the config for this
        option.

        Parameters
        ----------
        value : 
            A value that must match the dtype attribute.
        """
        if not isinstance(value, self.dtype):
            raise TypeError(
                "Option '{}' with type {} does not match "
                "input type {}.".format(
                    self.varname, self.dtype.__name__, type(value).__name__
                )
            )

    def _set_value(self, value):
        """
        Set the value of an option.
        
        Parameters
        ----------
        value : 
            A value that must match the dtype attribute.
        """
        self._validate(value)
        self._value = value

    def get_value(self):
        """
        Gets the current value of the option.
        """
        return self._value

    def get_default_value(self):
        """
        Gets the default value of the option.
        """
        return self._default

    def visible(self):
        """
        Returns a ``bool`` indicating if the option is visible in the GUI.
        """
        return not self.hidden


class Option(BaseOption):
    """
    Utility class to represent a user defined option. Mainly used by the 
    GUI to render to a dialogue box.
    
    Parameters
    ----------
    name : `str` 
        GUI name of the option.
    varname : `str`
        Variable name used by the script it is defined in.
    dtype : 
        Data-type of the option value.
    default : ``dtype``
        Default value option assumes upon instantiation.
    hidden : bool
        Inidcate if the option should be rendered by the GUI.
    choices : `dict`
        A key-value map representing values with a predefined set of
        allowable values. The key should a nice/readable string used 
        in the GUI.
        
    Methods
    -------
    keytransform
        Transforms a key that appears in choices values into its corresponding
        key. Throws ValueError if value is neither a key or value.
    validate
        Validate a potential value that will be set as in the config for this
        option.
    get_value
        Returns the value of this option. If this option has choices
        then it will return the current value selected in *choices*.
    set_value
        Set the value of this option. Should also make a call to the 
        inherited classes _validate function.
    get_choice_key
        The choice key is the current selected key in the *choices* attribute.
        This method get the choice key that is currently selected.
    set_choice_key
        The choice key is the current selected key in the *choices* attribute.
        This method sets the choice key. *key* must be either a valid
        value in *choices* or a valid key in *choices*.
    get_default_value
        Return default value of this option. If this option has choices
        then it will return the current value selected in *choices*.
    is_default
        Returns a bool if the current value is the default
    
    See Also
    --------
    :py:class:`~enrich2.plugins.options.BaseOption`
    
    """

    def __init__(self, name, varname, dtype, default, choices=None, hidden=True):
        """

        """
        super(Option, self).__init__(name, varname, dtype, default, hidden)
        self.choices = {} if choices is None else choices
        self._rev_choices = {} if choices is None else choices
        if not isinstance(self.choices, dict):
            raise TypeError(
                "Parameter 'choices' in option '{}' must be a "
                "dict.".format(self.name)
            )

        for key in self.choices.keys():
            if not isinstance(key, str):
                raise TypeError("Choice keys must be strings.")

        for value in self.choices.values():
            if not isinstance(value, dtype):
                raise TypeError("Choice values must be {}.".format(dtype.__name__))

        self._rev_choices = {v: k for (k, v) in self.choices.items()}
        if len(self._rev_choices) != len(self.choices):
            raise ValueError("Non unique values found in choices.")

        self._choice_key = None

        if self.choices:
            self.set_choice_key(default)
            self._default = self.choices[self._choice_key]
            self._value = self.choices[self._choice_key]

        if self.choices:
            assert self._choice_key is not None

        self.validate(self._default)

    def __eq__(self, other):
        name_eq = self.name == other.name
        varname_eq = self.varname == other.varname
        dtype_eq = self.dtype == other.dtype
        hidden_eq = self.hidden == other.hidden
        default_eq = self.get_default_value() == other.get_default_value()
        value_eq = self.get_value() == other.get_value()
        choices_eq = self.choices == other.choices
        rev_choices_eq = self._rev_choices == other._rev_choices
        choice_key_eq = self.get_choice_key() == other.get_choice_key()
        return (
            name_eq
            and varname_eq
            and dtype_eq
            and hidden_eq
            and default_eq
            and value_eq
            and choices_eq
            and choice_key_eq
            and rev_choices_eq
        )

    def __ne__(self, other):
        return not self == other

    def keytransform(self, value):
        """
        Transforms a key that appears in choices values into its corresponding
        key. Throws ValueError if value is neither a key or value.

        Parameters
        ----------
        value : str
            A string value appearing in either the keys of choices or the 
            values of choices.

        Returns
        -------
        str
            The key value of a choice.
        """

        if self.choices:
            if value in self._rev_choices:
                super()._validate(value)
                return self._rev_choices[value]
            elif value in self.choices:
                return value
            else:
                raise ValueError(
                    "Trying to set 'choices' with an undefined "
                    "value '{}'.".format(value)
                )
        else:
            super()._validate(value)
            return value

    def validate(self, value):
        """
        Validate a potential value that will be set as in the config for this
        option.

        Parameters
        ----------
        value : 
            A value that must match the dtype attribute.
        """
        super()._validate(value)
        if self.choices:
            self.keytransform(value)
        return self

    def set_value(self, value):
        """
        Set the value of this option. Should also make a call to the 
        inherited classes _validate function.
        
        Parameters
        ----------
        value : 
            Set the value of this option, which must match the *dtype* of
            the option.
        """
        self.validate(value)
        if self.choices:
            self.set_choice_key(value)
            value = self.choices[self._choice_key]
        super()._set_value(value)
        return self

    def get_value(self):
        """
        Returns the value of this option. If this option has choices
        then it will return the current value selected in *choices*.
        """
        if self.choices:
            return self.choices[self._choice_key]
        return self._value

    def set_choice_key(self, key):
        """
        The choice key is the current selected key in the *choices* attribute.
        This method sets the choice key. *key* must be either a valid
        value in *choices* or a valid key in *choices*.

        Parameters
        ----------
        key : `str`
            Value to set the choice key to.
        """
        if self.choices:
            key = self.keytransform(key)
            self._choice_key = key
        return self

    def get_choice_key(self):
        """
        The choice key is the current selected key in the *choices* attribute.
        This method get the choice key that is currently selected.

        Returns
        -------
        Currently selected key in the *choices* attribute.
        """
        if not self.choices:
            return self._choice_key
        return self.keytransform(self._choice_key)

    def get_default_value(self):
        """
        Return default value of this option. If this option has choices
        then it will return the current value selected in *choices*.
        """
        if self.choices:
            key = self.keytransform(self._default)
            return self.choices[key]
        return self._default

    def is_default(self):
        """
        Returns a bool if the current value is the default
        """
        return self.get_value() == self.get_default_value()


# -------------------------------------------------------------------------- #
#                           Option containers
# -------------------------------------------------------------------------- #
class BaseOptions(Mapping):
    """
    A :py:class:`collections.Mapping` subclass representing the mapping
    of option *varname* to corresponding 
    :py:class:`~enrich2.plugins.options.Option` objects.
        
    Methods
    -------
    put
        Insert a varname: option item into the mapping.
    to_dict
        Builds a new mapping of :py:class:`~enrich2.plugins.options.Option` 
        *varname* to *value* key-value pairs.
    has_options
        Indicates if the instance is currently populated with any options.
    option_varnames
        Returns a KeysView of the object
    option_names
        Returns a list of option names.
    set_option_by_varname
        Set an option by its *varname*
    get_option_by_varname
        Get an option by its *varname*
    validate_option_by_varname
        Validate an option by its *varname*
    get_visible_options
        Return a `list` of :py:class:`~enrich2.plugins.options.Option` that
        are not hidden.
    get_hidden_options
        Return a `list` of :py:class:`~enrich2.plugins.options.Option` that
        are hidden.
    to_dict_with_default_indicator
        Builds a new mapping of :py:class:`~enrich2.plugins.options.Option` 
        *varname* to tuple key-value pairs. Tuple is a (*value*, bool)
        to indicate if the value is the same as the specified default.
    
    See Also
    --------
    :py:class:`Mapping`
    
    """

    def __init__(self):
        self._options = dict()

    def __iter__(self):
        return iter(self._options)

    def __getitem__(self, key):
        return self._options[key]

    def __len__(self):
        return len(self._options)

    def __bool__(self):
        return bool(self._options)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        self_opts = sorted([o for o in self.values()], key=lambda x: x.varname)
        other_opts = sorted([o for o in other.values()], key=lambda x: x.varname)
        return all([o1 == o2 for (o1, o2) in zip(self_opts, other_opts)])

    def __ne__(self, other):
        return not self == other

    def to_dict(self):
        """
        Builds a new mapping of :py:class:`~enrich2.plugins.options.Option` 
        *varname* to *value* key-value pairs.
        
        Returns
        -------
        dict
        """
        return {k: o.get_value() for (k, o) in self._options.items()}

    def to_dict_with_default_indicator(self):
        """
        Builds a new mapping of :py:class:`~enrich2.plugins.options.Option` 
        *varname* to tuple key-value pairs. Tuple is a (*value*, bool)
        to indicate if the value is the same as the specified default.

        Returns
        -------
        dict
        """
        return {k: (o.get_value(), o.is_default()) for (k, o) in self._options.items()}

    def has_options(self):
        """
        Indicates if the instance is currently populated with any options.
        
        Returns
        -------
        bool
        """
        return bool(self)

    def option_varnames(self):
        """
        Returns a KeysView of the object
        """
        return list(self._options.keys())

    def option_names(self):
        """
        Returns a list of option names.
        """
        return [o.name for o in self._options.values()]

    def set_option_by_varname(self, varname, value):
        """
        Set an option by its *varname*
        
        Parameters
        ----------
        varname : str
            Varname of the option to set.
        value : 
            Value to set option with.
        """
        if varname not in self._options:
            raise KeyError(
                "Key '{}' not found in {}.".format(varname, self.__class__.__name__)
            )
        self._options[varname].set_value(value)

    def validate_option_by_varname(self, varname, value):
        """
        Validate an option by its *varname*

        Parameters
        ----------
        varname : str
            Varname of the option to be validated.
        value : 
            Value to validate option with.
        """
        if varname not in self._options:
            raise KeyError(
                "Key '{}' not found in {}.".format(varname, self.__class__.__name__)
            )
        self._options[varname].validate(value)

    def get_option_by_varname(self, varname):
        """
        Get an option by its *varname*

        Parameters
        ----------
        varname : str
            Varname of the option to be validated.
        """
        if varname not in self._options:
            raise KeyError(
                "Key '{}' not found in {}.".format(varname, self.__class__.__name__)
            )
        return self._options[varname]

    def put(self, varname, option):
        """
        Insert a varname: option item into the mapping.

        Parameters
        ----------
        varname : str
            Varname of the option to be validated.
        option: :py:class:`~enrich2.plugins.options.Option`
            Option to insert.
            
        Raises
        ------
        ValueError
            If trying to insert a key that already exists.
        """
        if varname in set(self._options.keys()):
            raise ValueError(
                "Cannot define two options with the same "
                "varname '{}'.".format(varname)
            )
        self._options[varname] = option

    def get_visible_options(self):
        """
        Return a `list` of :py:class:`~enrich2.plugins.options.Option` that
        are not hidden.
        """
        return [o for o in self._options.values() if o.visible()]

    def get_hidden_options(self):
        """
        Return a `list` of :py:class:`~enrich2.plugins.options.Option` that
        are hidden.
        """
        return [o for o in self._options.values() if not o.visible()]


class Options(BaseOptions):
    """
    Utility class that is to be used by a plugin developer to add options
    to their scoring script. Subclasses 
    :py:class:`~enrich2.plugins.options.BaseOptions`
    
    Methods
    -------
    add_option
        Adds an option.
    
    See Also
    --------
    :py:class:`~enrich2.plugins.options.BaseOptions`
    """

    def __init__(self):
        super().__init__()

    def add_option(self, name, varname, dtype, default, choices=None, hidden=True):
        """
        Adds an option.

        Parameters
        ----------
        name : str 
            GUI name of the option.
        varname : str
            Variable name used by the script it is defined in.
        dtype : 
            Data-type of the option value.
        default : ``dtype``
            Default value option assumes upon instantiation.
        hidden : bool
            Inidcate if the option should be rendered by the GUI.
        choices : `dict`
            A key-value map representing values with a predefined set of
            allowable values. The key should a nice/readable string used 
            in the GUI.
        """
        option = Option(
            name=name,
            varname=varname,
            dtype=dtype,
            default=default,
            choices=choices,
            hidden=hidden,
        )
        self.put(varname, option)


# -------------------------------------------------------------------------- #
#                       Utility parse/validate methods
# -------------------------------------------------------------------------- #
def parse(file_path, backend=json):
    """
    Parses a configuration file into an options `dict`. File must be a 
    json/yaml file with keys 'scorer' and 'scorer options'.
    
    Parameters
    ----------
    file_path : str
        Path pointing to the configuration file to be parsed.
    backend : Default :py:mod:`json`
        Backend to be used to parse file.

    Returns
    -------
    dict
    """
    if isinstance(file_path, str):
        cfg = backend.load(open(file_path, "r"))
    else:
        cfg = backend.load(file_path)

    if SCORER in cfg:
        if SCORER_OPTIONS in cfg[SCORER]:
            return cfg[SCORER][SCORER_OPTIONS]
        else:
            raise ValueError(
                "Unrecognised config file, couldn't find "
                "expected keys. File requires the nested key"
                "'{}/{}'.".format(SCORER, SCORER_OPTIONS)
            )
    elif SCORER_OPTIONS in cfg:
        return cfg[SCORER_OPTIONS]
    else:
        raise ValueError(
            "Unrecognised config file, couldn't find "
            "expected keys. File requires the nested key"
            "'{}/{}' or the key "
            "'{}'".format(SCORER, SCORER_OPTIONS, SCORER_OPTIONS)
        )


def validate(cfg_dict):
    """
    Validates that *cfg_dict* is a valid dictionary.

    Parameters
    ----------
    cfg_dict : dict
       Dictionary to validate

    Returns
    -------
    dict
    """
    if not isinstance(cfg_dict, dict):
        raise TypeError(
            "Expected parsed configuration to be type 'dict'"
            " Found {}.".format(type(cfg_dict).__name__)
        )


# -------------------------------------------------------------------------- #
#                           Options File Object
# -------------------------------------------------------------------------- #
class OptionsFile(object):
    """
    Utility class to represent a configuration file and it's associated parsing
    and validation funcitons.
    
            
    Parameters
    ----------
    name : str
        Descriptive name of the file to be rendered in the GUI.
    parsing_func : Callable
        Function to parse file with.
    parsing_func_kwargs : dict
        Keyword arguments required by ``parsing_func``.
    validator_func : Callable
        Function to validate parsing output.
    validator_func_kwargs : dict
        Keyword arguments required by ``validator_func``.
    
    Methods
    -------
    parse_to_dict
        Parse a configuration file into an options attributes dictionary
        with *varname* : *vale* pairs required by a plugin.
    validate_cfg
        Validate a parsed config.
    """

    @staticmethod
    def default_json_options_file(name="Options File"):
        """
        Returns a default ``json`` 
        :py:class:`~enrich2.plugins.options.OptionsFile` for loading
        ``Enrich2`` config files.
        
        Parameters
        ----------
        name : str
            Descriptive name of the file to be rendered in the GUI.

        Returns
        -------
        :py:class:`~enrich2.plugins.options.OptionsFile`
        """
        options_file = OptionsFile(
            name=name,
            parsing_func=parse,
            parsing_func_kwargs={"backend": json},
            validator_func=validate,
            validator_func_kwargs={},
        )
        return options_file

    @staticmethod
    def default_yaml_options_file(name="Options File"):
        """
        Returns a default ``yaml`` 
        :py:class:`~enrich2.plugins.options.OptionsFile` for loading
        ``Enrich2`` config files.

        Parameters
        ----------
        name : str
            Descriptive name of the file to be rendered in the GUI.

        Returns
        -------
        :py:class:`~enrich2.plugins.options.OptionsFile`
        """
        options_file = OptionsFile(
            name=name,
            parsing_func=parse,
            parsing_func_kwargs={"backend": yaml},
            validator_func=validate,
            validator_func_kwargs={},
        )
        return options_file

    def __init__(
        self,
        name,
        parsing_func,
        parsing_func_kwargs,
        validator_func,
        validator_func_kwargs,
    ):
        self.name = name
        self._parser_func = parsing_func
        self.parse_kwargs = parsing_func_kwargs
        self._validator_func = validator_func
        self.valid_kwargs = validator_func_kwargs

        if not isinstance(self.parse_kwargs, dict):
            raise TypeError("Argument 'parser_kwargs' must be a dictionary.")

        if not isinstance(self.valid_kwargs, dict):
            raise TypeError("Argument 'valid_kwargs' must be a dictionary.")

    def parse_to_dict(self, file_path):
        """
        Parse a configuration file into an options attributes dictionary
        with *varname* : *vale* pairs required by a plugin.
        
        Parameters
        ----------
        file_path : str
            Path pointing to the file to parse.

        Returns
        -------
        dict
        """
        return self._parser_func(file_path, **self.parse_kwargs)

    def validate_cfg(self, cfg):
        """
        Validate a parsed config.
        
        Parameters
        ----------
        cfg : dict
            The attribute dictionary to validate.
        """
        self._validator_func(cfg, **self.valid_kwargs)


# -------------------------------------------------------------------------- #
#                           Utility methods
# -------------------------------------------------------------------------- #
def get_unused_options(cfg_dict, options):
    """
    Returns the unused keys in a configuration dictionary. An unused key
    is a key that is not seen in *options*.
    
    Parameters
    ----------
    cfg_dict : dict
    options : :py:class:`~enrich2.plugins.options.Options`

    Returns
    -------
    `set`
        Set of unused keys.
    """
    unused = set()
    option_keys = set(options.keys())
    for key in cfg_dict.keys():
        if key not in option_keys:
            unused.add(key)
    return unused


def get_unused_options_ls(cfg_dict, options_ls):
    """
    Returns the unused keys in a configuration dictionary. An unused key
    is a key that is not seen in any *options_ls* item.

    Parameters
    ----------
    cfg_dict : dict
    options_ls : list
        list of :py:class:`~enrich2.plugins.options.Options` objects.

    Returns
    -------
    `set`
        Set of unused keys.
    """
    unused = set()
    option_keys = set([k for opts in options_ls for k in opts])
    for key in cfg_dict.keys():
        if key not in option_keys:
            unused.add(key)
    return unused


def options_not_in_config(cfg, options):
    """
    Returns a list of :py:class:`~enrich2.plugins.options.Options` objects
    with keys in *options* not seen in the *cfg* dictionary, typically
    parsed from an external configuration file.

    Parameters
    ----------
    cfg : dict
    options : :py:class:`~enrich2.plugins.options.Options`

    Returns
    -------
    `list`
        List of :py:class:`~enrich2.plugins.options.Options`
    """
    missing = []
    for varname, option in options.items():
        if varname not in cfg:
            missing.append(option)
    return missing


def option_varnames_not_in_cfg(cfg, options):
    """
    Returns keys in *options* not seen in the *cfg* dictionary, typically
    parsed from an external configuration file.

    Parameters
    ----------
    cfg : dict
    options : :py:class:`~enrich2.plugins.options.Options`

    Returns
    -------
    `list`
        Subset of keys from :py:class:`~enrich2.plugins.options.Options`
    """
    return [opt.varname for opt in options_not_in_config(cfg, options)]


def option_names_not_in_cfg(cfg, options):
    """
    Returns names of *options* not seen in the *cfg* dictionary, typically
    parsed from an external configuration file.

    Parameters
    ----------
    cfg : dict
    options : :py:class:`~enrich2.plugins.options.Options`

    Returns
    -------
    `list`
        List of names from :py:class:`~enrich2.plugins.options.Option` objects.
    """
    return [opt.name for opt in options_not_in_config(cfg, options)]


def apply_cfg_to_options(cfg, options):
    """
    Parses a cfg dictionary and sets the values of the corresponding 
    :py:class:`~enrich2.plugins.options.Option` in the mapping of
    :py:class:`~enrich2.plugins.options.Options` by *varname*
    
    Parameters
    ----------
    cfg : dict
    options : :py:class:`~enrich2.plugins.options.Options`
    """
    for key, value in cfg.items():
        if key in set(options.option_varnames()):
            options.set_option_by_varname(key, value)
