import os.path

from tkinter import StringVar, BooleanVar
from tkinter import messagebox
from tkinter import filedialog
from tkinter.ttk import *
from tkinter import LEFT


DEFAULT_COLUMNS = 3


class SectionLabel(object):
    """
    A custom object representing a label for a discrete GUI section
    
    Parameters
    ----------
    text : `str`
        The text label for the section.
    
    Attributes
    ----------
    text : `str`
        The text label for the section.
         
    Methods
    -------
    body
        Creates the body frame for the label.
    validate
        validate method to be overridden 
    apply
        apply method to be overridden 
    enable 
        enable method to be overridden
    disable
        disable method to be overriden
    """

    def __init__(self, text):
        self.text = text

    def body(self, master, row, columns=DEFAULT_COLUMNS, **kwargs):
        """
        Builds the main frame for housing the label, to be contained within
        some master tk widget.
        
        Parameters
        ----------
        master : A Tk widget or window.
            Master widget.
        row : 
            The row number of the label frame.
        columns : 
            The column span of the label frame.
        kwargs : `dict`
            Keyword arguments. No used in this implementation.
            
        Returns
        -------
        `int`
            Returns the number of rows taken by this element.
        """
        label = Label(master, text=self.text, justify=LEFT)
        label.grid(row=row, column=0, columnspan=columns, sticky="w")
        return 1

    def validate(self):
        return True

    def apply(self):
        return None

    def enable(self):
        pass

    def disable(self):
        pass


class Checkbox(object):
    """
    A utility class to represent a custom checkbox with helper methods.
    
    Parameters
    ----------
    text : `str`
        The text label for the checkbox.
    cfg : `dict`
        A dictionary representing of widgets with `key` being the key in the
        cfg for this widget.
    key : `str`
        The key for this widget in `cfg`. 
    
    Attributes
    ----------
    checkbox : `Checkbox`
        A tk checkbox widget.
    enabled : `bool`
        Boolean indicating if this widget is enabled.
    value : `BooleanVar`
        The tk variable linked to the checkbox.
    text : `str`
        The text label for the checkbox
    cfg : `dict`
        A dictionary representing of widgets with `key` being the key in the
        cfg for this widget.
    key : `str`
        The key for this widget in `cfg`. 
    
    Methods
    -------
    body
        Place the required elements using the grid layout method.
        Returns the number of rows taken by this element.
    validate
        Validate the checkbox selection. Returns True, always.
    apply
        If enabled, sets the configuration for `key` as the current
        checkbox selection.   
    enable
        Enables the checkbox widget from interaction.
    disable
        Disables the checkbox widget from interaction.
    """

    def __init__(self, text, cfg, key):
        self.checkbox = None
        self.enabled = True

        self.value = BooleanVar()
        self.text = text
        self.cfg = cfg
        self.key = key
        try:
            if self.cfg[self.key] not in (True, False):
                self.value.set(False)
            else:
                self.value.set(self.cfg[self.key])
        except KeyError:
            self.value.set(False)  # default to False

    def body(self, master, row, columns=DEFAULT_COLUMNS, **kwargs):
        """
        Place the required elements using the grid layout method.
        Returns the number of rows taken by this element.
        
        Parameters
        ----------
        master : A tk widget or window.
        row : `int`
            The row variable to use during packing/grid
        columns : `int`
            The columnspan to use during packing/grid
        kwargs : `dict`
            Keyword arguements to pass to packing/grid. Currently ignored.
            
        Returns
        -------
        `int`
            Returns the number of rows taken by this element.
        """
        self.checkbox = Checkbutton(master, text=self.text, variable=self.value)
        self.checkbox.grid(row=row, column=0, columnspan=columns, sticky="w")
        return 1

    def validate(self):
        """
        Validate the checkbox selection.
        """
        return True

    def apply(self):
        """
        If enabled, sets the configuration for `key` as the current
        checkbox selection.        
        """
        if self.enabled:
            self.cfg[self.key] = self.value.get()
        else:
            self.cfg[self.key] = None

    def enable(self):
        """
        Set the state of the checkbox widget to not disabled.
        """
        self.enabled = True
        self.checkbox.state(["!disabled"])

    def disable(self):
        """
        Set the state of the checkbox widget to disabled.
        """
        self.enabled = False
        self.checkbox.state(["disabled"])


