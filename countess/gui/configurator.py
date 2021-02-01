"""
Enrich2 gui configurator module
===============================
This is class representing the main TK window, which is the parent window
for all other frames.
"""


import json
import platform
import logging
import threading
import queue
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog

from tkinter.ttk import Frame, Button, Checkbutton, Treeview, LabelFrame
from tkinter.messagebox import askyesno, showinfo, showwarning, askokcancel

from ..base.config_constants import SCORER, SCORER_OPTIONS, SCORER_PATH
from ..base.constants import CALLBACK, MESSAGE, KWARGS
from ..base.utils import get_logging_queue, log_message
from ..experiment.condition import Condition
from ..selection.selection import Selection
from .create_root_dialog import CreateRootDialog
from .create_seqlib_dialog import CreateSeqLibDialog
from .delete_dialog import DeleteDialog
from .edit_dialog import EditDialog, clear_nones
from .seqlib_apply_dialog import SeqLibApplyDialog
from ..config.config_check import is_selection, seqlib_type
from ..config.config_check import is_seqlib, is_experiment
from ..libraries.seqlib import SeqLib
from ..experiment.experiment import Experiment
from .options_frame import ScorerScriptsDropDown
from .logging_frame import show_log_window
from .plugin_source_window import SourceWindow

__all__ = ["write_json", "Configurator"]


def write_json(d, handle):
    """
    Write the contents of dictionary *d* to an open file *handle* 
    in json format.

    *d* is passed to ``clear_nones`` before output.
    
    Parameters
    ----------
    d : `dict`
        Dictionary to write to file.
    handle : `Io`
        Open file handle to write to.
    """
    json.dump(clear_nones(d), handle, indent=2, sort_keys=True)


