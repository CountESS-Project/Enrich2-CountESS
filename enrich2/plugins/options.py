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


import json
import yaml
from collections import Mapping


# -------------------------------------------------------------------------- #
#                           Option Types
# -------------------------------------------------------------------------- #
class BaseOption(object):

    def __init__(self, name, varname, dtype, default, hidden):
        if not isinstance(name, str):
            raise TypeError("Parameter 'name' in option '{}' must be a "
                            "string.".format(name))
        if not isinstance(varname, str):
            raise TypeError("Parameter 'varname' in option '{}' must be a "
                            "string.".format(name))
        if not isinstance(hidden, bool):
            raise TypeError("Parameter 'hidden' in option '{}' must be a "
                            "boolean.".format(name))

        if not name:
            raise ValueError("Parameter 'name' in option '{}' must be a "
                            "non-empty string.".format(name))
        if not varname:
            raise ValueError("Parameter 'varname' in option '{}' must be a "
                            "non-empty string.".format(name))
        if dtype is None:
            raise TypeError("Parameter 'dtype' in option '{}' cannot be "
                            "NoneType.".format(name))

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
        return name_eq and varname_eq and dtype_eq and hidden_eq and \
               default_eq and value_eq

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

        Returns
        -------
        rtype : None
        """
        if not isinstance(value, self.dtype):
            raise TypeError("Option '{}' with type {} does not match "
                            "input type {}.".format(self.varname,
                                                    self.dtype.__name__,
                                                    type(value).__name__))

    def _set_value(self, value):
        """
        
        Parameters
        ----------
        value : 

        Returns
        -------

        """
        self._validate(value)
        self._value = value

    def get_value(self):
        """
        
        Returns
        -------

        """
        return self._value

    def get_default_value(self):
        """

        Returns
        -------

        """
        return self._default

    def visible(self):
        return not self.hidden


class Option(BaseOption):
    """
    Utility class to represent a user defined option. Mainly used by the 
    GUI to render to a dialogue box.
    """

    def __init__(self, name, varname, dtype, default,
                 choices=None, hidden=True):
        """
        Option Constructor.

        Parameters
        ----------
        name : `str` like
        varname : `str` like
        dtype :
        default : 
        choices : `dict` or `Iterable` like
        """
        super(Option, self).__init__(name, varname, dtype, default, hidden)
        self.choices = {} if choices is None else choices
        self._rev_choices = {} if choices is None else choices
        if not isinstance(self.choices, dict):
            raise TypeError("Parameter 'choices' in option '{}' must be a "
                            "dict.".format(self.name))

        for key in self.choices.keys():
            if not isinstance(key, str):
                raise TypeError("Choice keys must be strings.")

        for value in self.choices.values():
            if not isinstance(value, dtype):
                raise TypeError("Choice values must be {}.".format(
                    dtype.__name__))

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
        return name_eq and varname_eq and dtype_eq and hidden_eq and \
               default_eq and value_eq and choices_eq and choice_key_eq and \
               rev_choices_eq

    def __ne__(self, other):
        return not self == other

    def keytransform(self, value):
        """
        Transforms a key that appears in choices values into its corresponding
        key. Throws ValueError if value is neither a key or value.

        Parameters
        ----------
        value : `str` like
            A string value appearing in either the keys of choices or the 
            values of choices.

        Returns
        -------
        rtype : `str` like
            The key value of a choice.
        """

        if self.choices:
            if value in self._rev_choices:
                super()._validate(value)
                return self._rev_choices[value]
            elif value in self.choices:
                return value
            else:
                raise ValueError("Trying to set 'choices' with an undefined "
                                 "value '{}'.".format(value))
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

        Returns
        -------
        rtype : None
        """
        super()._validate(value)
        if self.choices:
            self.keytransform(value)
        return self

    def set_value(self, value):
        """
        
        Parameters
        ----------
        value : 

        Returns
        -------

        """
        self.validate(value)
        if self.choices:
            self.set_choice_key(value)
            value = self.choices[self._choice_key]
        super()._set_value(value)
        return self

    def get_value(self):
        """

        Returns
        -------

        """
        if self.choices:
            return self.choices[self._choice_key]
        return self._value

    def set_choice_key(self, key):
        """

        Parameters
        ----------
        key : 

        Returns
        -------

        """
        key = self.keytransform(key)
        self._choice_key = key
        return self

    def get_choice_key(self):
        """

        Parameters
        ----------
        value : 

        Returns
        -------

        """
        if not self.choices:
            return self._choice_key
        return self.keytransform(self._choice_key)

    def get_default_value(self):
        """

        Returns
        -------

        """
        if self.choices:
            key = self.keytransform(self._default)
            return self.choices[key]
        return self._default


# -------------------------------------------------------------------------- #
#                           Option containers
# -------------------------------------------------------------------------- #
class BaseOptions(Mapping):

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
        self_opts = sorted(
            [o for o in self.values()],
            key=lambda x: x.varname
        )
        other_opts = sorted(
            [o for o in other.values()],
            key=lambda x: x.varname
        )
        return all([o1 == o2 for (o1, o2) in zip(self_opts, other_opts)])

    def __ne__(self, other):
        return not self == other

    def to_dict(self):
        return {k: o.get_value() for (k, o) in self._options.items()}

    def has_options(self):
        return bool(self)

    def option_varnames(self):
        return self._options.keys()

    def option_names(self):
        return [o.name for o in self._options.values()]

    def set_option_by_varname(self, varname, value):
        if varname not in self._options:
            raise KeyError("Key '{}' not found in {}.".format(
                varname, self.__class__.__name__))
        self._options[varname].set_value(value)

    def validate_option_by_varname(self, varname, value):
        if varname not in self._options:
            raise KeyError("Key '{}' not found in {}.".format(
                varname, self.__class__.__name__))
        self._options[varname].validate(value)

    def get_option_by_varname(self, varname):
        if varname not in self._options:
            raise KeyError("Key '{}' not found in {}.".format(
                varname, self.__class__.__name__))
        return self._options[varname]

    def put(self, varname, option):
        if varname in set(self._options.keys()):
            raise ValueError("Cannot define two options with the same "
                             "varname '{}'.".format(varname))
        self._options[varname] = option

    def get_visible_options(self):
        return [o for o in self._options.values() if o.visible()]

    def get_hidden_options(self):
        return [o for o in self._options.values() if not o.visible()]


