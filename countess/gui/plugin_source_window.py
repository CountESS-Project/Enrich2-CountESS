from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askyesno

import os
import logging
from hashlib import md5


from ..base.utils import log_message


SOURCES = os.path.join(os.path.expanduser("~"), ".enrich2/sources.txt")
DEFAULT_SOURCE = os.path.join(os.path.expanduser("~"), ".enrich2")


def _ensure_sources_file_exists(file):
    if not os.path.exists(file):
        create_default = askyesno(
            "No file found.",
            "The file '{}' could not be found. Would you like to"
            "create the default sources file?".format(file),
        )
        if create_default:
            with open(file, "wt") as fp:
                fp.write(".enrich2")
        else:
            open(file, "wt").close()


def _source_is_valid(source_path):
    """
    Test if a path exists and is a valid directory
    Parameters
    ----------
    source_path : `str`
        The directory string to check

    Returns
    -------
    `bool`
        True if a path is a valid directory.
    """
    return source_path and os.path.exists(source_path) and os.path.isdir(source_path)


def parse_sources(file=SOURCES, include_default=False):
    """
    Parses a file of plugin directories into a set.
    
    Parameters
    ----------
    file : `str`
        the file to parse
    include_default : `bool`
        Explicitly include the default ~/.enrich2 directory.

    Returns
    -------
    `set`
        A set of string directories that exist.
    """
    _ensure_sources_file_exists(file)
    sources = set()
    with open(file, "rt") as fp:
        for line in fp:
            path = line.strip()
            if path == ".enrich2":
                sources.add(DEFAULT_SOURCE)
            if not _source_is_valid(path):
                log_message(
                    logging_callback=logging.warning,
                    msg="{} is not a valid source.".format(path),
                    extra={"oname": "SourceWindowModule"},
                )
            else:
                sources.add(os.path.normpath(path))

    if include_default:
        sources.add(DEFAULT_SOURCE)
    return sources


