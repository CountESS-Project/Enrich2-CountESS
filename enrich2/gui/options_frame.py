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

import os
import glob
import json
import logging
from tkinter import *
import tkinter.ttk as ttk
from collections import Iterable
import tkinter.messagebox as messagebox
from tkinter.filedialog import askopenfilename, asksaveasfile

from enrich2.plugins.options import Options, Option
from enrich2.plugins.options import options_not_in_config
from enrich2.plugins.options import get_unused_options
from enrich2.plugins import load_scorer_class_and_options
from ..base.utils import nested_format, log_message


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
    def __init__(self, parent, options, **kw):
        super(OptionsFrame, self).__init__(parent, **kw)
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
        if option.choices:
            self.make_choice_menu_widget(option)
        elif option.dtype in (str, 'string', 'char', 'chr'):
            self.make_string_entry_widget(option)
        elif option.dtype in ('integer', 'int', int):
            self.make_int_entry_widget(option)
        elif option.dtype in ('float', float):
            self.make_float_entry_widget(option)
        elif option.dtype in ('bool', bool, 'boolean'):
            self.make_bool_entry_widget(option)
        else:
            raise ValueError("Unrecognised attribute in option "
                             "dtype {}.".format(option.dtype))

    def make_choice_menu_widget(self, option):
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
            self, variable, option.get_choice_key(), *choices, command=set_func)
        popup_menu.grid(sticky=E, column=1, row=self.row)
        self.vname_tkvars_map[option.varname] = variable

    def make_entry(self, variable, option):
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
                    message=bad_input_msg.format(varname, error)
                )
                return False
            return True

        entry = Entry(
            self, textvariable=variable,
            validate="focusout", validatecommand=validate
        )
        entry.grid(sticky=EW, column=1, row=self.row)
        self.vname_tkvars_map[option.varname] = variable
        return entry

    def make_bool_entry_widget(self, option):
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

    def make_string_entry_widget(self, option: Option) -> None:
        variable = StringVar(self)
        variable.set(option.dtype(option.get_default_value()))
        self.make_entry(variable, option)

    def make_int_entry_widget(self, option):
        variable = IntVar(self)
        variable.set(option.dtype(option.get_default_value()))
        self.make_entry(variable, option)

    def make_float_entry_widget(self, option: Option) -> None:
        variable = DoubleVar(self)
        variable.set(option.dtype(option.get_default_value()))
        self.make_entry(variable, option)

    def set_validate(self, varname, value):
        bad_input_msg = "Error validating input for entry {}:\n\n{}"
        try:
            self.set_variable(varname, value)
            self.set_option(varname, value)
        except (KeyError, TclError, TypeError, ValueError) as error:
            option = self.get_option_by_varname(varname)
            self.set_variable(varname, option.get_value())
            messagebox.showwarning(
                title="Error setting option!",
                message=bad_input_msg.format(varname, error)
            )
            return False
        return True

    def get_option_by_varname(self, varname):
        option = self.options.get(varname, None)
        if option is None:
            raise KeyError("No option with the variable name '{}' could "
                           "be found".format(varname))
        return option

    def set_option(self, varname, value):
        option = self.get_option_by_varname(varname)
        option.set_value(value)

    def set_variable(self, varname, value):
        variable = self.vname_tkvars_map.get(varname, None)
        if variable is not None:
            variable.set(value)

    def get_option_cfg(self):
        cfg = {}
        for varname, opt in self.options.items():
            value = opt.get_value()
            default = opt.get_default_value()
            opt.validate(value)
            cfg[varname] = (value, value == default)
        return cfg

    def has_options(self):
        return self.options.has_options()


