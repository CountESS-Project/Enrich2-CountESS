#  Copyright 2016-2017 Alan F Rubin, Daniel C Esposito
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
#  along with Enrich2. If not, see <http://www.gnu.org/licenses/>.



import logging
from hashlib import md5
from tkinter.messagebox import askyesno


from ..base.utils import log_message
from ..plugins import load_scorer_class_and_options


class Plugin(object):
    def __init__(self, path):
        result = load_scorer_class_and_options(path)
        klass, options, options_file = result

        self.klass = klass
        self.options = options
        self.options_file = options_file
        self.path = path
        self.md5_stamp = md5(open(path, 'rb').read()).hexdigest()

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return str(self.metadata())

    def __eq__(self, other):
        return hash(self) == hash(other) and \
               self.md5_stamp == other.md5_stamp

    def metadata(self):
        return self.klass.name, self.klass.version, \
               self.klass.author, self.path

    def md5_has_changed(self):
        new_plugin = Plugin(self.path)
        if self.metadata() == new_plugin.metadata() and \
                        self.md5_stamp != new_plugin.md5_stamp:
            log_message(
                logging_callback=logging.info,
                msg='Plugin at path {} has the same metadata but different '
                    'file contents.'.format(self.path),
                extra={'oname': self.__class__.__name__}
            )
            return True
        elif self.metadata() != new_plugin.metadata() and \
                        self.md5_stamp != new_plugin.md5_stamp:
            log_message(
                logging_callback=logging.info,
                msg='Plugin at path {} has does not match.'.format(self.path),
                extra={'oname': self.__class__.__name__}
            )
            return True
        else:
            return False

    def refresh(self):
        if self.md5_has_changed():
            yes = askyesno(
                "Reload plugin?",
                "The plugin located at '{}' has been modified. Do "
                "you want to reload this plugin?".format(self.path)
            )
            if yes:
                self._reload()
                return True
        return False

    def _reload(self):
        result = load_scorer_class_and_options(self.path)
        klass, options, options_file = result
        self.klass = klass
        self.options = options
        self.options_file = options_file
        self.md5_stamp = md5(open(self.path, 'rb').read()).hexdigest()
        return self