class MyEntry(object):
    """
    Base class for labeled Entry fields.
    *text* is the Label/error box text.
    
    Parameters
    ----------
    text : `str`
        The text label for the checkbox.
    cfg : `dict`
        A dictionary representing of widgets with `key` being the key in the
        cfg for this widget.
    key : `str`
        The key for this widget in `cfg`. 
    optional : `bool`, default: ``False``
        Specifies if entry input is optional or not.
    
    Attributes
    ----------
    entry : `Entry`
        A tk Entry widget.
    enabled : `bool`
        Boolean indicating if this widget is enabled.
    value : `StringVar`
        The tk variable linked to the widget.
    text : `str`
        The text label for the widget
    cfg : `dict`
        A dictionary representing of widgets with `key` being the key in the
        cfg for this widget.
    key : `str`
        The key for this widget in `cfg`. 
    
    Methods
    -------
    body
        Place the required elements using the grid layout method.
        Returns the number of rows taken by this element.
    validate
        Validates the input. Returns ``True`` unless the field is blank and
        *optional* is ``False``.
    apply
        If enabled, sets the configuration at `key` as the current
        entry text stored in the tkvar.    
    enable
        Enables the widget to allow interaction.
    disable
        Disables the widget from interaction.
    """

    def __init__(self, text, cfg, key, optional=False):
        self.entry = None
        self.enabled = True

        self.value = StringVar()
        self.text = text
        self.cfg = cfg
        self.key = key
        self.optional = optional
        try:
            if self.cfg[self.key] is None:
                self.value.set("")
            else:
                self.value.set(self.cfg[self.key])
        except KeyError:
            self.value.set("")

    def body(self, master, row, columns=DEFAULT_COLUMNS, **kwargs):
        """
        Place the required elements using the grid layout method.
        Returns the number of rows taken by this element.
        
        Parameters
        ----------
        master : A tk widget or window.
        row : `int`
            The row variable to use during packing/grid
        columns : `int`
            The columnspan to use during packing/grid
        kwargs : `dict`
            Keyword arguements to pass to packing/grid. Currently ignored.
            
        Returns
        -------
        `int`
            Returns the number of rows taken by this element.
        """
        label = Label(master, text=self.text, justify=LEFT)
        label.grid(row=row, column=0, columnspan=1, sticky="e")
        self.entry = Entry(master, textvariable=self.value)
        self.entry.grid(row=row, column=1, columnspan=columns - 1, sticky="ew")
        return 1

    def validate(self):
        """
        Validates the input. Returns ``True`` unless the field is blank and
        *optional* is ``False``.
        """
        if not self.enabled:
            return True
        elif not self.optional and len(self.value.get()) == 0:
            messagebox.showwarning("", "{} not specified.".format(self.text))
            return False
        else:
            return True

    def apply(self):
        """
        If enabled, sets the configuration at `key` as the current
        entry text stored in the tkvar.   
        """
        if self.enabled and len(self.value.get()) > 0:
            self.cfg[self.key] = self.value.get()
        else:
            self.cfg[self.key] = None

    def enable(self):
        """
        Enables the widget.
        """
        self.enabled = True
        self.entry.state(["!disabled"])

    def disable(self):
        """
        Disables the widget from interaction.
        """
        self.enabled = False
        self.entry.state(["disabled"])