class Options(BaseOptions):
    """
    Utility class that is to be used by a plugin developer to add options
    to their scoring script.
    """

    def __init__(self):
        """

        """
        super().__init__()

    def add_option(self, name, varname, dtype, default, choices=None,
                   hidden=True):
        """

        Parameters
        ----------
        name : 
        varname : 
        dtype : 
        default : 
        choices :
        hidden :

        Returns
        -------

        """
        option = Option(
            name=name,
            varname=varname,
            dtype=dtype,
            default=default,
            choices=choices,
            hidden=hidden
        )
        self.put(varname, option)


# -------------------------------------------------------------------------- #
#                       Utility parse/validate methods
# -------------------------------------------------------------------------- #
SCORER = 'scorer'
SCORER_PATH = 'scorer_path'
SCORER_OPTIONS = 'scorer_options'

def parse(file_path, backend=json):
    if isinstance(file_path, str):
        cfg = backend.load(open(file_path, 'r'))
    else:
        cfg = backend.load(file_path)

    if SCORER in cfg:
        if SCORER_OPTIONS in cfg[SCORER]:
            return cfg[SCORER][SCORER_OPTIONS]
        else:
            raise ValueError("Unrecognised config file, couldn't find "
                             "expected keys. File requires the nested key"
                             "'scorer/scorer_options'.")
    elif SCORER_OPTIONS in cfg:
        return cfg[SCORER_OPTIONS]
    else:
        raise ValueError("Unrecognised config file, couldn't find "
                         "expected keys. File requires the nested key"
                         "'scorer/scorer_options' or the key 'scorer_options'")

def validate(cfg_dict):
    if not isinstance(cfg_dict, dict):
        raise TypeError(
            "Expected parsed configuration to be type 'dict'"
            " Found {}.".format(type(cfg_dict).__name__))
    if not bool(cfg_dict):
        empty_error = "Parsing function returned an empty dictionary"
        raise ValueError(empty_error)


# -------------------------------------------------------------------------- #
#                           Options File Object
# -------------------------------------------------------------------------- #
class OptionsFile(object):
    """
    Utility class to represent an 'Options file' and it's associated parsing
    and validation funcitons.
    """

    @staticmethod
    def default_json_options_file(name="Options File"):
        options_file = OptionsFile(
            name=name,
            parsing_func=parse,
            parsing_func_kwargs={'backend': json},
            validator_func=validate,
            validator_func_kwargs={}
        )
        return options_file

    @staticmethod
    def default_yaml_options_file(name="Options File"):
        options_file = OptionsFile(
            name=name,
            parsing_func=parse,
            parsing_func_kwargs={'backend': yaml},
            validator_func=validate,
            validator_func_kwargs={}
        )
        return options_file

    def __init__(self, name, parsing_func, parsing_func_kwargs,
                 validator_func, validator_func_kwargs):
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
        return self._parser_func(file_path, **self.parse_kwargs)

    def validate_cfg(self, cfg):
        self._validator_func(cfg, **self.valid_kwargs)


# -------------------------------------------------------------------------- #
#                           Utility methods
# -------------------------------------------------------------------------- #
def get_unused_options(cfg_dict, options):
    """
    
    Parameters
    ----------
    cfg_dict : 
    options : 

    Returns
    -------

    """
    unused = set()
    option_keys = set(options.keys())
    for key in cfg_dict.keys():
        if key not in option_keys:
            unused.add(key)
    return unused


def get_unused_options_ls(cfg_dict, options_ls):
    """
    
    Parameters
    ----------
    cfg_dict : 
    options_ls : 

    Returns
    -------

    """
    unused = set()
    option_keys = set([k for opts in options_ls for k in opts])
    for key in cfg_dict.keys():
        if key not in option_keys:
            unused.add(key)
    return unused


def options_not_in_config(cfg, options):
    """
    
    Parameters
    ----------
    cfg : 
    options : 

    Returns
    -------

    """
    missing = []
    for varname, option in options.items():
        if varname not in cfg:
            missing.append(option)
    return missing


def option_varnames_not_in_cfg(cfg, options):
    """
    
    Parameters
    ----------
    cfg : 
    options : 

    Returns
    -------

    """
    return [opt.varname for opt in options_not_in_config(cfg, options)]


def option_names_not_in_cfg(cfg, options):
    """
    
    Parameters
    ----------
    cfg : 
    options : 

    Returns
    -------

    """
    return [opt.name for opt in options_not_in_config(cfg, options)]


def apply_cfg_to_options(cfg, options):
    """
    
    Parameters
    ----------
    cfg : 
    options : 

    Returns
    -------

    """
    for key, value in cfg.items():
        if key in set(options.option_varnames()):
            options.set_option_by_varname(key, value)