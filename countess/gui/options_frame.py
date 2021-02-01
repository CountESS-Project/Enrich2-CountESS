import os
import glob
import json
import logging
from tkinter import *
import tkinter.ttk as ttk
from collections import Iterable
import tkinter.messagebox as messagebox
from tkinter.filedialog import askopenfilename, asksaveasfile

from ..base.config_constants import SCORER_OPTIONS, SCORER_PATH

from ..plugins.options import Options
from ..plugins.options import options_not_in_config
from ..plugins.options import get_unused_options
from ..base.utils import nested_format, log_message

from .plugin_source_window import parse_sources
from .plugin import Plugin


LabelFrame = ttk.LabelFrame
Frame = ttk.Frame
Label = ttk.Label
Entry = ttk.Entry
Button = ttk.Button
Checkbutton = ttk.Checkbutton
OptionMenu = ttk.OptionMenu


# -------------------------------------------------------------------------- #
#                Editable Options (Visible/Invisible) Frame
# -------------------------------------------------------------------------- #
class OptionsFrame(Frame, Iterable):
    """
    This class represents an independent Frame object which renders and 
    handles the setting of options defined in a script file.
    
    Parameters
    ----------
    parent : :py:class:`tkinter.ttk.Frame` or :py:class:`~tkinter.TopLevel`
        The parent frame or window.
    options : :py:class:`~enrich2.plugins.options.Options`
        The options this frame should manage.
    kw : `dict`
        Keyword arguments for the Frame class.
        
    Attributes
    ----------
    parent : :py:class:`tkinter.ttk.Frame` or :py:class:`~tkinter.TopLevel`
        The parent frame or window.
    row : `int`
        The row number used for grid/packing.
    options : :py:class:`~enrich2.plugins.options.Options`
        The options this frame should manage.
    vname_tkvars_map : `dict`
        A mapping of option variable names to their corresponding tk-variable.
        
    Methods
    -------
    parse_options
        Parses a :py:class:`~enrich2.plugins.options.Options` instance.
        If an option is visible, it creates an appropriate widget based
        on it's data type to render in the GUI.
    create_widget_from_option
        Creates a GUI widget based on the data-type of the supplied option.
        Each deligated function creates a tk-variable that is mapped to 
        in *vname_tkvars_map*.
    make_choice_menu_widget
        Creates drop-down menu for an option that contains choices.
    make_entry
        Creates a general text-entry widget for an option.
    make_bool_entry_widget
        Creates a boolean tick-box widget for an option.
    make_string_entry_widget
        Creates a string entry widget for an option.
    make_int_entry_widget
        Creates an int entry widget for an option.
    make_float_entry_widget
        Creates a float entry widget for an option.
    set_validate
        Attempts to set both an option indexed in the ``options`` attribute
        by *varname* and the corresponding tk variable with value.
    get_option_by_varname
        Get the instance of an option with the variable name *varname*
    set_option
        Attempts to set an option indexed in the ``options`` attribute
        by *varname* with value.       
    set_variable
        Attempts to set a tk variable indexed in the ``vname_tkvar_map`` 
        attribute by *varname* with value.      
    get_option_cfg
        Returns a dictionary of all options managed by this instance. Keys
        are the option variable names *varname* and values are a 
        tuple of (option value, boolean), the boolean indicating if the value
        is the same as the default for an option.
    has_options
        Returns True if the options managed by this instance contains options.
    
    See Also
    --------
    :py:class:`~tkinter.ttk.Frame`
    :py:class:`~collections.Iterable`
    """

    def __init__(self, parent, options, **kw):
        Frame.__init__(self, parent, **kw)
        Iterable.__init__(self)
        self.parent = parent
        self.row = 0

        self.options = Options() if options is None else options
        self.vname_tkvars_map = {}

        if options is not None:
            self.parse_options(options)
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=3)

    def __iter__(self):
        return iter(list(self.options.keys()))

    def parse_options(self, options):
        """
        Parses a :py:class:`~enrich2.plugins.options.Options` instance.
        If an option is visible, it creates an appropriate widget based
        on it's data type to render in the GUI.
        
        Parameters
        ----------
        options : :py:class:`~enrich2.plugins.options.Options`
            The options object to parse.
        """
        if not len(options):
            label_text = "No options found."
            label = Label(self, text=label_text, justify=LEFT)
            label.grid(sticky=EW, columnspan=1, row=self.row)
            self.rowconfigure(self.row, weight=1)
            self.row += 1

        for option in options.get_visible_options():
            self.create_widget_from_option(option)
            self.rowconfigure(self.row, weight=1)
            self.row += 1
        return

    def create_widget_from_option(self, option):
        """
        Creates a GUI widget based on the data-type of the supplied option.
        Each deligated function creates a tk-variable that is mapped to 
        in *vname_tkvars_map*.
        
        Parameters
        ----------
        option : :py:class:`~enrich2.plugins.options.Option`
            The option to create a widget for.
        """
        if option.choices:
            self.make_choice_menu_widget(option)
        elif option.dtype in (str, "string", "char", "chr"):
            self.make_string_entry_widget(option)
        elif option.dtype in ("integer", "int", int):
            self.make_int_entry_widget(option)
        elif option.dtype in ("float", float):
            self.make_float_entry_widget(option)
        elif option.dtype in ("bool", bool, "boolean"):
            self.make_bool_entry_widget(option)
        else:
            raise ValueError(
                "Unrecognised attribute in option " "dtype {}.".format(option.dtype)
            )

    def make_choice_menu_widget(self, option):
        """
        Creates drop-down menu for an option that contains choices.

        Parameters
        ----------
        option : :py:class:`~enrich2.plugins.options.Option`
            The option to create the widget for.
        """
        variable = StringVar(self)
        variable.set(option.get_default_value())

        label_text = "{}: ".format(option.name)
        label = Label(self, text=label_text, justify=LEFT)
        label.grid(sticky=EW, column=0, row=self.row)

        choices = option.choices
        choices = list(choices.keys())

        vname = option.varname
        set_func = lambda _, y=variable, x=vname: self.set_validate(x, y.get())
        popup_menu = OptionMenu(
            self, variable, option.get_choice_key(), *choices, command=set_func
        )
        popup_menu.grid(sticky=E, column=1, row=self.row)
        self.vname_tkvars_map[option.varname] = variable

    def make_entry(self, variable, option):
        """
        Creates a general text-entry widget for an option.

        Parameters
        ----------
        variable : A tkinter variable
            A variable that should be linked to the *varname* of the option
            so that modifications can be accessed easily.
        option : :py:class:`~enrich2.plugins.options.Option`
            The option to create the widget for.
        """
        label_text = "{}: ".format(option.name)
        label = Label(self, text=label_text, justify=LEFT)
        label.grid(sticky=EW, column=0, row=self.row)

        def validate():
            bad_input_msg = "Error validating input for entry {}:\n\n{}"
            varname = option.varname
            try:
                value = variable.get()
                self.set_variable(varname, value)
                self.set_option(varname, value)
            except (TclError, TypeError, KeyError, ValueError) as error:
                variable.set(option.dtype(option.get_value()))
                messagebox.showwarning(
                    title="Error setting option '{}'".format(varname),
                    message=bad_input_msg.format(varname, error),
                )
                return False
            return True

        entry = Entry(
            self, textvariable=variable, validate="focusout", validatecommand=validate
        )
        entry.grid(sticky=EW, column=1, row=self.row)
        self.vname_tkvars_map[option.varname] = variable
        return entry

    def make_bool_entry_widget(self, option):
        """
        Creates a boolean tick-box widget for an option.

        Parameters
        ----------
        option : :py:class:`~enrich2.plugins.options.Option`
            The option to create the widget for.
        """
        variable = BooleanVar(self)
        variable.set(option.get_default_value())

        label_text = "{}: ".format(option.name)
        label = Label(self, text=label_text, justify=LEFT)
        label.grid(sticky=EW, column=0, row=self.row)

        vname = option.varname
        set_func = lambda x=vname, y=variable: self.set_validate(x, y.get())
        checkbox = Checkbutton(self, variable=variable, command=set_func)
        checkbox.grid(sticky=E, column=1, row=self.row)
        self.vname_tkvars_map[option.varname] = variable

    def make_string_entry_widget(self, option):
        """
        Creates a string entry widget for an option.

        Parameters
        ----------
        option : :py:class:`~enrich2.plugins.options.Option`
            The option to create the widget for.
        """
        variable = StringVar(self)
        variable.set(option.dtype(option.get_default_value()))
        self.make_entry(variable, option)

    def make_int_entry_widget(self, option):
        """
        Creates an int entry widget for an option.

        Parameters
        ----------
        option : :py:class:`~enrich2.plugins.options.Option`
            The option to create the widget for.
        """
        variable = IntVar(self)
        variable.set(option.dtype(option.get_default_value()))
        self.make_entry(variable, option)

    def make_float_entry_widget(self, option):
        """
        Creates a float entry widget for an option.

        Parameters
        ----------
        option : :py:class:`~enrich2.plugins.options.Option`
            The option to create the widget for.
        """
        variable = DoubleVar(self)
        variable.set(option.dtype(option.get_default_value()))
        self.make_entry(variable, option)

    def set_validate(self, varname, value):
        """
        Attempts to set both an option indexed in the ``options`` attribute
        by *varname* and the corresponding tk variable with value.

        Parameters
        ----------
        varname : `str`
            The key of the option to set with *value* and validate.
        value : `Any`
            Value to validate and set the option with
            
        Returns
        -------
        `bool` 
            A boolean indicating if the value could be successfully
            validated and set.
        """
        bad_input_msg = "Error validating input for entry {}:\n\n{}"
        try:
            self.set_variable(varname, value)
            self.set_option(varname, value)
        except (KeyError, TclError, TypeError, ValueError) as error:
            option = self.get_option_by_varname(varname)
            self.set_variable(varname, option.get_value())
            messagebox.showwarning(
                title="Error setting option!",
                message=bad_input_msg.format(varname, error),
            )
            return False
        return True

    def get_option_by_varname(self, varname):
        """
        Get the instance of an option with the variable name *varname*
        
        Returns
        -------
        :py:class:`~enrich2.plugins.options.Option`
            The option with varname equal to *varname*
        """
        option = self.options.get(varname, None)
        if option is None:
            raise KeyError(
                "No option with the variable name '{}' could "
                "be found".format(varname)
            )
        return option

    def set_option(self, varname, value):
        """
        Attempts to set an option indexed in the ``options`` attribute
        by *varname* with value.
        
        Parameters
        ----------
        varname : `str`
            The key of the option to set with *value* and validate.
        value : `Any`
            Value to validate and set the option with
        """
        option = self.get_option_by_varname(varname)
        option.set_value(value)

    def set_variable(self, varname, value):
        """
        Attempts to set a tk variable indexed in the ``vname_tkvar_map`` 
        attribute by *varname* with value.

        Parameters
        ----------
        varname : `str`
            The key of the option to set with *value* and validate.
        value : `Any`
            Value to validate and set the option with
        """
        variable = self.vname_tkvars_map.get(varname, None)
        if variable is not None:
            variable.set(value)

    def get_option_cfg(self):
        """
        Returns a dictionary of all options managed by this instance. Keys
        are the option variable names *varname* and values are a 
        tuple of (option value, boolean), the boolean indicating if the value
        is the same as the default for an option.
        
        Returns
        -------
        `dict`
            Option configuration dictionary.
        """
        cfg = {}
        for varname, opt in self.options.items():
            value = opt.get_value()
            default = opt.get_default_value()
            opt.validate(value)
            cfg[varname] = (value, value == default)
        return cfg

    def has_options(self):
        """
        Returns True if the options managed by this instance contains options.
        
        Returns
        -------
        `bool`
            True if ``options`` is not empty.
        """
        return self.options.has_options()


