from tkinter import StringVar
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

globals()["Selection"] = Selection
globals()["Condition"] = Condition
globals()["Experiment"] = Experiment
globals()["BarcodeSeqLib"] = BarcodeSeqLib
globals()["BcidSeqLib"] = BcidSeqLib
globals()["BcvSeqLib"] = BcvSeqLib
globals()["BasicSeqLib"] = BasicSeqLib
globals()["IdOnlySeqLib"] = IdOnlySeqLib


class CreateRootDialog(CustomDialog):
    """
    Dialog box for creating a new root element.
    
    
    Parameters
    ----------
    parent_window : `TopLevel` or `Tk`
        Parent Tk window managing this dialog
    title : `str`: default: 'Create Root Object'
        The title of the dialog window.
        
    Attributes
    ----------
    element_tkstring : `StringVar`
        String name of the selected root element to index into the globals
        to get the right class to instantiate.
    cfg_dict: `dict`
        Configuration dictionary to configure root element with.
    output_directory_tk: `StringVar`
        The output directory variable linked to the `output directory` 
        string entry field.
    name_tk : `StringVar`
        The name variable linked to the `Name` string entry field.
    element : :py:class:`~enrich2.base.storemanager.StoreManager`
        Root element object.
    
    Methods
    -------
    body
        Creates the body for the root dialog, laying out the radio boxes
        choices for each root object type (experiment, selection, library).
    buttonbox
        Creates a buttonbox to handles the radio box selection.
    validate
        Validate the selection and configuration of the root object.
    apply
        Applies the root configuration to the selected root element upon
        clicking `ok`.
      
    See Also
    --------
    :py:class:`~enrich2.gui.dialog.CustomDialog`
    """

    def __init__(self, parent_window, title="Create Root Object"):
        self.element_tkstring = StringVar()
        self.cfg_dict = dict()
        self.output_directory_tk = FileEntry(
            "Output Directory",
            self.cfg_dict,
            "output directory",
            optional=False,
            directory=True,
        )
        self.name_tk = StringEntry("Name", self.cfg_dict, "name", optional=False)
        self.element = None
        CustomDialog.__init__(self, parent_window, title)

    def body(self, master):
        """
        Creates and grid-packs the body for rendering. 
        
        Creates a radiobutton for each SeqLib option and links these to the 
        string tk variable.
        
        Parameters
        ----------
        master : `TopLevel` or `Tk`
            Master window.
        """
        row_no = 0

        config_frame = LabelFrame(master, text="Root Configuration")
        self.name_tk.body(config_frame, 0)
        self.output_directory_tk.body(config_frame, 1)
        config_frame.grid(
            column=0, row=row_no, sticky="nsew", columnspan=DEFAULT_COLUMNS
        )

        row_no += 1
        element_types = LabelFrame(master, padding=(3, 3, 12, 12), text="Root Type")
        element_types.grid(
            column=0, row=row_no, sticky="nsew", columnspan=DEFAULT_COLUMNS
        )

        label = Label(element_types, text="Experiment")
        label.grid(column=0, row=1, sticky="w")
        rb = Radiobutton(
            element_types,
            text="Experiment",
            variable=self.element_tkstring,
            value="Experiment",
        )
        rb.grid(column=0, row=2, sticky="w")
        rb.invoke()

        label = Label(element_types, text="Selection")
        label.grid(column=0, row=3, sticky="w")
        rb = Radiobutton(
            element_types,
            text="Selection",
            variable=self.element_tkstring,
            value="Selection",
        )
        rb.grid(column=0, row=4, sticky="w")

        label = Label(element_types, text="Sequence Library")
        label.grid(column=0, row=5, sticky="w")
        for i, k in enumerate(seqlib_label_text.keys()):
            rb = Radiobutton(
                element_types,
                text=seqlib_label_text[k],
                variable=self.element_tkstring,
                value=k,
            )
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
        """
        Checks the fields specified by the output directory and root object
        name entry fields.
        
        Returns
        -------
        `bool`
        """
        # check the fields
        return self.output_directory_tk.validate() and self.name_tk.validate()

    def apply(self):
        """
        Gets the configuration specified by the fields `output_directory`
        and `name` and applies them to the selected root element to create
        a new root object.
        """
        # apply the fields
        self.output_directory_tk.apply()
        self.name_tk.apply()

        # create the object
        try:
            print("Selection" in globals())
            self.element = globals()[self.element_tkstring.get()]()
        except KeyError:
            raise KeyError(
                "Unrecognized element type '{}'".format(self.element_tkstring.get())
            )

        # set the properties from this dialog
        self.element.output_dir_override = False
        self.element.output_dir = self.cfg_dict["output directory"]
        self.element.name = self.cfg_dict["name"]