class Configurator(tk.Tk):
    """
    The main Tk window representing the main app.
    
    Attributes
    ---------- 
    treeview :  :py:class:`~tkinter.Treeview`
        The treeview widget.
    treeview_popup_target_id : `int`
        The pop target id relating to the id of the selected element.
    treeview_popup : :py:class:`~tkinter.Widget`
        The treeview popup widget.
    cfg_file_name : `str`
        The file name of the current configuration.
    element_dict : `dict`
        The dictionary of elements. Keys are the element ids.
    root_element : :py:class:`~enrich2.base.storemanager.StoreManager`
        An instance inheriting from storemanager that acts as a root object.
    force_recalculate :py:class:`tkinter.BooleanVar`
        The tkinter boolean variable for this option.
    component_outliers :py:class:`tkinter.BooleanVar`
        The tkinter boolean variable for this option.
    tsv_requested : :py:class:`tkinter.BooleanVar`
        The tkinter boolean variable for this option.
    treeview_buttons : `list`
        The ``new``, ``edit`` and ``delete`` buttons.
    go_button : :py:class`~tkinter.ttk.Button`
        The button that begins the analysis
    scorer_widget : :py:class:`~enrich2.gui.options_frame.ScorerScriptsDropDown`
        The ScorerScriptsDropDown instance associated with this app.
    scorer : :py:class:`~enrich2.plugins.scoring.BaseScorerPlugin`
        The scorer class loaded from a plugin
    scorer_attrs : `dict`
        The scoring attributes for the plugin.
    scorer_path : `str`
        The path to the currently selected scoring plugin.
    analysis_thread : :py:class:`~threading.Thread`
        The thread object that runs the computation method to prevent 
        GUI blocking.
    
    Methods
    -------
    create_main_frame
    create_menubar
    create_treeview_context_menu
    create_new_element
    
    menu_open
    menu_save
    menu_saveas
    menu_selectall
    
    refresh_treeview
    treeview_context_menu
    set_treeview_properties
    populate_tree
    go_button_press
    new_button_press
    edit_button_press
    delete_button_press
    delete_element
    apply_seqlib_fastq
    
    get_element
    get_focused_element
    get_selected_elements
    get_selected_scorer_class
    get_selected_scorer_attrs
    get_selected_scorer_path
    
    run_analysis
    set_gui_state
    configure_analysis
    
    refresh_plugins
    show_plugin_source_window

    See Also
    --------
    :py:class:`~tkinter.Tk`
    
    """

    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Enrich 2")

        # Main app variables
        self.cfg_file_name = tk.StringVar()
        self.element_dict = dict()
        self.root_element = None
        self.analysis_thread = None
        self.plugin_source_window = None
        self.queue = queue.Queue()

        # Treeview variables
        self.treeview = None
        self.treeview_popup_target_id = None
        self.treeview_popup = None

        # analysis options
        self.force_recalculate = tk.BooleanVar()
        self.component_outliers = tk.BooleanVar()
        self.tsv_requested = tk.BooleanVar()

        # allow resizing
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # create UI elements
        self.treeview_buttons = []
        self.go_button = None
        self.scorer_widget = None
        self.scorer = None
        self.scorer_attrs = None
        self.scorer_path = None
        self.create_main_frame()
        self.create_menubar()
        self.create_treeview_context_menu()
        self.after(10, self.poll_logging_queue)

        self.plugin_source_window = SourceWindow(master=self)
        self.plugin_source_window.hide()
        self.refresh_plugins()

    # ---------------------------------------------------------------------- #
    #                           Creation Methods
    # ---------------------------------------------------------------------- #
    def create_treeview_context_menu(self):
        """
        This creates the tree-like view rendering the experiment heirachy.
        """
        self.treeview_popup = tk.Menu(self, tearoff=0)
        self.treeview_popup.add_command(
            label="Apply FASTQ...", command=self.apply_seqlib_fastq
        )

    def create_main_frame(self):
        """
        Large function creating all the basic elements of the main app frame.
        Creates the treeview and associated buttons, the scoring plugin frame
        and the go button.
        """
        # Frame for the Treeview and New/Edit/Delete buttons
        main = Frame(self, padding=(3, 3, 12, 12))
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0)
        main.grid(row=0, column=0, sticky="nsew")

        # ------------------------------------------------------- #
        # Frame for the Treeview and its scrollbars
        tree_frame = Frame(main, padding=(3, 3, 12, 12))
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.rowconfigure(1, weight=0)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.columnconfigure(1, weight=0)
        tree_frame.grid(row=0, column=0, sticky="nsew")

        # ------------------------------------------------------- #
        # Treeview with column headings
        self.treeview = Treeview(tree_frame)
        self.treeview["columns"] = ("class", "barcodes", "variants")
        self.treeview.column("class", width=120)
        self.treeview.heading("class", text="Type")
        self.treeview.column("barcodes", width=25, stretch=tk.NO, anchor=tk.CENTER)
        self.treeview.heading("barcodes", text="BC")
        self.treeview.column("variants", width=25, stretch=tk.NO, anchor=tk.CENTER)
        self.treeview.heading("variants", text="V")
        self.treeview.grid(row=0, column=0, sticky="nsew")

        # Treeview context menu bindings
        self.treeview.bind("<Button-2>", self.treeview_context_menu)

        # Treeview scrollbars
        tree_ysb = tk.Scrollbar(
            tree_frame, orient="vertical", command=self.treeview.yview
        )
        tree_xsb = tk.Scrollbar(
            tree_frame, orient="horizontal", command=self.treeview.xview
        )
        tree_ysb.grid(row=0, column=1, sticky="nsw")
        tree_xsb.grid(row=1, column=0, sticky="ewn")
        self.treeview.config(yscroll=tree_ysb.set, xscroll=tree_xsb.set)

        # ------------------------------------------------------- #
        # Frame for New/Edit/Delete buttons
        button_frame = Frame(main, padding=(3, 3, 12, 12))
        button_frame.grid(row=1, column=0)
        new_button = Button(button_frame, text="New...", command=self.new_button_press)
        new_button.grid(row=0, column=0)
        edit_button = Button(
            button_frame, text="Edit...", command=self.edit_button_press
        )
        edit_button.grid(row=0, column=1)
        delete_button = Button(
            button_frame, text="Delete", command=self.delete_button_press
        )
        delete_button.grid(row=0, column=2)

        self.treeview_buttons = [new_button, delete_button, edit_button]

        # ------------------------------------------------------- #
        # Frame for Plugin and Analysis Options
        right_frame = Frame(main, padding=(3, 3, 12, 12))
        right_frame.rowconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=0)
        right_frame.columnconfigure(0, weight=1)
        right_frame.columnconfigure(1, weight=0)
        right_frame.grid(row=0, column=1, sticky="new")

        # ------------------------------------------------------- #
        # LabelFrame for plugin and options
        scoring_plugin = ScorerScriptsDropDown(
            right_frame, text="Scoring Options", padding=(3, 3, 12, 12)
        )
        scoring_plugin.grid(row=0, column=0, sticky="new")
        self.scorer_widget = scoring_plugin

        # ------------------------------------------------------- #
        # LabelFrame for Analysis Options
        row = 0
        options_frame = LabelFrame(
            right_frame, text="Analysis Options", padding=(3, 3, 12, 12)
        )
        options_frame.grid(row=1, column=0, sticky="new", pady=4)

        # force recalculate
        force_recalculate = Checkbutton(
            options_frame, text="Force Recalculation", variable=self.force_recalculate
        )
        force_recalculate.grid(column=0, row=row, sticky="w")
        row += 1

        # component outliers
        component_outliers = Checkbutton(
            options_frame,
            text="Component Outlier Statistics",
            variable=self.component_outliers,
        )
        component_outliers.grid(column=0, row=row, sticky="w")
        row += 1

        # write tsv
        tsv_requested = Checkbutton(
            options_frame, text="Write TSV Files", variable=self.tsv_requested
        )
        tsv_requested.grid(column=0, row=row, sticky="w")
        tsv_requested.invoke()
        row += 1

        # ------------------------------------------------------- #
        # Run Analysis button frame
        go_button_frame = Frame(main, padding=(3, 3, 12, 12))
        go_button_frame.grid(row=1, column=1)
        go_button = Button(
            go_button_frame, text="Run Analysis", command=self.go_button_press
        )
        go_button.grid(column=0, row=0)
        self.go_button = go_button

    def create_new_element(self):
        """
        Create and return a new element based on the current selection.

        This element is not added to the treeview. 
        """
        element = None
        parent_element = self.get_focused_element()
        if isinstance(parent_element, Experiment):
            element = Condition()
            element.parent = parent_element
        elif isinstance(parent_element, Condition):
            element = Selection()
            element.parent = parent_element
        elif isinstance(parent_element, Selection):
            element = CreateSeqLibDialog(self).element_type()
            element.parent = parent_element
        elif isinstance(parent_element, SeqLib):
            # special case: creates a copy of the selected SeqLib as a sibling
            element = type(parent_element)()
            element.configure(parent_element.serialize())
            element.parent = parent_element.parent
            # clear out the seqlib-specific values
            element.name = None
            element.timepoint = None
            element.counts_file = None
            element.reads = None
        else:
            raise ValueError(
                "Unrecognized parent object " "type '{}'".format(type(parent_element))
            )
        return element

    def create_menubar(self):
        """
        Creates the menubar for the main app, with associated drop down menus.
        """
        # make platform-specific keybinds
        if platform.system() == "Darwin":
            accel_string = "Command+"
            accel_bind = "Command-"
        else:
            accel_string = "Ctrl+"
            accel_bind = "Control-"

        # create the menubar
        menubar = tk.Menu(self)

        # file menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(
            label="Open...",
            accelerator="{}O".format(accel_string),
            command=self.menu_open,
        )
        filemenu.add_command(
            label="Save", accelerator="{}S".format(accel_string), command=self.menu_save
        )
        filemenu.add_command(
            label="Save As...",
            accelerator="{}Shift+S".format(accel_string),
            command=self.menu_saveas,
        )
        menubar.add_cascade(label="File", menu=filemenu)

        # edit menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(
            label="Select All",
            accelerator="{}A".format(accel_string),
            command=self.menu_selectall,
        )
        menubar.add_cascade(label="Edit", menu=filemenu)

        # tools menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(
            label="Show Log",
            accelerator="{}L".format(accel_string),
            command=show_log_window,
        )
        filemenu.add_command(
            label="Plugin Sources",
            accelerator="{}P".format(accel_string),
            command=self.show_plugin_source_window,
        )
        filemenu.add_command(
            label="Refresh Plugins",
            accelerator="{}R".format(accel_string),
            command=self.refresh_plugins,
        )
        menubar.add_cascade(label="Tools", menu=filemenu)

        # add the menubar
        self.config(menu=menubar)

        # add file menu keybinds
        self.bind("<{}o>".format(accel_bind), lambda event: self.menu_open())
        self.bind("<{}s>".format(accel_bind), lambda event: self.menu_save())
        self.bind("<{}Shift-s>".format(accel_bind), lambda event: self.menu_saveas())

        # add edit menu keybinds
        self.bind("<{}a>".format(accel_bind), lambda event: self.menu_selectall())

        # add show log menu keybinds
        # add edit menu keybinds
        self.bind("<{}l>".format(accel_bind), lambda event: show_log_window())
        self.bind(
            "<{}p>".format(accel_bind), lambda event: self.show_plugin_source_window()
        )
        self.bind("<{}r>".format(accel_bind), lambda event: self.refresh_plugins())

    # ---------------------------------------------------------------------- #
    #                          Treeview Methods
    # ---------------------------------------------------------------------- #
    def treeview_context_menu(self, click):
        """
        Sets the currently selected treeview object id in the variable
        ``treeview_popup_target_id``.
        
        Parameters
        ----------
        click : 
            tkinter click event
        """
        target = self.treeview.identify_row(click.y)
        if target != "":
            self.treeview_popup_target_id = target
            self.treeview_popup.post(click.x_root, click.y_root)
        self.treeview_popup_target_id = None

    def apply_seqlib_fastq(self):
        """
        Applies settings to the seqlib object by running the configuration
        method.
        """
        SeqLibApplyDialog(self, self, self.treeview_popup_target_id)

    def new_button_press(self):
        """
        Spawns a dialog box depending on the currently selected treeview item
        to create a new element.
        """
        if self.treeview.focus() == "" and self.root_element is not None:
            tkinter.messagebox.showwarning(None, "No parent element selected.")
        else:
            if self.treeview.focus() == "" and self.root_element is None:
                element = CreateRootDialog(self).element
                if isinstance(element, SeqLib):
                    EditDialog(self, self, element)
                self.root_element = element
            else:
                element = self.create_new_element()
                EditDialog(self, self, element)

            # refresh the treeview and re-assign treeview id's
            self.refresh_treeview()

            # select the newly added element if it was successfully added
            if element.treeview_id in list(self.element_dict.keys()):
                self.treeview.focus(element.treeview_id)
                self.treeview.selection_set(element.treeview_id)
            else:
                if element.parent is not None:
                    self.treeview.focus(element.parent.treeview_id)
                    self.treeview.selection_set(element.parent.treeview_id)
                del element

    def edit_button_press(self):
        """
        Spawns a dialog box depending on the currently selected treeview item
        to edit the selected element.
        """
        if self.treeview.focus() == "":
            tkinter.messagebox.showwarning(None, "No element selected.")
        else:
            EditDialog(self, self, self.get_focused_element())

    def delete_button_press(self):
        """
        Deletes the selected treeview element and it's children.
        """
        if self.treeview.focus() == "":
            tkinter.messagebox.showwarning(None, "No element selected.")
        else:
            DeleteDialog(self, self)

    def delete_element(self, tree_id):
        """
        Delete element with Treeview id *tree_id* from the tree, from the 
        element dictionary, and from the associated data structure. Recursively 
        deletes all children of *tree_id*.

        The tree should be refreshed using :py:meth:`refresh_tree` after 
        each deletion. This is the responsibility of the caller.

        Parameters
        ----------
        tree_id : `int`
            The id of the currently selected treeview element.

        """
        if tree_id in self.element_dict:
            # recursively delete children
            if self.element_dict[tree_id].children is not None:
                for child in self.element_dict[tree_id].children:
                    self.delete_element(child.treeview_id)

            # check if deleting the root element
            if self.root_element.treeview_id == tree_id:
                # clear the root element
                print("None {}".format(tree_id))
                self.root_element = None
            else:
                try:
                    # remove the element from its parent's list of children
                    self.element_dict[tree_id].parent.remove_child_id(tree_id)
                except AttributeError:
                    raise AttributeError("Non-root element lacks proper parent")

            # delete the element from the dictionary
            del self.element_dict[tree_id]

    def refresh_treeview(self):
        """
        Clears the Treeview and repopulates it with the 
        current contents of the tree.
        """
        # clear the entries in the Treeview
        for x in self.treeview.get_children():
            self.treeview.delete(x)

        # clear the id-element dictionary
        # elements may be given new id's after repopulation
        self.element_dict.clear()

        # repopulate
        if self.root_element is not None:
            self.populate_tree(self.root_element)

    def set_treeview_properties(self, element):
        """
        Set the information text for the Treeview *element*.

        Parameters
        ----------
        element : :py:class:`~enrich2.base.storemanager.StoreManager`
            The storemanager object to configure.
        """
        # set class property
        self.treeview.set(element.treeview_id, "class", element.treeview_class_name)

        # add the check marks for barcodes/variants
        if "variants" in element.labels:
            self.treeview.set(element.treeview_id, "variants", u"\u2713")
        else:
            self.treeview.set(element.treeview_id, "variants", "")
        if "barcodes" in element.labels:
            self.treeview.set(element.treeview_id, "barcodes", u"\u2713")
        else:
            self.treeview.set(element.treeview_id, "barcodes", "")

        self.treeview.set(element.treeview_id, "class", element.treeview_class_name)

    def populate_tree(self, element, parent_id=""):
        """
        Recursively populate the Treeview.

        Also populates the *id_cfgstrings*.

        Parameters
        ----------
        element : :py:class:`~enrich2.base.storemanager.StoreManager`
            The storemanager object to configure.
        parent_id : `int`
            ``treeview_id`` of element's parent.
        """
        # insert into the Treeview
        element.treeview_id = self.treeview.insert(
            parent_id, "end", text=element.name, open=True
        )
        # add id-element pair to dictionary
        self.element_dict[element.treeview_id] = element
        # set information fields
        self.set_treeview_properties(element)

        # populate for children
        if element.children is not None:
            for child in element.children:
                self.populate_tree(child, parent_id=element.treeview_id)

    # ---------------------------------------------------------------------- #
    #                          Getter Methods
    # ---------------------------------------------------------------------- #
    def get_selected_scorer_class(self):
        """
        Returns the currently selected scoring class object.
        """
        return self.scorer

    def get_selected_scorer_attrs(self):
        """
        Returns the currently selected scoring class attribute `dict`.
        """
        return self.scorer_attrs

    def get_selected_scorer_path(self):
        """
        Returns the currently selected scoring path.
        """
        return self.scorer_path

    def get_element(self, treeview_id):
        """
        Returns the element with *treeview_id*.

        Parameters
        ----------
        treeview_id : `int`
            ``treeview_id`` attribute of element to get.

        Returns
        -------
        :py:class:`~enrich2.base.storemanager.StoreManager`
            The instance with matching ``treeview_id``

        """
        return self.element_dict[treeview_id]

    def get_focused_element(self):
        """
        Gets the focused element in the treeview.

        Returns
        -------
        :py:class:`~enrich2.base.storemanager.StoreManager`
            Returns the element that is currently being focused in the 
            Treeview. ``None`` if nothing is focused.
        """
        if self.treeview.focus() != "":
            return self.get_element(self.treeview.focus())
        else:
            return None

    def get_selected_elements(self):
        """
        Returns a list of currently selected elements in the treeview.

        Returns
        -------
        `list`
            Returns a list of elements that are currently selected in the 
            Treeview. If no elements are selected, it returns an empty list.

        """
        return [self.get_element(x) for x in self.treeview.selection()]

    # ---------------------------------------------------------------------- #
    #                          Menubar Methods
    # ---------------------------------------------------------------------- #
    def menu_open(self):
        """
        Spawns an `askopenfilename` dialog to open a configuration file.
        """
        message_title = "Open Configuration"
        fname = tkinter.filedialog.askopenfilename()
        if len(fname) > 0:  # file was selected
            try:
                with open(fname, "rU") as handle:
                    cfg = json.load(handle)
            except ValueError:
                tkinter.messagebox.showerror(
                    message_title, "Failed to parse config file."
                )
            except IOError:
                tkinter.messagebox.showerror(
                    message_title, "Could not read config file."
                )
            else:
                if is_experiment(cfg):
                    obj = Experiment()
                elif is_selection(cfg):
                    obj = Selection()
                elif is_seqlib(cfg):
                    sltype = seqlib_type(cfg)
                    obj = globals()[sltype]()
                else:
                    tkinter.messagebox.showerror(
                        message_title, "Unrecognized config format."
                    )
                    return
                obj.output_dir_override = False
                try:
                    if isinstance(obj, Experiment) or isinstance(obj, Selection):
                        obj.configure(cfg, init_from_gui=True)
                    else:
                        obj.configure(cfg)

                    # Try load the scorer into the GUI
                    scorer_path = cfg.get(SCORER, {}).get(SCORER_PATH, "")
                    scorer_attrs = cfg.get(SCORER, {}).get(SCORER_OPTIONS, {})
                    if scorer_path:
                        self.scorer_widget.load_from_cfg_file(scorer_path, scorer_attrs)
                    else:
                        log_message(
                            logging_callback=logging.warning,
                            msg="No plugin could be loaded from configuration.",
                            extra={"oname": self.__class__.__name__},
                        )

                except Exception as e:
                    tkinter.messagebox.showerror(
                        message_title, "Failed to load config file:\n\n{}".format(e)
                    )
                else:
                    self.root_element = obj
                    self.cfg_file_name.set(fname)
                    self.refresh_treeview()

    def menu_save(self):
        """
        Asks the user where to save the current configuration.
        """
        if len(self.cfg_file_name.get()) == 0:
            self.menu_saveas()
        elif self.root_element is None:
            tkinter.messagebox.showwarning(
                "Save Configuration", "Cannot save empty configuration."
            )
        else:
            save = askyesno("Save Configuration", "Overwrite existing configuration?")
            if not save:
                return
            try:
                with open(self.cfg_file_name.get(), "w") as handle:
                    cfg = self.root_element.serialize()

                    # Get the currently selected scorer
                    if not isinstance(self.root_element, SeqLib) and not isinstance(
                        self.root_element, Condition
                    ):
                        (
                            _,
                            attrs,
                            scorer_path,
                        ) = self.scorer_widget.get_scorer_class_attrs_path()
                        cfg[SCORER] = {SCORER_PATH: scorer_path, SCORER_OPTIONS: attrs}
                    write_json(cfg, handle)
            except IOError:
                tkinter.messagebox.showerror(
                    "Save Configuration", "Failed to save config file."
                )
            else:
                tkinter.messagebox.showinfo(
                    "Save Configuration",
                    "Saved file at location:\n\n{}".format(self.cfg_file_name.get()),
                )

    def menu_saveas(self):
        """
        Asks the user where to save the current configuration.
        """
        if self.root_element is None:
            tkinter.messagebox.showwarning(
                "Save Configuration", "Cannot save empty configuration."
            )
        else:
            fname = tkinter.filedialog.asksaveasfilename()
            if len(fname) > 0:  # file was selected
                try:
                    with open(fname, "w") as handle:
                        cfg = self.root_element.serialize()

                        # Get the currently selected scorer
                        if not isinstance(self.root_element, SeqLib) and not isinstance(
                            self.root_element, Condition
                        ):
                            (
                                _,
                                attrs,
                                scorer_path,
                            ) = self.scorer_widget.get_scorer_class_attrs_path()
                            cfg[SCORER] = {
                                SCORER_PATH: scorer_path,
                                SCORER_OPTIONS: attrs,
                            }
                        write_json(cfg, handle)
                except IOError:
                    tkinter.messagebox.showerror(
                        "Save Configuration", "Failed to save config file."
                    )
                else:
                    self.cfg_file_name.set(fname)
                    tkinter.messagebox.showinfo(
                        "Save Configuration",
                        "Saved file at location:\n\n{}".format(
                            self.cfg_file_name.get()
                        ),
                    )

    def menu_selectall(self):
        """
        Add all elements in the Treeview to the selection.
        """
        for k in self.element_dict.keys():
            self.treeview.selection_add(k)

    def show_plugin_source_window(self):
        """
        Show the pop-up window to modify plugin sources
        """
        if not self.plugin_source_window:
            self.plugin_source_window = SourceWindow(master=self)
        else:
            self.plugin_source_window.toggle_show()

    # ---------------------------------------------------------------------- #
    #                         Run Analysis Methods
    # ---------------------------------------------------------------------- #
    def go_button_press(self):
        """
        Starts the analysis if all elements have been properly configured.
        This will run the analysis in a new thread and block out GUI editing 
        to prevent the analysis breaking.
        """
        (
            self.scorer,
            self.scorer_attrs,
            self.scorer_path,
        ) = self.scorer_widget.get_scorer_class_attrs_path()

        if self.scorer is None or self.scorer_attrs is None:
            tkinter.messagebox.showwarning(
                "Incomplete Configuration", "No scoring plugin selected."
            )
        elif self.root_element is None:
            tkinter.messagebox.showwarning(
                "Incomplete Configuration", "No experimental design specified."
            )
        else:
            plugin, *_ = self.scorer_widget.get_selected_plugin()
            if plugin.md5_has_changed():
                proceed = askokcancel(
                    "Selected plugin has been modified.",
                    "The selected plugin has been modified on disk. Do you "
                    "want to proceed with the current version? To see changes "
                    "click 'Cancel' and refresh plugins before proceeding.",
                )
                if not proceed:
                    return
            if askyesno(
                "Save Configuration?",
                "Would you like to save the confiugration " "file before proceeding?",
            ):
                self.menu_save()
            run = askyesno(
                "Begin Analysis?",
                "Click Yes when you are ready to start.\n\nThis could "
                "take some time so grab a cup of tea, or a beer if that's "
                "your thing, and enjoy the show.",
            )
            if run:
                self.configure_analysis()
                self.set_gui_state(tk.DISABLED)
                thread = threading.Thread(target=self.run_analysis)
                thread.setDaemon(True)
                self.analysis_thread = thread
                self.analysis_thread.start()
                self.after(100, self.poll_analysis_thread)

    def poll_logging_queue(self):
        """
        Polls the logging queue for messages to log.
        """
        try:
            log = get_logging_queue(init=True).get(0)
            log[CALLBACK](log[MESSAGE], **log[KWARGS])
            self.after(10, self.poll_logging_queue)
        except queue.Empty:
            self.after(10, self.poll_logging_queue)

    def poll_analysis_thread(self):
        """
        Polls the thread to check it's state. When it is finished, all stores
        are closed.
        """
        try:
            analysis_result = self.queue.get(0)
            self.handle_analysis_result(analysis_result)
        except queue.Empty:
            self.after(100, self.poll_analysis_thread)

    def handle_analysis_result(self, success):
        """
        Shows the appropriate messagebox and logs exceptions upon analysis
        completing.
        
        Parameters
        ----------
        success : `bool`
            Exception object if an error occured during analysis, otherwise
            None to indicate successful computation.
        """
        log_message(
            logging_callback=logging.info,
            msg="Closing stores...",
            extra={"oname": self.root_element.name},
        )
        self.root_element.store_close(children=True)
        log_message(
            logging_callback=logging.info,
            msg="Stores closed.",
            extra={"oname": self.root_element.name},
        )

        if success:
            showinfo("Analysis completed.", "Analysis has completed successfully!")
            log_message(
                logging_callback=logging.info,
                msg="Completed successfully!",
                extra={"oname": self.root_element.name},
            )
        else:
            showwarning(
                "Error during analysis.",
                "An error occurred during the analysis. See log for details",
            )
            log_message(
                logging_callback=logging.info,
                msg="Completed, but with errors!",
                extra={"oname": self.root_element.name},
            )
        self.set_gui_state(tk.NORMAL)

    def run_analysis(self):
        """
        Runs the storemanager compute method.
        """
        try:
            self.root_element.validate()
            self.root_element.store_open(children=True)
            self.root_element.calculate()
            if self.root_element.tsv_requested:
                self.root_element.write_tsv()
            self.queue.put(True, block=False)
        except Exception as exception:
            log_message(
                logging_callback=logging.exception,
                msg=exception,
                extra={"oname": self.root_element.name},
            )
            self.queue.put(False, block=False)
        finally:
            return

    def configure_analysis(self):
        """
        Configures the attributes of the root_element by querying the GUI
        options.
        """
        try:
            self.root_element.force_recalculate = self.force_recalculate.get()
            self.root_element.component_outliers = self.component_outliers.get()
            self.root_element.tsv_requested = self.tsv_requested.get()

            scorer_class = self.get_selected_scorer_class()
            scorer_class_attrs = self.get_selected_scorer_attrs()
            scorer_path = self.get_selected_scorer_path()
            self.root_element.scorer_class = scorer_class
            self.root_element.scorer_class_attrs = scorer_class_attrs
            self.root_element.scorer_path = scorer_path
        except Exception as e:
            log_message(
                logging_callback=logging.info,
                msg="An error occurred when trying to configure the " "root element.",
                extra={"oname": self.root_element.name},
            )
            log_message(
                logging_callback=logging.exception,
                msg=e,
                extra={"oname": self.root_element.name},
            )

    # ---------------------------------------------------------------------- #
    #                         GUI Modifications
    # ---------------------------------------------------------------------- #
    def set_gui_state(self, state):
        """
        Sets the state of the `go_button`, `treeview` and `treeview_buttons`.

        Parameters
        ----------
        state : `str`
            State to set, usually ``'normal'`` or ``'disabled'``

        """
        for btn in self.treeview_buttons:
            btn.config(state=state)
        self.go_button.config(state=state)
        if state == "normal":
            self.treeview.bind("<Button-2>", self.treeview_context_menu)
        else:
            self.treeview.bind("<Button-2>", lambda event: event)

    def refresh_plugins(self):
        """
        Refresh the plugins by re-checking the sources file.
        """
        if self.plugin_source_window:
            sources = self.plugin_source_window.sources
            self.scorer_widget.refresh_sources(sources)