# -------------------------------------------------------------------------- #
#                        Frame for File Handling
# -------------------------------------------------------------------------- #
class OptionsFileFrame(Frame):
    """
    This class represents a Frame subclass which manages the loading of
    option configuration files. If this instance is linked to a 
    :py:class:`~OptionsFrame` then loading a configuration file will
    attempt to match up the options in that frame to the ones found
    in parsed configuration file, and handle the validation/setting of these
    options.
    
    Parameters
    ----------
    parent : :py:class:`tkinter.ttk.Frame` or :py:class:`~tkinter.TopLevel`
        The parent frame or window.
    options_file : :py:class:`~enrich2.plugins.options.OptionsFile`
        The options file instance to parse/validate options files with.
    config : `dict`
        Keyword arguments to pass into Frame __init__
    
    Attributes
    ----------
    row : `int`
        The row number used for grid/packing.
    active_cfg : `dict`
        A dictionary of option variable names and their corresponding
        values.
    options_frame : :py:class:`~OptionsFrame`
        A linked options frame. ``None`` if it doesn't exist.
    options_file : :py:class:`~enrich2.plugins.options.OptionsFile`
        The options file instance to parse/validate options files with.
    
    Methods
    -------
    _make_widgets
        Makes the widgets for this Frame
    _make_label
        Makes a label widget with text being the name of the options_file
        attribute.
    _make_button
        Makes the load button.
    load_from_file
        Load a configuration file from disk. 
    apply_to_options
        Applies a loaded a configuration file from disk. Handles the cases 
        where unknown options have been found that do not match any options
        in `options_frame`, parsed options could not be validated, or there
        are missing options from the file that are in the `options_frame`.
    options_file_incomplete
        Returns a list of missing options from a configuration file
        that exist in the linked options frame.
    update_option_frame : 
        Given a dictionary of option varname-value pairs, attempts to update
        the options and tk-variables in the linked `options_frame`.
    get_option_cfg
        Returns the configuration loaded previously from a config file.
    link_to_options_frame
        Links this instance to an existing options frame.
    
    See Also
    --------
    :py:class:`~OptionsFrame`
    :py:class:`~tkinter.ttk.Frame`
    """

    def __init__(self, parent, options_file=None, **config):
        super().__init__(parent, **config)
        self.row = 0
        self.active_cfg = {}
        self.options_frame = None
        self.options_file = options_file
        if options_file is not None:
            self._make_widgets()
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=3)

    def _make_widgets(self):
        """
        Makes the widgets for this Frame.
        """
        self._make_label()
        self._make_button()
        self.rowconfigure(self.row, weight=1)
        self.row += 1

    def _make_label(self):
        """
        Makes a label widget with text being the name of the options_file
        attribute.
        """
        label_text = "{}: ".format(self.options_file.name)
        label = Label(self, text=label_text, justify=LEFT)
        label.grid(row=self.row, column=0, sticky=EW)

    def _make_button(self):
        """
        Makes the load button.
        """
        button = Button(self, text="Load...", command=self.load_from_file)
        button.grid(row=self.row, column=1, sticky=E)

    def load_from_file(self):
        """
        Load a configuration file from disk. 
        """
        file_path = askopenfilename()
        if not file_path:
            return

        self.active_cfg = {}
        cfg_error_msg = (
            "There was an error parsing file {}. "
            "\n\nPlease see log for details.".format(file_path)
        )
        validation_error_msg = (
            "There was an error during validation. " "\n\nPlease see log for details."
        )
        try:
            cfg = self.options_file.parse_to_dict(file_path)
        except BaseException as error:
            log_message(
                logging_callback=logging.exception,
                msg=error,
                extra={"oname": self.__class__.__name__},
            )
            messagebox.showerror("Parse Error", cfg_error_msg)
            return

        try:
            self.options_file.validate_cfg(cfg)
        except BaseException as error:
            log_message(
                logging_callback=logging.exception,
                msg=error,
                extra={"oname": self.__class__.__name__},
            )
            messagebox.showerror("Validation Error", validation_error_msg)
            return

        self.active_cfg = cfg
        self.apply_to_options()

    def apply_to_options(self):
        """
        Applies a loaded a configuration file from disk. Handles the cases 
        where unknown options have been found that do not match any options
        in `options_frame`, parsed options could not be validated, or there
        are missing options from the file that are in the `options_frame`.
        """
        success = "Successfully applied configuration file to plugin options."
        if not self.options_frame:
            messagebox.showwarning(
                "Apply Configuration Warning",
                "No options have been defined in this plugin. Cannot apply"
                "loaded configuration.",
            )
            return

        if not self.active_cfg:
            messagebox.showwarning(
                "Apply Configuration Warning",
                "No configuration file has been loaded. Please load one first.",
            )
            return

        warn_message = ""
        unused_keys = get_unused_options(self.active_cfg, self.options_frame.options)
        incomplete = self.options_file_incomplete()
        self.active_cfg = {
            k: v for (k, v) in self.active_cfg.items() if k not in unused_keys
        }

        if unused_keys:
            unused = "\n".join(["'{}'".format(n) for n in unused_keys])
            warn_message += (
                "The following options found in the configuration"
                "file are not defined in the current plugin and "
                "will not be used during analysis:\n\n{}\n\n"
            )
            warn_message = warn_message.format(unused)

        if incomplete:
            incomplete = "\n".join(["'{}'".format(n) for n in incomplete])
            warn_message += (
                "The following options defined in the plugin "
                "could not be found in the configuration file:"
                "\n\n{}\n\nThese options will not been altered."
            )
            warn_message = warn_message.format(incomplete)

        if warn_message:
            messagebox.showwarning("Apply configuration to options.", warn_message)

        applied_successfully = self.update_option_frame(self.active_cfg)
        if applied_successfully and not warn_message:
            messagebox.showinfo("Apply configuration to options.", success)
        return

    def options_file_incomplete(self):
        """
        Returns a list of missing options from a configuration file
        that exist in the linked options frame.
        """
        missing = []
        if self.options_frame and self.active_cfg:
            missing = options_not_in_config(self.active_cfg, self.options_frame.options)
            if missing:
                return [opt.varname for opt in missing]
            return missing
        return missing

    def update_option_frame(self, cfg):
        """
        Given a dictionary of option varname-value pairs, attempts to update
        the options and tk-variables in the linked `options_frame`.
        
        Parameters
        ----------
        cfg : `dict`
            Dictionary of option `varname`-value pairs to update the 
            options_frame with
        """
        current = []
        for varname, value in cfg.items():
            bad_input_msg = (
                "The following error occured when validating"
                " option with variable name '{}':\n\n{}\n\n"
                "Loading the specified configuration has been "
                "aborted. Please supply a correct configuration "
                "file before proceeding. No changes "
                "have been made."
            )
            try:
                option = self.options_frame.get_option_by_varname(varname)
                current.append((varname, option.get_value()))
                self.options_frame.set_option(varname, value)
                if option.choices:
                    self.options_frame.set_variable(varname, option.get_choice_key())
                else:
                    self.options_frame.set_variable(varname, option.get_value())
            except (KeyError, TclError, TypeError, ValueError) as error:
                for varname, old_val in current:
                    self.options_frame.set_option(varname, old_val)
                    option = self.options_frame.get_option_by_varname(varname)
                    if option.choices:
                        self.options_frame.set_variable(
                            varname, option.get_choice_key()
                        )
                    else:
                        self.options_frame.set_variable(varname, option.get_value())
                messagebox.showwarning(
                    title="Error setting option!",
                    message=bad_input_msg.format(varname, error),
                )
                log_message(
                    logging_callback=logging.exception,
                    msg=error,
                    extra={"oname": self.__class__.__name__},
                )
                return False
        return True

    def get_option_cfg(self):
        """
        Returns the configuration loaded previously from a config file.
        
        Returns
        -------
        `dict`
            Loaded configuration dictionary.
        """
        return self.active_cfg

    def link_to_options_frame(self, options_frame: OptionsFrame):
        """
        Links this instance to an existing options frame.
        
        Parameters
        ----------
        options_frame : :py:class:`~OptionsFrame`
            Options frame to link this instance to.
        """
        self.options_frame = options_frame


