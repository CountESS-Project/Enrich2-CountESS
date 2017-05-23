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


from tkinter import Toplevel, BOTH
from tkinter.ttk import *


class CustomDialog(Toplevel):
    """
    Class to open dialogs which uses ttk instead of tkinter for style
    consistency. This class is intended as a base class for custom dialogs
    """

    def __init__(self, parent, title = None, body_frame_text=''):
        """
        Initialize a dialog.
        
        Parameters
        ----------
        parent : Toplevel
            A parent window (the application window)
        title : str
            The dialog window title
        """
        Toplevel.__init__(self, parent)

        self.withdraw() # remain invisible for now
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
            self.body_frame = LabelFrame(
                self.overall_frame, text=body_frame_text)
        else:
            self.body_frame =Frame(self.overall_frame)
        self.initial_focus = self.body(self.body_frame)

        self.body_frame.grid(
            column=self.column, row=self.row, sticky='nsew',
            padx=5, pady=5
        )
        self.rowconfigure(self.row, weight=1)
        self.columnconfigure(self.column, weight=1)
        self.row += 1

        self.button_box = Frame(self.overall_frame)
        self.buttonbox()

        self.button_box.grid(
            column=self.column, row=self.row, sticky='e',
            padx=5, pady=5
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
            self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                      parent.winfo_rooty()+50))

        self.deiconify() # become visible now

        self.initial_focus.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def destroy(self):
        """Destroy the window"""
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
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        try:
            self.apply()
        finally:
            self.cancel()

    def cancel(self, event=None):
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