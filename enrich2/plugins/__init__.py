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


import os
import sys
from .scoring import BaseScorerPlugin
from .options import Options, OptionsFile


class ModuleLoader(object):
    def __init__(self, path):
        if not isinstance(path, str):
            raise TypeError("Argument `path` needs to be a string.")
        if not os.path.exists(path):
            raise IOError("Invalid plugin path {}.".format(path))

        path_to_module_folder = '/'.join(path.split('/')[:-1])
        module_folder = path_to_module_folder.split('/')[-1]
        module_name, ext = os.path.splitext(path.split('/')[-1])
        if ext != '.py':
            raise IOError("Plugin must be a python file.")

        try:
            sys.path.append(path_to_module_folder)
            top_module = __import__("{}.{}".format(module_folder, module_name))
            self.module_name = module_name
            self.module_folder = module_folder
            self.module = getattr(top_module, self.module_name)
        except BaseException as err:
            raise ImportError(err)

    def get_module_attrs(self):
        return self.module.__dict__.items()

    def get_attr_from_module(self, name):
        if not hasattr(self.module, name):
            raise AttributeError("Module {} does not have attribute "
                                 "{}.".format(self.module_name, name))
        return getattr(self.module, name)


def load_scorer_class_and_options(path):
    loader = ModuleLoader(path)
    scorers = []
    for attr_name, attr in loader.get_module_attrs():
        if implements_methods(attr) and attr != BaseScorerPlugin:
            scorers.append(attr)
    if len(scorers) < 1:
        raise ImportError("Could not find any classes implementing "
                          "the required BaseScorerPlugin interface.")
    if len(scorers) > 1:
        raise ImportError("Found Multiple classes implementing "
                          "the required BaseScorerPlugin interface.")

    options_ = None
    options_file = None
    for attr_name, attr in loader.get_module_attrs():
        if isinstance(attr, Options):
            if options_ is not None:
                raise ImportError("Two Options classes found. Expecting only"
                                  "one instantiation.")
            if not attr.has_options():
                raise ImportError("Options class must contain options.")
            options_ = attr

    if options_ is not None and options_.has_options():
        options_file = OptionsFile.default_json_options_file()

    scorer_class = scorers[-1]
    return scorer_class, options_, options_file


def implements_methods(class_):
    if not hasattr(class_, "_base_name"):
        return False
    if not getattr(class_, "_base_name") == 'BaseScorerPlugin':
        return False
    if not hasattr(class_, "compute_scores"):
        return False
    return True

