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

import tkinter
import tkinter.messagebox
import tkinter.filedialog

from tkinter.ttk import *
from tkinter import E

from collections import OrderedDict
from .dialog import CustomDialog

from ..libraries.basic import BasicSeqLib
from ..libraries.barcodevariant import BcvSeqLib
from ..libraries.barcodeid import BcidSeqLib
from ..libraries.barcode import BarcodeSeqLib
from ..libraries.overlap import OverlapSeqLib
from ..libraries.seqlib import SeqLib
from ..libraries.variant import VariantSeqLib
from ..libraries.idonly import IdOnlySeqLib


seqlib_label_text = OrderedDict([
    ("BcvSeqLib", "Barcoded Variant"),
    ("BcidSeqLib", "Barcoded Identifier"),
    ("BasicSeqLib", "Basic"),
    ("BarcodeSeqLib", "Barcodes Only"),
    ("IdOnlySeqLib", "Identifiers Only"),
])


class CreateSeqLibDialog(CustomDialog):
    """
    Dialog box for creating a new SeqLib.
    """
    def __init__(self, parent_window, title="New SeqLib"):
        self.element_tkstring = tkinter.StringVar()
        self.element_type = None
        CustomDialog.__init__(self, parent_window, title, "SeqLib Type")

    def body(self, master):
        for i, k in enumerate(seqlib_label_text.keys()):
            rb = Radiobutton(
                master, text=seqlib_label_text[k],
                variable=self.element_tkstring, value=k
            )
            rb.grid(column=0, row=(i + 1), sticky="w")
            if i == 0:
                rb.invoke()

    def buttonbox(self):
        """
        Display only one button.
        """
        box = self.button_box
        w = Button(box, text="OK", width=10, command=self.ok)
        w.grid(column=0, row=0, padx=5, pady=5, sticky=E)
        self.bind("<Return>", self.ok)

    def apply(self):
        try:
            self.element_type = globals()[self.element_tkstring.get()]
        except KeyError:
            raise KeyError("Unrecognized element type.")