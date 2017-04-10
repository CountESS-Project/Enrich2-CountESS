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

# -*- coding: utf-8 -*-

"""
This module contains classes representing the data model of an Enrich2
configuration file. Each class represents a `yaml`/`json` dictionary
and contains validation methods to format input from a GUI configurator.

Example
-------


Notes
-----


Attributes
----------


"""

from abc import ABC, abstractclassmethod


class Configuration(ABC):
    """
    Abtract class representing required operations on the data model.
    """

    @abstractclassmethod
    def validate(self):
        pass

    @abstractclassmethod
    def serialize(self):
        pass


class ExperimentConfiguration(Configuration):
    pass

class SelectionsConfiguration(Configuration):
    pass

class ConditonsConfiguration(Configuration):
    pass

class FASTQConfiguration(Configuration):
    pass

class BarcodesConfiguration(Configuration):
    pass

class IdentifiersConfiguration(Configuration):
    pass

class VariantsConfiguration(Configuration):
    pass

class WildTypeConfiguration(Configuration):
    pass

class LibrariesConfiguration(Configuration):
    pass