class SourceWindow(Toplevel):
    """
    This is a :py:class:`Toplevel` subclass to represent a pop-out window
    to add/remove plugin sources for Enrich2.
    
    Parameters
    ----------
    master : `object`, optional
        Tkinter object which is the master of this window. Usually a Tk object. 
    sources_file: `str`, optional
        Load sources from the specified file.
    kwargs : `dict`
        Keyword arguments for Toplevel.
    
    Attributes
    ----------
    row : `int`
        Row for grid-packing book-keeping.
    visible : `bool`
        Indicates if the widget is visible. Used by hide/show/toggle_show
    sources_file: `str`
        Sources file that the widget is modifying. Will be created in the 
        default home directory ('~/.enrich2/sources.txt') if no file was 
        passed at initialisation time.
    sources: `set`
        Set of plugin directories currently being used.
    current_stamp : `str`
        Current MD5 hexdigest of ``sources_file``
    session_start_sources: `set`
        Sources being used when this window was shown.
    init_sources : `set`
        Sources being used when this window was created.
    listbox: `Listbox`
        Lisbox widget from tkinter module inside this window.
    
    Methods
    -------
    _setup_scrollbar_and_listbox
        Setup the Listbox widget.
    _setup_buttons
        Setup the window button layout.
    toggle_show
        Toggles between hide/show.
    hide
        Hide the window.
    show
        Show the window.
    restore
        Restores ``sources`` to the sources present when the window was
        opened from the ``tools`` menu.
    absolute_restore
        Restores ``sources`` to the sources loaded when ``__init__`` 
        was first called.
    ask_save_and_quit
        For use when clicking the `x` button. Asks if changes should be saved
        since opening the window. Otherwise, reverts back to whatever sources
        were present when the window was first opened.
    save_and_quit
        Saves the current set of sources in `sources` to ``sources.txt`` in
        the home directory. Overwrites existing data.
    poll_file_changes
        Polls ``sources.txt`` for changes and updates the widget accordingly. 
        Uses a simple md5 hash on the file to determine if there have been
        any changes.
    update_listbox
        Updates the text items in the Listbox object according to the 
        items in `sources.txt`
    remove_item
        Remove a directory into the current list of sources.
    add_item
        Add a directory into the current list of sources.
    
    See Also
    --------
    :py:class:`Toplevel`
    """

    def __init__(self, master=None, sources_file=SOURCES, **kwargs):
        Toplevel.__init__(self, master, **kwargs)
        _ensure_sources_file_exists(sources_file)
        self.row = 0
        self.visible = False
        self.sources_file = sources_file
        self.sources = parse_sources(file=sources_file)
        self.current_stamp = md5(open(sources_file, "rb").read()).hexdigest()
        self.session_start_sources = self.sources
        self.init_sources = self.sources
        self.listbox = None

        self._setup_scrollbar_and_listbox()
        self._setup_buttons()

        self.protocol("WM_DELETE_WINDOW", self.ask_save_and_quit)

    def _setup_scrollbar_and_listbox(self):
        """
        Setup the Listbox widget.
        """
        list_box_frame = Frame(self)
        list_box_frame.rowconfigure(0, weight=1)
        list_box_frame.columnconfigure(0, weight=1)
        list_box_frame.columnconfigure(1, weight=0)
        list_box_frame.grid(row=0, column=0, sticky=NSEW)

        self.listbox = Listbox(list_box_frame)
        self.listbox.grid(sticky=NSEW, row=0, column=0, padx=(2, 2), pady=(2, 2))

        list_ysb = Scrollbar(
            list_box_frame, orient="vertical", command=self.listbox.yview
        )
        list_xsb = Scrollbar(
            list_box_frame, orient="horizontal", command=self.listbox.xview
        )
        list_ysb.grid(row=0, column=1, sticky=N + S + W, padx=(0, 2), pady=(2, 0))
        list_xsb.grid(row=1, column=0, sticky=E + W + N, padx=(2, 0), pady=(0, 0))
        self.listbox.config(yscroll=list_ysb.set, xscroll=list_xsb.set)

        list_box_frame.grid(sticky=NSEW, row=0, column=0)
        self.rowconfigure(self.row, weight=1)
        self.columnconfigure(0, weight=1)
        self.row += 1

        for source in self.sources:
            self.listbox.insert(END, source)

    def _setup_buttons(self):
        """
        Setup the window button layout.
        """
        buttons = Frame(self)
        insert = Button(buttons, text="Add", command=self.insert_item)
        insert.grid(sticky=W, row=0, column=0, padx=5, pady=5)
        delete = Button(buttons, text="Remove", command=self.remove_item)
        delete.grid(sticky=W, row=0, column=1, padx=5, pady=5)
        default = Button(buttons, text="Restore", command=self.absolute_restore)
        default.grid(sticky=W, row=0, column=2, padx=5, pady=5)

        save = Button(buttons, text="Done", command=self.save_and_quit)
        save.grid(sticky=E, row=0, column=3, padx=5, pady=5)

        buttons.grid(sticky=EW, row=self.row, column=0)
        buttons.columnconfigure(3, weight=3)
        self.row += 1

    def toggle_show(self):
        """
        Toggles between hide/show.
        """
        if not self.visible:
            self.show()
        else:
            self.hide()

    def hide(self):
        """
        Hide the window.
        """
        self.visible = False
        self.withdraw()

    def show(self):
        """
        Show the window and poll file for changes.
        """
        self.session_start_sources = self.sources
        self.visible = True
        self.poll_file_changes()
        self.update()
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self.after_idle(self.attributes, "-topmost", False)

    def restore(self):
        """
        Restores ``sources`` to the sources present when the window was
        opened from the ``tools`` menu.
        """
        self.sources = self.session_start_sources
        self.listbox.delete(0, END)
        for source in self.sources:
            self.listbox.insert(END, source)

    def absolute_restore(self):
        """
        Restores ``sources`` to the sources loaded when ``__init__`` 
        was first called.
        """
        self.sources = self.init_sources
        self.listbox.delete(0, END)
        for source in self.sources:
            self.listbox.insert(END, source)

    def ask_save_and_quit(self):
        """
        For use when clicking the `x` button. Asks if changes should be saved
        since opening the window. Otherwise, reverts back to whatever sources
        were present when the window was first opened.
        """
        save = askyesno("Save changes?", "Would you like to save your changes?")
        if save:
            self.save_and_quit()
        else:
            self.restore()
            self.hide()

    def save_and_quit(self):
        """
        Saves the current set of sources in `sources` to ``sources.txt`` in
        the home directory. Overwrites existing data.
        """
        with open(self.sources_file, "wt") as fp:
            for source in self.sources:
                fp.write("{}\n".format(source))
        self.poll_file_changes()
        self.hide()

    def poll_file_changes(self):
        """
        Polls ``sources.txt`` for changes and updates the widget accordingly. 
        Uses a simple md5 hash on the file to determine if there have been
        any changes.
        """
        _ensure_sources_file_exists(self.sources_file)
        stamp = md5(open(self.sources_file, "rb").read()).hexdigest()
        if stamp != self.current_stamp:
            self.update_listbox()
            self.current_stamp = stamp

    def update_listbox(self):
        """
        Updates the text items in the Listbox object according to the 
        items in `sources.txt`
        """
        sources = parse_sources(file=self.sources_file)
        self.listbox.delete(0, END)
        for source in sources:
            self.listbox.insert(END, source)

    def remove_item(self):
        """
        Remove a directory into the current list of sources.
        """
        if self.listbox.curselection():
            item_idx = self.listbox.curselection()[0]
            item = self.listbox.get(item_idx)
            if item == DEFAULT_SOURCE:
                yes = askyesno(
                    "Remove default directory?",
                    "Are you sure you want to remove the default Enrich2 "
                    "plugin directory? To add it back in later on, this "
                    "directory can be found at '{}'".format(DEFAULT_SOURCE),
                )
                if yes:
                    self.listbox.delete(ANCHOR)
                    self.sources = set([x for x in self.sources if x != item])
            else:
                self.listbox.delete(ANCHOR)
                self.sources = set([x for x in self.sources if x != item])

    def insert_item(self):
        """
        Insert a directory into the current list of sources.
        """
        source_folder = askdirectory()
        if source_folder:
            source_folder = os.path.normpath(source_folder)
            if _source_is_valid(source_folder):
                self.listbox.insert(END, source_folder)
                self.sources.add(source_folder)