# -------------------------------------------------------------------------- #
#                        Frame for File Handling
# -------------------------------------------------------------------------- #
class OptionsFileFrame(Frame):
    def __init__(self, parent, options_file, **config):
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
        self._make_label()
        self._make_button()
        self.rowconfigure(self.row, weight=1)
        self.row += 1

    def _make_label(self):
        label_text = "{}: ".format(self.options_file.name)
        label = Label(self, text=label_text, justify=LEFT)
        label.grid(row=self.row, column=0, sticky=EW)

    def _make_button(self):
        button = Button(self, text='Load...', command=self.load_from_file)
        button.grid(row=self.row, column=1, sticky=E)

    def load_from_file(self):
        file_path = askopenfilename()
        if not file_path:
            return

        self.active_cfg = {}
        cfg_error_msg = "There was an error parsing file {}. " \
                        "\n\nPlease see log for details.".format(file_path)
        validation_error_msg = "There was an error during validation. " \
                               "\n\nPlease see log for details."
        try:
            cfg = self.options_file.parse_to_dict(file_path)
        except BaseException as error:
            log_message(
                logging_callback=logging.exception,
                msg=error, extra={'oname': self.__class__.__name__}
            )
            messagebox.showerror('Parse Error', cfg_error_msg)
            return

        try:
            self.options_file.validate_cfg(cfg)
        except BaseException as error:
            log_message(
                logging_callback=logging.exception,
                msg=error, extra={'oname': self.__class__.__name__}
            )
            messagebox.showerror('Validation Error', validation_error_msg)
            return

        self.active_cfg = cfg
        self.apply_to_options()

    def apply_to_options(self):
        success = 'Successfully applied configuration file to plugin options.'
        if not self.options_frame:
            messagebox.showwarning(
                'Apply Configuration Warning',
                "No options have been defined in this plugin. Cannot apply"
                "loaded configuration."
            )
            return

        if not self.active_cfg:
            messagebox.showwarning(
                'Apply Configuration Warning',
                "No configuration file has been loaded. Please load one first."
            )
            return

        warn_message = ""
        unused_keys = get_unused_options(
            self.active_cfg, self.options_frame.options)
        incomplete = self.options_file_incomplete()
        self.active_cfg = {k: v for (k, v) in self.active_cfg.items()
                           if k not in unused_keys}

        if unused_keys:
            unused = '\n'.join(["'{}'".format(n) for n in unused_keys])
            warn_message += "The following options found in the configuration" \
                            "file are not defined in the current plugin and " \
                            "will not be used during analysis:\n\n{}\n\n"
            warn_message = warn_message.format(unused)

        if incomplete:
            incomplete = '\n'.join(["'{}'".format(n) for n in incomplete])
            warn_message += "The following options defined in the plugin " \
                            "could not be found in the configuration file:" \
                            "\n\n{}\n\nThese options will not been altered."
            warn_message = warn_message.format(incomplete)

        if warn_message:
            messagebox.showwarning(
                'Apply configuration to options.', warn_message)

        applied_successfully = self.update_option_frame(self.active_cfg)
        if applied_successfully and not warn_message:
            messagebox.showinfo('Apply configuration to options.', success)
        return

    def options_file_incomplete(self):
        missing = []
        if self.options_frame and self.active_cfg:
            missing = options_not_in_config(
                self.active_cfg, self.options_frame.options)
            if missing:
                return [opt.varname for opt in missing]
            return missing
        return missing

    def update_option_frame(self, cfg):
        current = []
        for varname, value in cfg.items():
            bad_input_msg = "The following error occured when validating" \
                            " option with variable name '{}':\n\n{}\n\n" \
                            "Loading the specified configuration has been " \
                            "aborted. Please supply a correct configuration " \
                            "file before proceeding. No changes " \
                            "have been made."
            try:
                option = self.options_frame.get_option_by_varname(varname)
                current.append((varname, option.get_value()))
                self.options_frame.set_option(varname, value)
                if option.choices:
                    self.options_frame.set_variable(
                        varname, option.get_choice_key()
                    )
                else:
                    self.options_frame.set_variable(
                        varname, option.get_value()
                    )
            except (KeyError, TclError, TypeError, ValueError) as error:
                for varname, old_val in current:
                    self.options_frame.set_option(varname, old_val)
                    option = self.options_frame.get_option_by_varname(varname)
                    if option.choices:
                        self.options_frame.set_variable(
                            varname,
                            option.get_choice_key()
                        )
                    else:
                        self.options_frame.set_variable(
                            varname,
                            option.get_value()
                        )
                messagebox.showwarning(
                    title="Error setting option!",
                    message=bad_input_msg.format(varname, error)
                )
                log_message(
                    logging_callback=logging.exception,
                    msg=error, extra={'oname': self.__class__.__name__}
                )
                return False
        return True

    def get_option_cfg(self):
        return self.active_cfg

    def link_to_options_frame(self, options_frame: OptionsFrame):
        self.options_frame = options_frame