class FileEntry(MyEntry):
    """
    Creates a labeled Entry field for a file or directory.

    Parameters
    ----------
    text : `str` 
        is the Label/error box text.
    directory : `bool`
        is ``True`` if selecting a directory (instead of a file).
    extensions : `list`
        is a list of valid file endings
    cfg : `dict`
        A dictionary representing of widgets with `key` being the key in the
        cfg for this widget.
    key : `str`
        The key for this widget in `cfg`. 
    optional : `bool`, default: ``False``
        Specifies if entry input is optional or not.
    
    Attributes
    ----------
    choose : `Button`
        Choose file button.
    clear : `Button`
        Clear selection button.
    directory : `bool`
        is ``True`` if selecting a directory (instead of a file).
    extensions : `list`
        is a list of valid file endings
    
    Methods
    -------
    body
        Place the required elements using the grid layout method.
        Returns the number of rows taken by this element.
    validate
        Validate the selected file to make sure it exists and has the 
        correct extension.
    enable
        Enables the widget to allow interaction.
    disable
        Disables the widget from interaction.
    """

    def __init__(
        self, text, cfg, key, optional=False, directory=False, extensions=None
    ):
        MyEntry.__init__(self, text, cfg, key, optional)
        self.choose = None
        self.clear = None

        self.directory = directory
        if extensions is not None:
            self.extensions = [x.lower() for x in extensions]
        else:
            self.extensions = None

    def body(self, master, row, columns=DEFAULT_COLUMNS, **kwargs):
        """
        Place the required elements using the grid layout method.
        Returns the number of rows taken by this element.
        
        Parameters
        ----------
        master : A tk widget or window.
        row : `int`
            The row variable to use during packing/grid
        columns : `int`
            The columnspan to use during packing/grid
        kwargs : `dict`
            Keyword arguements to pass to packing/grid. Currently ignored.
            
        Returns
        -------
        `int`
            Returns the number of rows taken by this element.
        """
        label = Label(master, text=self.text, justify=LEFT)
        label.grid(row=row, column=0, columnspan=1, sticky="e")
        self.entry = Entry(master, textvariable=self.value)
        self.entry.grid(row=row, column=1, columnspan=columns - 1, sticky="ew")
        if self.directory:
            self.choose = Button(
                master,
                text="Choose...",
                command=lambda: self.value.set(filedialog.askdirectory()),
            )
        else:
            self.choose = Button(
                master,
                text="Choose...",
                command=lambda: self.value.set(filedialog.askopenfilename()),
            )

        self.choose.grid(row=row + 1, column=2, sticky="e")

        if self.optional:
            self.clear = Button(
                master, text="Clear", command=lambda: self.value.set("")
            )
            self.clear.grid(row=row + 1, column=2, sticky="e")

        return 2

    def validate(self):
        """
        Validate the selected file to make sure it exists and has the 
        correct extension.
        """
        if not self.enabled:
            return True

        elif len(self.value.get()) == 0:
            if not self.optional:
                messagebox.showwarning(
                    "File Error", "{} not specified.".format(self.text)
                )
                return False
            else:
                return True

        else:
            if os.path.exists(self.value.get()):
                if self.extensions is not None:
                    valid_ext = any(
                        self.value.get().lower().endswith(x) for x in self.extensions
                    )

                    if valid_ext:
                        return True
                    else:
                        messagebox.showwarning(
                            "File Error",
                            "Invalid file extension for {}.".format(self.text),
                        )
                        return False
                else:  # no extension restriction
                    return True
            else:
                messagebox.showwarning(
                    "File Error", "{} file does not exist.".format(self.text)
                )
                return False

    def enable(self):
        """
        Enables the widget to allow interaction.
        """
        self.enabled = True
        self.entry.state(["!disabled"])
        self.choose.state(["!disabled"])
        if self.optional:
            self.clear.state(["!disabled"])

    def disable(self):
        """
        Disables the widget from interaction.
        """
        self.enabled = False
        self.entry.state(["disabled"])
        self.choose.state(["disabled"])
        if self.optional:
            self.clear.state(["disabled"])


class StringEntry(MyEntry):
    """
    Creates a labeled Entry field for a string.
    
    Parameters
    ----------
    text : `str` 
        is the Label/error box text.
    cfg : `dict`
        A dictionary representing of widgets with `key` being the key in the
        cfg for this widget.
    key : `str`
        The key for this widget in `cfg`. 
    optional : `bool`, default: ``False``
        Specifies if entry input is optional or not.
        
    Methods
    -------
    body
        Place the required elements using the grid layout method.
        Returns the number of rows taken by this element.
    """

    def __init__(self, text, cfg, key, optional=False):
        MyEntry.__init__(self, text, cfg, key, optional)

    def body(self, master, row, columns=DEFAULT_COLUMNS, **kwargs):
        """
        Place the required elements using the grid layout method.
        Returns the number of rows taken by this element.
        
        Parameters
        ----------
        master : A tk widget or window.
        row : `int`
            The row variable to use during packing/grid
        columns : `int`
            The columnspan to use during packing/grid
        kwargs : `dict`
            Keyword arguements to pass to packing/grid. Currently ignored.
            
        Returns
        -------
        `int`
            Returns the number of rows taken by this element.
        """
        label = Label(master, text=self.text, justify=LEFT)
        label.grid(row=row, column=0, columnspan=1, sticky="w")
        self.entry = Entry(master, textvariable=self.value)
        self.entry.grid(row=row, column=1, columnspan=columns - 1, sticky="ew")
        return 1


