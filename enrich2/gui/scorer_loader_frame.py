#  Copyright 2016 Alan F Rubin, Daniel C Esposito.
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
import logging
from tkinter import *
import tkinter.messagebox as messagebox
from ..plugins import load_scoring_class_and_options


TOP_LEVEL = os.path.dirname(__file__)
print(TOP_LEVEL)
print(os.path.isdir("{}/../plugins/"))
print(os.path.isdir("{}/../../plugins/"))


class ScorerScriptsDropDown(Frame):

    def __init__(self, parent=None, scripts_dir='./'):
        Frame.__init__(parent)
        self.parent = parent
