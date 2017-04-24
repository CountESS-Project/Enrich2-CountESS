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
        self.choices = [] if choices is None else choices
        self.tooltip = tooltip

    def validate(self, value):
        if not isinstance(value, self.dtype):
            raise TypeError("Option type {} does not match "
                            "input type {}.".format(self.dtype, type(value)))


class ScoringOptions(object):
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


def make_attribute_dictionary(options_value_tuple):
    """
    
    Parameters
    ----------
    options_value_tuple : 

    Returns
    -------

    """
    options_dict = {}
    for option, value in options_value_tuple:
        option.validate(value)
        options_dict[option.varname] = value
    return options_dict
