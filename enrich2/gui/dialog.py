from tkinter import Toplevel, BOTH
from tkinter.ttk import *


class CustomDialog(Toplevel):
    """
    Class to open dialogs which uses ttk instead of tkinter for style
    consistency. This class is intended as a base class for custom dialogs
    
    Parameters
    ----------
    parent : `enrich2.gui.configurator.Configurator`
        A parent window (the application window)
    title : `str`
        The dialog window title
    body_frame_text: `str`, default: ''   
        Specify text to house all elements in a `LabelFrame`
        
    Methods
    -------
    body
        Create dialog body, overrides TopLevel.
    destroy
        Handles the destory window event.
    buttonbox
        Adds a standard button box to the dialog.
    ok
        Handles the 'ok' button press event.
    cancel
        Handles the 'cancel' button press event.
    validate
        This method is called automatically to validate the data before the
        dialog is destroyed. By default, it always validates OK.
    apply
        This method is called automatically to process the data, *after*
        the dialog is destroyed. By default, it does nothing.
    
    See Also
    --------
    :py:class:`~Toplevel`
    """

    def __init__(self, parent, title=None, body_frame_text=""):
        """
        Initialize a dialog.
        """
        Toplevel.__init__(self, parent)

        self.withdraw()  # remain invisible for now
        # If the master is not viewable, don't
        # make the child transient, or else it
        # would be opened withdrawn
        if parent.winfo_viewable():
            self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent
        self.result = None
        self.row = 0
        self.column = 0

        self.overall_frame = Frame(self)

        if body_frame_text:
            self.body_frame = LabelFrame(self.overall_frame, text=body_frame_text)
        else:
            self.body_frame = Frame(self.overall_frame)
        self.initial_focus = self.body(self.body_frame)

        self.body_frame.grid(
            column=self.column, row=self.row, sticky="nsew", padx=5, pady=5
        )
        self.rowconfigure(self.row, weight=1)
        self.columnconfigure(self.column, weight=1)
        self.row += 1

        self.button_box = Frame(self.overall_frame)
        self.buttonbox()

        self.button_box.grid(
            column=self.column, row=self.row, sticky="e", padx=5, pady=5
        )
        self.rowconfigure(self.row, weight=1)
        self.columnconfigure(self.column, weight=1)
        self.row += 1
        self.column += 1

        self.overall_frame.pack(fill=BOTH, expand=True)
        self.resizable(False, False)

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        if self.parent is not None:
            self.geometry(
                "+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50)
            )

        self.deiconify()  # become visible now

        self.initial_focus.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def destroy(self):
        """
        Destroy the window
        """
        self.initial_focus = None
        Toplevel.destroy(self)

    def body(self, master):
        """
        Create dialog body.

        Return widget that should have initial focus.
        This method should be overridden, and is called
        by the __init__ method.
        """
        pass

    def buttonbox(self):
        """
        Add standard button box.

        Override if you do not want the standard buttons
        """
        w = Button(self.button_box, text="OK", width=10, command=self.ok)
        w.grid(column=0, row=0, padx=5, pady=5)
        w = Button(self.button_box, text="Cancel", width=10, command=self.cancel)
        w.grid(column=1, row=0, padx=5, pady=5)
        self.button_box.rowconfigure(0, weight=1)
        self.button_box.columnconfigure(0, weight=1)
        self.button_box.columnconfigure(1, weight=1)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

    def ok(self, event=None):
        """
        Handles the 'ok' button click.
        """
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        try:
            self.apply()
            self.parent.refresh_treeview()
        finally:
            self.cancel()

    def cancel(self, event=None):
        """
        Handles the 'cancel' button click event.
        """
        # put focus back to the parent window
        if self.parent is not None:
            self.parent.focus_set()
        self.destroy()

    def validate(self):
        """
        Validate the data

        This method is called automatically to validate the data before the
        dialog is destroyed. By default, it always validates OK.
        """
        return 1

    def apply(self):
        """
        Process the data

        This method is called automatically to process the data, *after*
        the dialog is destroyed. By default, it does nothing.
        """
        pass