# -------------------------------------------------------------------------- #
#                           Main GUI Frame
# -------------------------------------------------------------------------- #
plugins_folder = os.path.join(os.path.expanduser('~'), '.enrich2/')


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
                
    """
    def __init__(self, parent=None, scripts_dir=plugins_folder, **config):
        super().__init__(parent, **config)
        self.row = 0
        self.current_view = 'Regression'
        self.btn_frame = None
        self.drop_menu_tkvar = None
        self.drop_menu = None
        self.plugins = {}

        self._parse_directory(scripts_dir)
        self.make_widgets()
        self.make_buttons()
        self.show_new_view(self.current_view)

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
        klass, options, options_file = self.parse_file(script_path)
        if klass is None and options_file is None and options is None:
            log_message(
                logging_callback=logging.warning,
                msg="Could not load plugin {}.".format(script_path),
                extra={'oname': self.__class__.__name__}
            )
            return

        # Update the options from the script_attrs provided by cfg file
        scorer_cfg = options.to_dict()
        for k, v in script_attrs.items():
            scorer_cfg[k] = v

        # If the script has already been loaded, update the options
        # Otherwise create new frames for rendering.
        if not self.plugin_exists(klass, script_path):
            options_frame, options_file_frame = self.make_options_frames(
                options, options_file
            )
            options_file_frame.update_option_frame(scorer_cfg)
            self.add_plugin(
                klass,
                options_frame,
                options_file_frame,
                script_path
            )
            _, _, _, _, tkname = \
                self.plugins[self.plugin_hash(klass, script_path)]
            self.drop_menu.set_menu(tkname, *self.get_views())
            self.drop_menu_tkvar.set(tkname)
            self.update_options_view(tkname)
            log_message(
                logging_callback=logging.info,
                msg="Loaded plugin from path {}.".format(script_path),
                extra={'oname': self.__class__.__name__}
            )
        else:
            _, _, options_file_frame, _, tkname = \
                self.plugins[self.plugin_hash(klass, script_path)]
            self.drop_menu_tkvar.set(tkname)
            self.update_options_view(tkname)
            options_file_frame.update_option_frame(scorer_cfg)
            log_message(
                logging_callback=logging.info,
                msg="Plugin from path {} updated.".format(script_path),
                extra={'oname': self.__class__.__name__}
            )

    def _parse_directory(self, scripts_dir):
        """
        Parses a directory into plugins stored in the plugins dictionary.
        
        Parameters
        ----------
        scripts_dir : `str`
            Directory containing a selection of scripts
        """
        files = sorted(glob.glob("{}/*.py".format(scripts_dir)))
        for path in files:
            path = path.replace("\\", '/')
            full_path = os.path.join(os.getcwd(), path)

            klass, options, options_file = self.parse_file(full_path)
            if klass is None and options is None and options_file is None:
                continue
            options_frame, options_file_frame = self.make_options_frames(
                options, options_file)
            self.add_plugin(
                klass,
                options_frame,
                options_file_frame,
                full_path
            )

    def parse_file(self, path):
        """
        Parse a plugin file located at path into 
        :py:class: `~enrich2.plugins.scoring.BaseScorerPlugin`,
        :py:class: `~enrich2.plugins.options.Options` and 
        :py:class: `~enrich2.plugins.options.OptionsFile`
        
        Parameters
        ----------
        path : `str`
            The path to the plugin file.

        Returns
        -------
        `tuple`
            Loaded class, options and options_file
        """
        if "__init__.py" in path:
            return None, None, None
        try:
            result = load_scorer_class_and_options(path)
            klass, options, options_file = result
            return klass, options, options_file
        except Exception as e:
            log_message(
                logging_callback=logging.exception, msg=e,
                extra={'oname': self.__class__.__name__})
            messagebox.showerror(
                "Error loading plugin...",
                "There was an error loading the script:\n\n{}."
                "\n\nSee log for details\n\n{}.".format(path, e)
            )
            return None, None, None

    def plugin_hash(self, klass, path):
        """
        Generate a hash key based on name, authors, version and path
        
        Parameters
        ----------
        klass : :py:class: `~enrich2.plugins.scoring.BaseScorerPlugin`
            The class loaded from a plugin file
        path : `str`
            The path pointing to the plugin
        
        Returns
        -------
        `int`
            integer hash returned by :py:func: `hash`

        """
        return hash((klass.name, klass.version, klass.author, path))

    def plugin_exists(self, klass, path):
        """
        Check if a plugin exist based on name, authors, version and path
        
        Parameters
        ----------
        klass : :py:class: `~enrich2.plugins.scoring.BaseScorerPlugin`
            The class loaded from a plugin file
        path : `str`
            The path pointing to the plugin
        
        Returns
        -------
        `bool`
            True if plugin already exists
        """
        key = self.plugin_hash(klass, path)
        if key in self.plugins:
            return True
        return False

    def get_plugin_gui_name(self, klass, path):
        """
        Returns the name the GUI uses to render the plugin in the drop down.
        
        Parameters
        ----------
        klass : :py:class: `~enrich2.plugins.scoring.BaseScorerPlugin`
            The class loaded from a plugin file
        path : `str`
            The path pointing to the plugin
        
        Returns
        -------
        `str`
            String name used by GUI
        """
        _, _, _, _, tkname = self.plugins[self.plugin_hash(klass, path)]
        return tkname

    def add_plugin(self, klass, options_frame, options_file_frame, path):
        """
        Add a plugin to the plugins dictionary. Creates a unique name
        for the GUI if there are name collisions using the name defined in
        the class being added.
        
        Parameters
        ----------
        klass : :py:class: `~enrich2.plugins.scoring.BaseScorerPlugin` 
            The class loaded from a plugin file
        options_frame : :py:class:`OptionsFileFrame`
            OptionsFileFrame create from the class
        options_file_frame : :py:class:`OptionsFrame`
            OptionsFrame object created from the class
        path : `str`
            The path pointing to the plugin

        Returns
        -------
        None

        """
        if self.plugin_exists(klass, path):
           return

        # Rename plugins with the same 'name' attribute.
        tkname = klass.name
        tknames = set(name for _, _, _, _, name in self.plugins.values())
        if tkname in tknames:
            same_name = [n for n in tknames if n.split('[')[0].strip() == tkname]
            num = len(same_name)
            tkname = "{} [{}]".format(tkname, num)
        self.plugins[self.plugin_hash(klass, path)] = \
            (klass, options_frame, options_file_frame, path, tkname)

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
            default = 'No plugins detected'
            drop_menu = OptionMenu(self, StringVar(), default, *[default])
            drop_menu.grid(sticky=E, column=1, row=self.row)
            self.drop_menu = drop_menu
            self.increment_row()
        else:
            self.make_drop_down_widget()

    def make_drop_down_widget(self):
        """
        Make the drop-down menu.
        """
        choices = self.get_views()
        menu_var = StringVar(self)
        self.drop_menu_tkvar = menu_var

        switch = lambda v: self.update_options_view(v)
        drop_menu = OptionMenu(self, menu_var, self.current_view,
                                *choices, command=switch)
        drop_menu.grid(sticky=E, column=1, row=self.row)
        self.drop_menu = drop_menu
        self.increment_row()

        details = lambda v=menu_var: self.show_plugin_details(v.get())
        btn = Button(self, text='Plugin Details', command=details)
        btn.grid(sticky=E, column=1, row=self.row)
        self.increment_row()

    def make_buttons(self):
        """
        Make the print to log and save as buttons for interacting with a 
        plugin.
        """
        btn_frame = Frame(self)
        log_btn = Button(btn_frame, text='Print to Log',
                         command=self.log_parameters)
        save_btn = Button(btn_frame, text='Save As...',
                          command=self.save_config)
        log_btn.grid(row=0, column=0, sticky=E)
        save_btn.grid(row=0, column=1, sticky=E)
        self.btn_frame = btn_frame

    def increment_row(self):
        """
        Increment the row for grid packing.
        """
        self.row += 1

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
            Size 4 tuple with klass, OptionsFrame, OptionsFileFrame and path
        """
        tkname_map = {
            n: (a, b, c, d) for (a, b, c, d, n) in self.plugins.values()
        }
        return tkname_map[tkname]

    def get_views(self):
        """
        Get the current possible views able to be rendered by the GUI.
        
        Returns
        -------
        `list`
            List of string tknames
        """
        return sorted([view for (_, _, _, _, view) in self.plugins.values()])

    def hide_current_view(self):
        """
        Hide the current view and forget the current grid packing structure
        """
        _, options_frame, options_file_frame, _ = \
            self.get_plugin_by_tkname(self.current_view)
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
        _, options_frame, options_file_frame, _ = \
            self.get_plugin_by_tkname(next_view)
        if options_frame.has_options():
            options_frame.grid(
                sticky=NSEW, row=self.row,
                columnspan=2, pady=(12, 0))
            self.increment_row()

            options_file_frame.grid(
                sticky=NSEW, row=self.row,
                columnspan=2, pady=(12, 0))
            self.increment_row()

            self.btn_frame.grid(
                row=self.row, columnspan=2,
                sticky=E, pady=(12, 0))
            self.increment_row()

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
        if not self.plugins:
            return None, None, None

        attrs = {}
        klass, opt_frame, opt_file_frame, path = \
            self.get_plugin_by_tkname(self.current_view)
        options_cfg = opt_frame.get_option_cfg()
        for k, (v, default) in options_cfg.items():
            if keep_defult_bool:
                attrs[k] = (v, default)
            else:
                attrs[k] = v
        return klass, attrs, path

    def save_config(self):
        """
        Saves the scorer portion of the current plugin to a config JSON file.
        """
        fp = asksaveasfile()
        if fp:
            _, attrs, path = self.get_scorer_class_attrs_path()
            if attrs and path:
                json_cfg = {
                    'scorer_path': path,
                    'scorer_options': attrs
                }
                json.dump(json_cfg, fp)
                messagebox.showinfo(
                    "Configuration Saved!",
                    "Successfully saved plugin configuration!"
                )
            else:
                messagebox.showwarning(
                    "Nothing to save.",
                    "No plugin loaded or no attributes to save."
                )

    def log_parameters(self):
        """
        Prints the current plugin's parameters to the current log handler(s).
        """
        _, cfg, _ = self.get_scorer_class_attrs_path(keep_defult_bool=True)
        if not cfg or cfg is None:
            messagebox.showwarning(
                "Nothing to log.",
                "No plugin loaded or no attributes to log."
            )
            return
        msg = "Scorer Parameters "
        msg += nested_format(cfg, False, tab_level=0)
        log_message(
            logging_callback=logging.info, msg=msg,
            extra={'oname': self.__class__.__name__}
        )

    def show_plugin_details(self, name):
        """
        Create a messagebox displaying the current plugin
        
        Parameters
        ----------
        name : `str`
            A string name used by :py:module: `tkinter` in the drop down menu.
        """
        klass, _, _, path = self.get_plugin_by_tkname(name)
        messagebox.showinfo(
            '{} Information\n\n'.format(name),
            'Name: {}\n\nVersion: {}\n\nAuthors: '
            '{}\n\nPath: {}'.format(klass.name,
                                    klass.version, klass.author, path)
        )
