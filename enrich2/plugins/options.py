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
from collections import Mapping


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
class BaseOption(object):

    def __init__(self, name, varname, dtype, default):
        self.name = name
        self.varname = varname
        self.dtype = dtype
        self.default = default
        self.value = default

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
            raise TypeError("Option '{}' with type {} does not match input type "
                            "{}.".format(self.varname, self.dtype.__name__,
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
        self.value = value

    def get_value(self):
        """
        
        Returns
        -------

        """
        return self.value


class Option(BaseOption):
    """
    Utility class to represent a user defined option. Mainly used by the 
    GUI to render to a dialogue box.
    """

    def __init__(self, name, varname, dtype, default, choices=None):
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
        super(Option, self).__init__(name, varname, dtype, default)
        self.choices = {} if choices is None else choices
        self._rev_choices = {} if choices is None else choices

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
        self._rev_choices = {v: k for (k, v) in self.choices.items()}
        self.validate(self.value)

    def keytransform(self, value):
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
        super()._validate(value)
        if value in self._rev_choices:
            return self._rev_choices[value]
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
        if self.choices:
            if self.keytransform(value) not in self.choices.keys():
                raise ValueError("Trying to set 'choices' with an undefined "
                                 "value '{}'.".format(value))

    def set_value(self, value):
        """
        
        Parameters
        ----------
        value : 

        Returns
        -------

        """
        if self.choices:
            value = self.keytransform(value)
        super()._set_value(value)


class HiddenOption(BaseOption):
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
        super(HiddenOption, self).__init__(varname, varname, dtype, default)
        self.validate(self.value)

    def validate(self, value):
        super()._set_value(value)

    def set_value(self, value):
        super()._validate(value)


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

    def get_option_by_varname(self, varname):
        if varname not in self._options:
            raise KeyError("Key '{}' not found in {}.".format(
                varname, self.__class__.__name__))
        return self._options[varname]

    def add_item(self, varname, option):
        if varname in set(self._options.keys()):
            raise ValueError("Cannot define two options with the same "
                             "varname '{}'.".format(varname))
        self._options[varname] = option


class Options(BaseOptions):
    """
    Utility class that is to be used by a plugin developer to add options
    to their scoring script.
    """

    def __init__(self):
        """

        """
        super().__init__()

    def add_option(self, name, varname, dtype, default, choices=None):
        """

        Parameters
        ----------
        name : 
        varname : 
        dtype : 
        default : 
        choices : 

        Returns
        -------

        """
        option = Option(name, varname, dtype, default, choices)
        self.add_item(varname, option)


class HiddenOptions(BaseOptions):
    """
    Utility class that is to be used by a plugin developer to add 
    hidden options to their scoring script.
    """

    def __init__(self):
        """

        """
        super().__init__()

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
        option = HiddenOption(varname, dtype, default)
        self.add_item(varname, option)


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