class IntegerEntry(MyEntry):
    """
    Creates a labeled Entry field for an integer.

    Parameters
    ----------
    text : `str` 
        is the Label/error box text.
    cfg : `dict`
        A dictionary representing of widgets with `key` being the key in the
        cfg for this widget.
    key : `str`
        The key for this widget in `cfg`. 
    optional : `bool`, default: ``False``
        Specifies if entry input is optional or not.
    minvalue : `int`
        Minimum value the entry can take.
        
    Attributes
    ----------
    minvalue : `int`
        Minimum value the entry can take.
        
    Methods
    -------
    body
        Place the required elements using the grid layout method.
        Returns the number of rows taken by this element.
    validate
        Validates the input. Returns ``True`` unless the field is blank and
        *optional* is ``False``.
    apply
        If enabled, sets the configuration at `key` as the current
        entry text stored in the tkvar.    
    """

    def __init__(self, text, cfg, key, optional=False, minvalue=0):
        MyEntry.__init__(self, text, cfg, key, optional)
        self.minvalue = minvalue

    def body(self, master, row, columns=DEFAULT_COLUMNS, width=4, left=False, **kwargs):
        """
        Add the labeled entry to the Frame *master* using grid at *row*.
        Returns the number of rows taken by this element.
      
        Parameters
        ----------
        master : A tk widget or window.
        row : `int`
            The row variable to use during packing/grid
        columns : `int`
            Is the number of columns in *master*.
        kwargs : `dict`
            Keyword arguements to pass to packing/grid. Currently ignored.
        width : `int` 
            Controls the width of the Entry.
        left : `bool` 
            Is ``True`` if the Entry is to the left of the Label.
            
        Returns
        -------
        `int`
            Returns the number of rows taken by this element.
        """
        if left:
            entry_column = 0
            entry_sticky = "e"
            entry_width = 1
            label_column = 1
            label_sticky = "w"
            label_width = columns - 1
        else:
            entry_column = 1
            entry_sticky = "w"
            entry_width = columns - 1
            label_column = 0
            label_sticky = "e"
            label_width = 1

        label = Label(master, text=self.text, justify=LEFT)
        label.grid(
            row=row, column=label_column, columnspan=label_width, sticky=label_sticky
        )
        self.entry = Entry(master, textvariable=self.value, width=width)
        self.entry.grid(
            row=row, column=entry_column, columnspan=entry_width, sticky=entry_sticky
        )
        return 1

    def validate(self):
        """
        Returns ``True`` if the value entered validates; else ``False``.

        If *self.optional* is ``True``, the field can be empty.
        Checks the *self.minvalue* that was passed on creation.
        """
        if not self.enabled:
            return True
        else:
            try:
                intvalue = int(self.value.get())
            except ValueError:
                if len(self.value.get()) == 0:
                    if not self.optional:
                        messagebox.showwarning(
                            "Validation Error", "{} not specified.".format(self.text)
                        )
                        return False
                    else:
                        return True
                else:
                    messagebox.showwarning(
                        "Validation Error", "{} is not an integer.".format(self.text)
                    )
                    return False
            else:
                if intvalue < self.minvalue:
                    messagebox.showwarning(
                        "",
                        "{} lower than minimum "
                        "value ({}).".format(self.text, self.minvalue),
                    )
                    return False
                else:
                    return True

    def apply(self):
        """
        Applies the value in the tkvar to the cfg passed during creation.
        """
        if self.enabled and len(self.value.get()) > 0:
            self.cfg[self.key] = int(self.value.get())
        else:
            self.cfg[self.key] = None
