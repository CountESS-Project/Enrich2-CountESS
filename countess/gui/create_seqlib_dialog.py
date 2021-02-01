import tkinter
import tkinter.messagebox
import tkinter.filedialog

from tkinter.ttk import *
from tkinter import E

from collections import OrderedDict
from .dialog import CustomDialog

# Ensure all the classes are in globals dictionary.
from ..libraries.basic import BasicSeqLib
from ..libraries.barcodevariant import BcvSeqLib
from ..libraries.barcodeid import BcidSeqLib
from ..libraries.barcode import BarcodeSeqLib
from ..libraries.seqlib import SeqLib
from ..libraries.variant import VariantSeqLib
from ..libraries.idonly import IdOnlySeqLib


seqlib_label_text = OrderedDict(
    [
        ("BcvSeqLib", "Barcoded Variant"),
        ("BcidSeqLib", "Barcoded Identifier"),
        ("BasicSeqLib", "Basic"),
        ("BarcodeSeqLib", "Barcodes Only"),
        ("IdOnlySeqLib", "Identifiers Only"),
    ]
)


class CreateSeqLibDialog(CustomDialog):
    """
    Dialog box for creating a new SeqLib.
    
    Parameters
    ----------
    parent_window : `Tk` or `TopLevel`
        The managing window. Usually the main Enrich2 app configurator.
    title : `str`
        The title of the dialog window.
    
    Attributes
    ----------
    element_tkstring : :py:class:`~tkinter.StringVar`
        The tk string variable linked to the button box.
    element_type : A subclass of StoreManager.
        The constructor of the currently selected class.
    
    Methods
    -------
    body
        Creates the body of the dialog.
    buttonbox
        Creates and grid packs the button boxes.
    apply
        Handles the 'Ok' button press event.
    
    See Also
    --------
    :py:class:`~CustomDialog`
    """

    def __init__(self, parent_window, title="New SeqLib"):
        self.element_tkstring = tkinter.StringVar()
        self.element_type = None
        CustomDialog.__init__(self, parent_window, title, "SeqLib Type")

    def body(self, master):
        """
        Creates a radiobutton for each SeqLib option and links these to the 
        string tk variable.
        
        Parameters
        ----------
        master : `Tk` or `TopLevel`
            The managing window. Usually the main Enrich2 app configurator.
        """
        for i, k in enumerate(seqlib_label_text.keys()):
            rb = Radiobutton(
                master,
                text=seqlib_label_text[k],
                variable=self.element_tkstring,
                value=k,
            )
            rb.grid(column=0, row=(i + 1), sticky="w")
            if i == 0:
                rb.invoke()

    def buttonbox(self):
        """
        Grid places the button box and places an 'OK' button in the same
        frame. Display only one button.
        """
        box = self.button_box
        w = Button(box, text="OK", width=10, command=self.ok)
        w.grid(column=0, row=0, padx=5, pady=5, sticky=E)
        self.bind("<Return>", self.ok)

    def apply(self):
        """
        Gets the element string from the selected radio-button and uses this
        to index ``globals`` to set the corresponding class constructor.
        """
        try:
            self.element_type = globals()[self.element_tkstring.get()]
        except KeyError:
            raise KeyError("Unrecognized element type.")
