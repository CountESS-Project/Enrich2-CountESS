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


def nested_format(data, default, tab_level=1):
    """
    Print a human readable nested dictionary or nested list.
    
    Parameters
    ----------
    data : Data to print.
    default:     
    tab_level : Number of tabs to indent with.  

    Returns
    -------
    rtype : A formatted string.

    """
    msg = ""
    if isinstance(data, list) or isinstance(data, tuple):
        if not data:
            msg += 'Empty Iterable'
        else:
            msg += "-> Iterable"
            if default:
                msg += "-> Iterable [Default]"
            try:
                for i, (value, default) in enumerate(data):
                    msg += '\n' + '\t' * tab_level + '@index {}: '.format(i)
                    msg += nested_format(value, default, tab_level)
            except (TypeError, ValueError):
                for i, value in enumerate(data):
                    msg += '\n' + '\t' * tab_level + '@index {}: '.format(i)
                    msg += nested_format(value, False, tab_level)
            msg += '\n' + '\t' * tab_level + '@end of list'
    elif isinstance(data, dict):
        if not data:
            msg += 'Empty Dictionary'
        else:
            msg += "-> Dictionary"
            if default:
                msg += "-> Dictionary [Default]"
            try:
                for key, (value, default) in data.items():
                    msg += '\n' + "\t" * tab_level + "{}: ".format(key)
                    msg += nested_format(value, default, tab_level + 1)
            except (TypeError, ValueError):
                for key, value in data.items():
                    msg += '\n' + "\t" * tab_level + "{}: ".format(key)
                    msg += nested_format(value, False, tab_level + 1)
    else:
        if isinstance(data, str):
            data = "'{}'".format(data)
        dtype = type(data).__name__
        if default:
            msg += "({} [Default], {})".format(data, dtype)
        else:
            msg += "({}, {})".format(data, dtype)
    return msg


    
