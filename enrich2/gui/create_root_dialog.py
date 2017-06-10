#  Copyright 2016 Alan F Rubin
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

import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog

from tkinter import StringVar, LEFT, RIGHT, N, E, S, W
from tkinter.ttk import *

from .dialog import CustomDialog
from .create_seqlib_dialog import seqlib_label_text
from .dialog_elements import FileEntry, StringEntry, DEFAULT_COLUMNS


from ..experiment.experiment import Experiment
from ..experiment.condition import Condition
from ..selection.selection import Selection
from ..libraries.barcode import BarcodeSeqLib
from ..libraries.barcodeid import BcidSeqLib
from ..libraries.barcodevariant import BcvSeqLib
from ..libraries.basic import BasicSeqLib
from ..libraries.idonly import IdOnlySeqLib
from ..libraries.overlap import OverlapSeqLib

globals()['Selection'] = Selection
globals()['Condition'] = Condition
globals()['Experiment'] = Experiment
globals()['BarcodeSeqLib'] = BarcodeSeqLib
globals()['BcidSeqLib'] = BcidSeqLib
globals()['BcvSeqLib'] = BcvSeqLib
globals()['BasicSeqLib'] = BasicSeqLib
globals()['IdOnlySeqLib'] = IdOnlySeqLib


class CreateRootDialog(CustomDialog):
    """
    Dialog box for creating a new root element.
    """
    def __init__(self, parent_window, title="Create Root Object"):
        self.element_tkstring = StringVar()
        self.cfg_dict = dict()
        self.output_directory_tk = FileEntry(
            "Output Directory", self.cfg_dict,
            'output directory', optional=False, directory=True
        )
        self.name_tk = StringEntry(
            "Name", self.cfg_dict, 'name', optional=False
        )
        self.element = None
        text = "Root Configuration"
        CustomDialog.__init__(self, parent_window, title, body_frame_text=text)

    def body(self, master):
        row_no = 0

        config_frame = LabelFrame(master, text="Root Configuration")
        self.name_tk.body(config_frame, 0)
        self.output_directory_tk.body(config_frame, 1)
        config_frame.grid(
            column=0, row=row_no, sticky="nsew", columnspan=DEFAULT_COLUMNS)

        row_no += 1
        element_types = LabelFrame(
            master, padding=(3, 3, 12, 12), text="Root Type")
        element_types.grid(
            column=0, row=row_no, sticky="nsew", columnspan=DEFAULT_COLUMNS)

        label = Label(element_types, text="Experiment")
        label.grid(column=0, row=1, sticky="w")
        rb = Radiobutton(
            element_types, text="Experiment",
            variable=self.element_tkstring, value="Experiment")
        rb.grid(column=0, row=2, sticky="w")
        rb.invoke()

        label = Label(element_types, text="Selection")
        label.grid(column=0, row=3, sticky="w")
        rb = Radiobutton(
            element_types, text="Selection",
            variable=self.element_tkstring, value="Selection")
        rb.grid(column=0, row=4, sticky="w")

        label = Label(element_types, text="Sequence Library")
        label.grid(column=0, row=5, sticky="w")
        for i, k in enumerate(seqlib_label_text.keys()):
            rb = Radiobutton(
                element_types, text=seqlib_label_text[k],
                variable=self.element_tkstring, value=k)
            rb.grid(column=0, row=(i + 6), sticky="w")

    def buttonbox(self):
        """
        Display only one button.
        """
        box = self.button_box
        w = Button(box, text="OK", width=10, command=self.ok)
        w.grid(row=0, column=0, padx=5, pady=5)
        self.bind("<Return>", self.ok)

    def validate(self):
        # check the fields
        return self.output_directory_tk.validate() and self.name_tk.validate()

    def apply(self):
        # apply the fields
        self.output_directory_tk.apply()
        self.name_tk.apply()

        # create the object
        try:
            print('Selection' in globals())
            self.element = globals()[self.element_tkstring.get()]()
        except KeyError:
            raise KeyError("Unrecognized element type '{}'".format(
                self.element_tkstring.get()))

        # set the properties from this dialog
        self.element.output_dir_override = False
        self.element.output_dir = self.cfg_dict['output directory']
        self.element.name = self.cfg_dict['name']

