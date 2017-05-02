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


def parse(file_path, backend=json):
    return backend.load(open(file_path, 'r'))


def valid(cfg_dict):
    return bool(cfg_dict)


class Option(object):
    """
    Utility class to represent a user defined option. Mainly used by the 
    GUI to render to a dialogue box.
    """

    def __init__(self, name, varname, dtype, default,
                 choices=None, tooltip="No information"):
        """

        Parameters
        ----------
        name : 
        varname : 
        dtype : 
        default : 
        choices : 
        tooltip : 
        """
        self.name = name
        self.varname = varname
        self.dtype = dtype
        self.default = default
        self.choices = {} if choices is None else choices
        self.tooltip = tooltip

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

    def validate(self, value):
        if not isinstance(value, self.dtype):
            raise TypeError("Option '{}' type {} does not match input type "
                            "{}.".format(self.name, self.dtype, type(value)))


class ScorerOptions(object):
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

    def append(self, option):
        self.options.append(option)
        return self


class OptionsFile(object):
    """
    
    """

    @staticmethod
    def default_json_options_file(name="JSON options file"):
        options_file = OptionsFile(
            name=name,
            parsing_func=parse,
            parsing_func_kwargs={'backend': json},
            validator_func=valid,
            validator_func_kwargs={}
        )
        return options_file

    @staticmethod
    def default_yaml_options_file(name="YAML options file"):
        options_file = OptionsFile(
            name=name,
            parsing_func=parse,
            parsing_func_kwargs={'backend': yaml},
            validator_func=valid,
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


class ScorerOptionsFiles(object):

    def __init__(self):
        self.options_files = []

    def __iter__(self):
        return iter(self.options_files)

    def __getitem__(self, item):
        return self.options_files[item]

    def __len__(self):
        return len(self.options_files)

    def add_options_file(self, name, parsing_func, parsing_func_kwargs,
                         validator_func, validator_func_kwargs):
        options_file = OptionsFile(
            name=name,
            parsing_func=parsing_func,
            parsing_func_kwargs=parsing_func_kwargs,
            validator_func=validator_func,
            validator_func_kwargs=validator_func_kwargs
        )
        self.options_files.append(options_file)

    def append(self, options_file):
        self.options_files.append(options_file)
        return self

