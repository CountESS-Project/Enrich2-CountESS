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
from collections import Iterable


# -------------------------------------------------------------------------- #
#                       Utility parse/validate methods
# -------------------------------------------------------------------------- #
def parse(file_path, backend=json):
    cfg = backend.load(open(file_path, 'r'))
    if 'scorer' in cfg:
        if 'scorer_options' in cfg:
            return cfg['scorer']['scorer_options']
    if 'scorer_options' in cfg:
        return cfg['scorer_options']
    else:
        raise ValueError("Unrecognised config file, couldn't find "
                         "expected keys. File requires the nested key"
                         "'scorer/scorer_options' or the key 'scorer_options'")

def validate(cfg_dict):
    if not isinstance(cfg_dict, dict):
        raise TypeError("Expected parsed configuration to be type 'dict'"
                        " Found {}.".format(type(cfg_dict).__name__))
    if not bool(cfg_dict):
        empty_error = "Parsing function returned an empty dictionary"
        raise ValueError(empty_error)


# -------------------------------------------------------------------------- #
#                           Option Types
# -------------------------------------------------------------------------- #
class Option(object):
    """
    Utility class to represent a user defined option. Mainly used by the 
    GUI to render to a dialogue box.
    """

    def __init__(self, name, varname, dtype, default,
                 choices=None, tooltip="No information"):
        """
        Option Constructor.

        Parameters
        ----------
        name : `str` like
        varname : `str` like
        dtype :
        default : 
        choices : `dict` or `Iterable` like
        tooltip : `str` like
        """
        self.name = name
        self.varname = varname
        self.dtype = dtype
        self.default = default
        self.choices = {} if choices is None else choices
        self.rev_choices = {} if choices is None else choices
        self.tooltip = tooltip
        self.value = default

        if not isinstance(self.choices, Iterable):
            raise TypeError("Parameter 'choices' in option '{}' must be an "
                            "iterable.".format(self.name))

        if isinstance(self.choices, Iterable) and \
                not isinstance(self.choices, dict):
            self.choices = {x: x for x in self.choices}

        if self.choices:
            if self.default not in self.choices:
                raise AttributeError("Parameter 'default' in option '{}' not "
                                     "found in 'choices'.".format(self.name))
        self.rev_choices = {v: k for k, v in self.choices.items()}
        self.set_value(default)

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
        if not isinstance(value, self.dtype):
            raise TypeError("Option '{}' type {} does not match input type "
                            "{}.".format(self.name, self.dtype.__name__,
                                         type(value).__name__))
        if self.choices:
            if value not in self.choices.keys() and \
                            value not in self.rev_choices.keys():
                raise ValueError("Trying to set 'choices' with an undefined "
                                 "value '{}'.".format(value))

    def set_value(self, value):
        self.validate(value)
        if self.choices:
            value = self.get_choice_key(value)
        self.value = value

    def get_choice_key(self, value):
        """
        Allow a user to set a config option with wither the GUI key or
        value key.
        
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
        self.validate(value)
        if value in self.rev_choices:
            return self.rev_choices[value]
        return value


class HiddenOption(object):
    """
    Utility class to represent a user defined option. These options only appear
    in the configuration file and will typically represent more advanced python
    data structure.
    """

    def __init__(self, varname, dtype, default):
        """
        HiddenOption Constructor.

        Parameters
        ----------
        varname : `str` like
        dtype :
        default : 
        """
        self.name = varname
        self.varname = varname
        self.dtype = dtype
        self.default = default
        self.value = default
        self.set_value(default)

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
        if not isinstance(value, self.dtype):
            raise TypeError("Option '{}' type {} does not match input type "
                            "{}.".format(self.name, self.dtype.__name__,
                                         type(value).__name__))

    def set_value(self, value):
        self.validate(value)
        self.value = value


# -------------------------------------------------------------------------- #
#                           Option containers
# -------------------------------------------------------------------------- #
class Options(object):
    """
    Utility class that is to be used by a plugin developer to add options
    to their scoring script.
    """

    def __init__(self):
        """

        """
        self.options = []

    def add_option(self, name, varname, dtype,
                   default, choices=None, tooltip=""):
        """

        Parameters
        ----------
        name : 
        varname : 
        dtype : 
        default : 
        choices : 
        tooltip : 

        Returns
        -------

        """
        varnames = [o.name for o in self.options]
        if varname in varnames:
            raise ValueError("Cannot define two options with the same "
                             "varname '{}'.".format(varname))
        self.options.append(
            Option(name, varname, dtype, default, choices, tooltip)
        )
        return self

    def __iter__(self):
        return iter(self.options)

    def __len__(self):
        return len(self.options)

    def __getitem__(self, item):
        return self.options[item]

    def option_varnames(self):
        return [o.varname for o in self.options]

    def option_names(self):
        return [o.name for o in self.options]

    def set_option_by_varname(self, varname, value):
        options = {o.varname: o  for o in self}
        if varname not in options:
            raise KeyError("Key '{}' not found in {}.".format(
                varname, self.__class__.__name__))
        try:
            options[varname].set_value(value)
        except (TypeError, ValueError) as err:
            raise Exception("Error setting '{}' to "
                            "value {}:\n{}".format(varname, value, err))

    def to_dict(self):
        return {o.varname: o.value for o in self}

    def append(self, option):
        self.options.append(option)
        return self

    def has_options(self):
        return bool(self.options)


class HiddenOptions(object):
    """
    Utility class that is to be used by a plugin developer to add 
    hidden options to their scoring script.
    """

    def __init__(self):
        """

        """
        self.hidden_options = []

    def add_option(self, varname, dtype, default):
        """

        Parameters
        ----------
        varname : 
        dtype : 
        default : 

        Returns
        -------

        """
        varnames = [o.name for o in self.hidden_options]
        if varname in varnames:
            raise ValueError("Cannot define two hidden options with the same "
                             "varname '{}'.".format(varname))
        self.hidden_options.append(
            HiddenOption(varname, dtype, default)
        )
        return self

    def __iter__(self):
        return iter(self.hidden_options)

    def __len__(self):
        return len(self.hidden_options)

    def __getitem__(self, item):
        return self.hidden_options[item]

    def option_varnames(self):
        return [o.varname for o in self.hidden_options]

    def option_names(self):
        return [o.name for o in self.hidden_options]

    def to_dict(self):
        return {o.varname: o.value for o in self}

    def set_option_by_varname(self, varname, value):
        options = {o.varname: o  for o in self}
        if varname not in options:
            raise KeyError("Key '{}' not found in {}.".format(
                varname, self.__class__.__name__))
        try:
            options[varname].set_value(value)
        except (TypeError, ValueError) as err:
            raise Exception("Error setting '{}' to "
                            "value {}:\n{}".format(varname, value, err))

    def append(self, option):
        self.hidden_options.append(option)
        return self

    def has_options(self):
        return bool(self.hidden_options)


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
    option_keys = options.option_varnames()
    for key in cfg_dict.keys():
        if key not in option_keys:
            unused.add(key)
    return unused


def get_unused_options_ls(cfg_dict, *options):
    """
    
    Parameters
    ----------
    cfg_dict : 
    options : 

    Returns
    -------

    """
    unused = set()
    for opts in list(options):
        unused |= get_unused_options(cfg_dict, opts)
    return unused


def varname_intersection(options_a, options_b):
    """
    
    Parameters
    ----------
    options_a : 
    options_b : 

    Returns
    -------

    """
    vnames_a = set(options_a.option_varnames())
    vnames_b = set(options_b.option_varnames())
    return vnames_a & vnames_b


def option_varnames_not_in_cfg(cfg, options):
    """
    
    Parameters
    ----------
    cfg : 
    options : 

    Returns
    -------

    """
    defaults = set()
    for varname in options.option_varnames():
        if varname not in cfg:
            defaults.add(varname)
    return defaults


def option_names_not_in_cfg(cfg, options):
    """
    
    Parameters
    ----------
    cfg : 
    options : 

    Returns
    -------

    """
    defaults = set()
    for name in options.option_names():
        if name not in cfg:
            defaults.add(name)
    return defaults


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
        if key in set(options.set_option_by_varname()):
            options.set_option_by_varname(key, value)