# -------------------------------------------------------------------------- #
#                           Main GUI Frame
# -------------------------------------------------------------------------- #
DUMMY_NAME = "Choose a plugin..."


class ScorerScriptsDropDown(LabelFrame):
    """
    This class represents the Frame containing a currently selected plugin
    in the GUI and it's associated editable options, if there are any.
    
    Parameters
    ----------
    parent : `object`
        Tkinter object which is the master of this frame 
    scripts_dir : `str`
        Directory for containing Enrich2 plugins.
        
    Attributes
    ----------
    row : `int`
        The row number used for grid/packing.
    current_view : `str`
        The name of the current selected plugin.
    btn_frame : :py:class:`~tkinter.ttk.Frame`
        The frame housing the buttons of this GUI widget.
    drop_menu_tkvar : :py:class:`~tkinter.StringVar`
        Tk variable linked to the drop-down plugin menu.
    drop_menu : :py:class:`tkinter.ttk.OptionMenu`
    plugins : `dict`
        A dictionary of plugins objects indexed by their name attribute.
    
    Methods
    -------
    load_from_cfg_file
        Load a plugin which has been specified in a configuration file.
        If a plugin already exists, the plugin view will be updated otherwise
        a new plugin view will be created.
    _parse_directory
        Parses a directory into plugins stored in the plugins dictionary.
    parse_file
        Parse a plugin file located at path into 
        :py:class:`~enrich2.plugins.scoring.BaseScorerPlugin`,
        :py:class:`~enrich2.plugins.options.Options` and 
        :py:class:`~enrich2.plugins.options.OptionsFile` objects.    
    plugin_hash
        Generate a hash key based on name, authors, version and path.
    plugin_exists
        Check if a plugin exist based on name, authors, version and path.
    get_plugin_gui_name
        Returns the name the GUI uses to render the plugin in the drop down.
    add_plugin
        Add a plugin to the plugins dictionary. Creates a unique name
        for the GUI if there are name collisions using the name defined in
        the class being added.
    make_options_frames
        Creates the :py:class: `~OptionsFrame` and 
        :py:class: `~OptionsFileFrame` from 
        :py:class: `~enrich2.plugins.options.Options` and 
        :py:class: `~enrich2.plugins.options.OptionsFile`         
    make_widgets
        Make the drop-down menu and label.
    make_drop_down_widget
        Make the drop-down menu.    
    make_buttons
        Make the print to log and save as buttons for interacting with a 
        plugin.
    increment_row
        Increment the row for grid packing.     
    update_options_view
        Updates the current plugin view
    get_plugin_by_tkname
       Get a plugin tuple in plugins dictionary by its tkname 
    get_views
        Get the current possible views able to be rendered by the GUI.
    hide_current_view
        Hide the current view and forget the current grid packing structure
    show_new_view
        Updates the plugin frame to render the view specified by next_view
    get_scorer_class_attrs_path
        Returns the current scorer class, attributes and path
    save_config
        Saves the scorer portion of the current plugin to a config JSON file.
    log_parameters
        Prints the current plugin's parameters to the current log handler(s).
    show_plugin_details
        Create a messagebox displaying the current plugin
    refresh_sources
        Parses each directory in `'~/.enrich2/sources.txt'`
    remove_plugin
        Deletes a plugin from the drop-down menu.
    update_plugin
        Updates an existing plugin from the drop-down menu. This will spawn a 
        pop-up box asking to confirm if file contents have changed.
    get_selected_plugin
        Returns the currently selected plugin object.
    refresh_menu
        Utility function to refresh the choices that the drop-down menu
        displays. Call this after deleting or updating plugins.
    
    See Also
    --------
    :py:class:`~tkinter.ttk.LabelFrame`
    """

    def __init__(self, parent=None, plugin_sources=None, **config):
        super().__init__(parent, **config)
        self.row = 0
        self.current_view = DUMMY_NAME
        self.btn_frame = None
        self.details_btn = None
        self.drop_menu_tkvar = None
        self.drop_menu = None
        self.plugins = {}

        if plugin_sources:
            for scripts_dir in parse_sources(plugin_sources):
                self._parse_directory(scripts_dir)

        self.make_widgets()
        self.make_buttons()
        self.show_new_view(self.current_view)

    # ---------------------------------------------------------------------- #
    #                         Plugin Parsing
    # ---------------------------------------------------------------------- #
    def load_from_cfg_file(self, script_path, script_attrs):
        """
        Load a plugin which has been specified in a configuration file.
        If a plugin already exists, the plugin view will be updated otherwise
        a new plugin view will be created.
        
        Parameters
        ----------
        script_path : `str`
            Path pointing to the script
        script_attrs : `dict`
            Dictionary of attributes that were defined in a configuration file.
        """
        plugin = self.parse_file(script_path)
        if plugin is None:
            log_message(
                logging_callback=logging.warning,
                msg="Could not load plugin {}.".format(script_path),
                extra={"oname": self.__class__.__name__},
            )
            return

        # Update the options from the script_attrs provided by cfg file
        scorer_cfg = plugin.options.to_dict()
        for k, v in script_attrs.items():
            scorer_cfg[k] = v

        # If the script has already been loaded, update the options
        # Otherwise create new frames for rendering.
        if not self.plugin_exists(plugin):
            options_frame, options_file_frame = self.make_options_frames(
                plugin.options, plugin.options_file
            )
            options_file_frame.update_option_frame(scorer_cfg)
            self.add_plugin(plugin, options_frame, options_file_frame)

            _, _, _, tkname = self.plugins[hash(plugin)]
            self.drop_menu.set_menu(tkname, *self.get_views())
            self.drop_menu_tkvar.set(tkname)
            self.update_options_view(tkname)

            log_message(
                logging_callback=logging.info,
                msg="Loaded new plugin from path {}.".format(script_path),
                extra={"oname": self.__class__.__name__},
            )
        else:
            self.update_plugin(plugin)
            _, _, options_file_frame, tkname = self.plugins[hash(plugin)]
            options_file_frame.update_option_frame(scorer_cfg)

            self.drop_menu.set_menu(tkname, *self.get_views())
            self.drop_menu_tkvar.set(tkname)
            self.update_options_view(tkname)

            log_message(
                logging_callback=logging.info,
                msg="Plugin from path {} updated.".format(script_path),
                extra={"oname": self.__class__.__name__},
            )

    def _parse_directory(self, scripts_dir):
        """
        Parses a directory into plugins stored in the plugins dictionary.

        Parameters
        ----------
        scripts_dir : `str`
            Directory containing a selection of scripts
            
        Returns
        -------
        `list`
            List of view names that have been parsed.
        """
        added_views = []
        files = sorted(glob.glob("{}/*.py".format(scripts_dir)))
        for path in files:
            path = path.replace("\\", "/")
            full_path = os.path.join(os.getcwd(), path)

            plugin = self.parse_file(full_path)
            if plugin is None:
                continue
            if self.plugin_exists(plugin):
                plugin, *_ = self.plugins[hash(plugin)]
                self.update_plugin(plugin)
            else:
                options_frame, options_file_frame = self.make_options_frames(
                    plugin.options, plugin.options_file
                )
                self.add_plugin(plugin, options_frame, options_file_frame)
            added_views.append(self.get_plugin_gui_name(plugin))
        return added_views

    def parse_file(self, path):
        """
        Parse a plugin file located at path into 
        :py:class:`~enrich2.gui.plugin.Plugin`,

        Parameters
        ----------
        path : `str`
            The path to the plugin file.

        Returns
        -------
        `enrich2.gui.plugin.Plugin`
        """
        if "__init__.py" in path:
            return None
        try:
            return Plugin(path)
        except Exception as e:
            log_message(
                logging_callback=logging.exception,
                msg=e,
                extra={"oname": self.__class__.__name__},
            )
            messagebox.showerror(
                "Error loading plugin...",
                "There was an error loading the script:\n\n{}."
                "\n\nSee log for details\n\n{}.".format(path, e),
            )
            return None

    def refresh_sources(self, sources):
        """
        Parses each directory in `'~/.enrich2/sources.txt'`
        
        Parameters
        ----------
        sources : `set`
            A set of source directories in string format.
        """
        views_before = set(self.get_views())
        views_after = set()
        for directory in sources:
            log_message(
                logging_callback=logging.info,
                msg="Parsing plugin source directory '{}'.".format(directory),
                extra={"oname": self.__class__.__name__},
            )
            views_after |= set(self._parse_directory(directory))

        for view in views_before - views_after:
            plugin, *_ = self.get_plugin_by_tkname(view)
            self.remove_plugin(plugin)
        self.refresh_menu()

    # ---------------------------------------------------------------------- #
    #                     Plugin Modification/Getters
    # ---------------------------------------------------------------------- #
    def remove_plugin(self, plugin):
        """
        Deletes a plugin from the drop-down menu.
        
        Parameters
        ----------
        plugin : :py:class:`~enrich2.gui.plugin.Plugin`
            A plugin object to delete from the dictionary of plugins.
        """
        if self.plugin_exists(plugin):
            _, *frames, tkname = self.plugins[hash(plugin)]

            if self.current_view == tkname:
                self.hide_current_view()

            for frame in frames:
                frame.destroy()
            del self.plugins[hash(plugin)]

            if self.current_view == tkname and self.plugins:
                new_view = self.get_views()[0]
            elif not self.plugins:
                new_view = DUMMY_NAME
            else:
                new_view = self.current_view

            self.drop_menu.set_menu(new_view, *self.get_views())
            self.show_new_view(new_view)
            self.current_view = new_view

    def update_plugin(self, plugin):
        """
        Updates an existing plugin from the drop-down menu. This will spawn a 
        pop-up box asking to confirm if file contents have changed.
        
        Parameters
        ----------
        plugin : :py:class:`~enrich2.gui.plugin.Plugin`
            A plugin object to delete from the dictionary of plugins.
        """
        if self.plugin_exists(plugin):
            plugin, *frames, tkname = self.plugins[hash(plugin)]
            if plugin.refresh():
                if self.current_view == tkname:
                    self.hide_current_view()

                for frame in frames:
                    frame.destroy()
                del self.plugins[hash(plugin)]

                frames = self.make_options_frames(plugin.options, plugin.options_file)
                self.add_plugin(plugin, *frames)
                new_view = self.get_plugin_gui_name(plugin)

                if self.current_view == new_view:
                    self.drop_menu.set_menu(new_view, *self.get_views())
                    self.show_new_view(new_view)

    def plugin_exists(self, plugin):
        """
        Check if a plugin exists based on name, authors, version and path

        Parameters
        ----------
        plugin : :py:class:`~enrich2.gui.plugin.Plugin`
            The class loaded from a plugin file

        Returns
        -------
        `bool`
            True if plugin already exists
        """
        key = hash(plugin)
        if key in self.plugins:
            return True
        return False

    def get_plugin_gui_name(self, plugin):
        """
        Returns the name the GUI uses to render the plugin in the drop down.
        
        Parameters
        ----------
        plugin : :py:class:`~enrich2.gui.plugin.Plugin`
            The class loaded from a plugin file
        
        Returns
        -------
        `str`
            String name used by GUI
        """
        _, _, _, tkname = self.plugins[hash(plugin)]
        return tkname

    def add_plugin(self, plugin, options_frame, options_file_frame):
        """
        Add a plugin to the plugins dictionary. Creates a unique name
        for the GUI if there are name collisions using the name defined in
        the class being added.
        
        Parameters
        ----------
        plugin : :py:class:`~enrich2.gui.plugin.Plugin`
            The class loaded from a plugin file
        options_frame : :py:class:`OptionsFileFrame`
            OptionsFileFrame create from the class
        options_file_frame : :py:class:`OptionsFrame`
            OptionsFrame object created from the class
        
        Returns
        -------
        `str`
            The GUI name of the existing/added plugin
        """
        if self.plugin_exists(plugin):
            return self.get_plugin_gui_name(plugin)

        # Rename plugins with the same 'name' attribute.
        tkname = plugin.klass.name
        tknames = set(name for _, _, _, name in self.plugins.values())
        if tkname in tknames:
            same_name = [n for n in tknames if n.split("[")[0].strip() == tkname]
            num = len(same_name)
            tkname = "{} [{}]".format(tkname, num)
        log_message(
            logging_callback=logging.info,
            msg="Added plugin with name '{}' from path '{}'.".format(
                tkname, plugin.path
            ),
            extra={"oname": self.__class__.__name__},
        )
        self.plugins[hash(plugin)] = (plugin, options_frame, options_file_frame, tkname)
        return tkname

    def get_plugin_by_tkname(self, tkname):
        """
        Get a plugin tuple in plugins dictionary by its tkname

        Parameters
        ----------
        tkname : `str`
            A string name used by :py:module: `tkinter` in the drop down menu.

        Returns
        -------
        `tuple`
            Size 3 tuple with Plugin, OptionsFrame, OptionsFileFrame
        """
        tkname_map = {n: (a, b, c) for (a, b, c, n) in self.plugins.values()}
        return tkname_map[tkname]

    def get_selected_plugin(self):
        """
        Returns the currently selected plugin object.
        
        Returns
        -------
        `tuple`
            Contains a Plugin object and associated options/file tk frame
            objects.
        """
        if self.current_view and self.current_view != DUMMY_NAME:
            plugin, opt_frame, opt_file_frame = self.get_plugin_by_tkname(
                self.current_view
            )
            return plugin, opt_frame, opt_file_frame
        return None

    # ---------------------------------------------------------------------- #
    #                        Packing/Widget Methods
    # ---------------------------------------------------------------------- #
    def make_drop_down_widget(self, default, choices):
        """
        Make the drop-down menu.
        """
        menu_var = StringVar(self)
        self.drop_menu_tkvar = menu_var

        f = lambda v: self.update_options_view(v)
        drop_menu = OptionMenu(self, menu_var, default, *choices, command=f)
        drop_menu.grid(sticky=E, column=1, row=self.row)
        self.drop_menu = drop_menu
        self.increment_row()

    def make_details_button(self):
        """
        Make the 'details' button.
        """
        f = lambda v=self.drop_menu_tkvar: self.show_plugin_details(v.get())
        btn = Button(self, text="Plugin Details", command=f)
        btn.grid(sticky=E, column=1, row=self.row)
        self.details_btn = btn
        self.increment_row()

    def make_buttons(self):
        """
        Make the print to log and save as buttons for interacting with a 
        plugin.
        """
        btn_frame = Frame(self)
        log_btn = Button(btn_frame, text="Print to Log", command=self.log_parameters)
        save_btn = Button(btn_frame, text="Save As...", command=self.save_config)
        log_btn.grid(row=0, column=0, sticky=E)
        save_btn.grid(row=0, column=1, sticky=E)
        self.btn_frame = btn_frame

    def increment_row(self):
        """
        Increment the row for grid packing.
        """
        self.row += 1

    def make_options_frames(self, options, options_file):
        """
        Creates the :py:class: `~OptionsFrame` and 
        :py:class: `~OptionsFileFrame` from 
        :py:class: `~enrich2.plugins.options.Options` and 
        :py:class: `~enrich2.plugins.options.OptionsFile` 

        Parameters
        ----------
        options : :py:class: `~enrich2.plugins.options.Options`
            Options object loaded from a plugin
        options_file : :py:class: `~enrich2.plugins.options.OptionsFile`
            OptionsFile object loaded from a plugin

        Returns
        -------
        `tuple`
            Tuple of (OptionsFrame, OptionsFileFrame)

        """
        options_frame = OptionsFrame(self, options)
        options_file_frame = OptionsFileFrame(self, options_file)
        options_file_frame.link_to_options_frame(options_frame)
        return options_frame, options_file_frame

    def make_widgets(self):
        """
        Make the drop-down menu and label.
        """
        label = Label(self, text="Scoring Plugin: ", justify=LEFT)
        label.grid(sticky=EW, column=0, row=self.row)

        if not self.plugins:
            self.make_drop_down_widget(DUMMY_NAME, [DUMMY_NAME])
            self.make_details_button()
        else:
            self.make_drop_down_widget(DUMMY_NAME, self.get_views())
            self.make_details_button()

    def refresh_menu(self):
        """
        Utility function to refresh the choices that the drop-down menu
        displays. Call this after deleting or updating plugins.
        """
        if self.plugins:
            if self.current_view == DUMMY_NAME:
                new_view = self.get_views()[0]
                self.drop_menu.set_menu(new_view, *self.get_views())
                self.update_options_view(new_view)
            else:
                self.drop_menu.set_menu(self.current_view, *self.get_views())
                self.update_options_view(self.current_view)

    # ---------------------------------------------------------------------- #
    #                            Views
    # ---------------------------------------------------------------------- #
    def update_options_view(self, next_view):
        """
        Updates the current plugin view

        Parameters
        ----------
        next_view : str:
            A string name used by :py:module: `tkinter` in the drop down menu.

        """
        self.hide_current_view()
        self.show_new_view(next_view)
        self.current_view = next_view

    def get_views(self):
        """
        Get the current possible views able to be rendered by the GUI.
        
        Returns
        -------
        `list`
            List of string tknames
        """
        return sorted([view for (_, _, _, view) in self.plugins.values()])

    def hide_current_view(self):
        """
        Hide the current view and forget the current grid packing structure
        """
        if self.current_view != DUMMY_NAME:
            _, options_frame, options_file_frame = self.get_plugin_by_tkname(
                self.current_view
            )
            if options_frame.has_options():
                options_frame.grid_forget()
                self.row -= 1
                options_file_frame.grid_forget()
                self.row -= 1
                self.btn_frame.grid_forget()
                self.row -= 1

    def show_new_view(self, next_view):
        """
        Updates the plugin frame to render the view specified by next_view
        
        Parameters
        ----------
        next_view : `str`
            A string name used by :py:module: `tkinter` in the drop down menu.
        """
        if next_view != DUMMY_NAME:
            _, options_frame, options_file_frame = self.get_plugin_by_tkname(next_view)
            if options_frame.has_options():
                options_frame.grid(
                    sticky=NSEW, row=self.row, columnspan=2, pady=(12, 0)
                )
                self.increment_row()

                options_file_frame.grid(
                    sticky=NSEW, row=self.row, columnspan=2, pady=(12, 0)
                )
                self.increment_row()

                self.btn_frame.grid(row=self.row, columnspan=2, sticky=E, pady=(12, 0))
                self.increment_row()

    # ---------------------------------------------------------------------- #
    #                             Config Methods
    # ---------------------------------------------------------------------- #
    def get_scorer_class_attrs_path(self, keep_defult_bool=False):
        """
        Returns the current scorer class, attributes and path
        
        Parameters
        ----------
        keep_defult_bool : `bool`
            Values in attribute dictionary will be a tuple with the second
            element indicating if the value is the same as the default value
            defined in the plugin.

        Returns
        -------
        `tuple`
            Plugin class, dictionary of option varname-value pairs and the 
            plugin path.
        """
        if not self.plugins or self.current_view == DUMMY_NAME:
            return None, None, None

        attrs = {}
        plugin, opt_frame, opt_file_frame = self.get_selected_plugin()
        options_cfg = opt_frame.get_option_cfg()
        for k, (v, default) in options_cfg.items():
            if keep_defult_bool:
                attrs[k] = (v, default)
            else:
                attrs[k] = v
        return plugin.klass, attrs, plugin.path

    def save_config(self):
        """
        Saves the scorer portion of the current plugin to a config JSON file.
        """
        fp = asksaveasfile()
        if fp:
            _, attrs, path = self.get_scorer_class_attrs_path()
            if attrs and path:
                json_cfg = {SCORER_PATH: path, SCORER_OPTIONS: attrs}
                json.dump(json_cfg, fp)
                messagebox.showinfo(
                    "Configuration Saved!", "Successfully saved plugin configuration!"
                )
            else:
                messagebox.showwarning(
                    "Nothing to save.", "No plugin loaded or no attributes to save."
                )

    def log_parameters(self):
        """
        Prints the current plugin's parameters to the current log handler(s).
        """
        _, cfg, _ = self.get_scorer_class_attrs_path(keep_defult_bool=True)
        if not cfg or cfg is None:
            messagebox.showwarning(
                "Nothing to log.", "No plugin loaded or no attributes to log."
            )
            return
        msg = "Scorer Parameters "
        msg += nested_format(cfg, False, tab_level=0)
        log_message(
            logging_callback=logging.info,
            msg=msg,
            extra={"oname": self.__class__.__name__},
        )

    def show_plugin_details(self, name):
        """
        Create a messagebox displaying the current plugin
        
        Parameters
        ----------
        name : `str`
            A string name used by :py:module: `tkinter` in the drop down menu.
        """
        if name == DUMMY_NAME:
            messagebox.showwarning(
                "No plugin selected.\n\n".format(name),
                "Select a plugin from the drop down menu.",
            )
        else:
            plugin, *_ = self.get_plugin_by_tkname(name)
            klass = plugin.klass
            path = plugin.path
            messagebox.showinfo(
                "{} Information\n\n".format(name),
                "Name: {}\n\nVersion: {}\n\nAuthors: "
                "{}\n\nPath: {}".format(klass.name, klass.version, klass.author, path),
            )
