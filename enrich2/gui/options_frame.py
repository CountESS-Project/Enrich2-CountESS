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

from ..plugins.options import Options, Option
from ..plugins.options import options_not_in_config
from ..plugins.options import get_unused_options
from ..plugins import load_scoring_class_and_options
from ..base.utils import nested_format


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
        super().__init__(parent, **kw)
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
        variable.set(option.default)

        label_text = "{}: ".format(option.name)
        label = Label(self, text=label_text, justify=LEFT)
        label.grid(sticky=EW, column=0, row=self.row)

        choices = option.choices
        choices = list(choices.keys())

        vname = option.varname
        set_func = lambda _, y=variable, x=vname: self.set_validate(x, y.get())
        popup_menu = OptionMenu(
            self, variable, option.default, *choices, command=set_func)
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
                variable.set(option.dtype(option.value))
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
        variable.set(option.default)

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
        variable.set(option.dtype(option.default))
        self.make_entry(variable, option)

    def make_int_entry_widget(self, option):
        variable = IntVar(self)
        variable.set(option.dtype(option.default))
        self.make_entry(variable, option)

    def make_float_entry_widget(self, option: Option) -> None:
        variable = DoubleVar(self)
        variable.set(option.dtype(option.default))
        self.make_entry(variable, option)

    def set_validate(self, varname, value):
        bad_input_msg = "Error validating input for entry {}:\n\n{}"
        try:
            self.set_variable(varname, value)
            self.set_option(varname, value)
        except (KeyError, TclError, TypeError, ValueError) as error:
            option = self.get_option_by_varname(varname)
            self.set_variable(varname, option.value)
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
            value = opt.value
            default = opt.default
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

    def load_from_cfg(self, cfg):
        if 'scorer' in cfg:
            if 'scorer_options' in cfg:
                return cfg['scorer']['scorer_options']
        elif 'scorer_options' in cfg:
            return cfg['scorer_options']
        else:
            raise ValueError("Unrecognised config file, couldn't find "
                             "expected keys. File requires the nested key"
                             "'scorer/scorer_options' "
                             "or the key 'scorer_options'")

        success = 'Successfully parsed and validated config.'
        if self.options_frame:
            if self.update_option_frame(cfg):
                self.active_cfg = cfg
                if not self.options_file_incomplete():
                    messagebox.showinfo('Success!', success)
        else:
            self.active_cfg = cfg
            messagebox.showinfo('Success!', success)

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
            logging.exception(error, extra={'oname': self.__class__.__name__})
            messagebox.showerror('Parse Error', cfg_error_msg)
            return

        try:
            self.options_file.validate_cfg(cfg)
        except BaseException as error:
            logging.exception(error, extra={'oname': self.__class__.__name__})
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
                current.append((varname, option.value))
                self.options_frame.set_variable(varname, value)
                self.options_frame.set_option(varname, value)
            except (KeyError, TclError, TypeError, ValueError) as error:
                for vname, old_val in current:
                    self.options_frame.set_variable(vname, old_val)
                    self.options_frame.set_option(vname, old_val)
                messagebox.showwarning(
                    title="Error setting option!",
                    message=bad_input_msg.format(varname, error)
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
class ScorerScriptsDropDown(LabelFrame):
    def __init__(self, parent=None, scripts_dir='plugins/', **config):
        super().__init__(parent, **config)
        self.row = 0
        self.current_view = 'Regression'
        self.btn_frame = None
        self.plugins = {}

        self.parse_directory(scripts_dir)
        self.make_widgets()
        self.make_buttons()
        self.show_new_view(self.current_view)

    def parse_directory(self, scripts_dir):
        for path in glob.glob("{}/*.py".format(scripts_dir)):
            path = path.replace("\\", '/')
            full_path = os.path.join(os.getcwd(), path)
            if "__init__.py" in path:
                continue
            try:
                result = load_scoring_class_and_options(path)
                klass, options, options_file = result
                options_frame, options_file_frame = self.make_options_frames(
                    options, options_file
                )
            except Exception as e:
                logging.exception(e, extra={'oname': self.__class__.__name__})
                messagebox.showerror(
                    "Error loading plugin...",
                    "There was an error loading the script:\n\n{}."
                    "\n\nSee log for details\n\n{}.".format(full_path, e)
                )
                continue

            # Rename plugins with the same 'name' attribute.
            key = klass.name
            if key in self.plugins:
                same_name = [n for n in self.plugins.keys()
                             if n.split('[')[0].strip() == key]
                num = len(same_name)
                key = "{} [{}]".format(key, num)
            self.plugins[key] = (klass, options_frame,
                                 options_file_frame, full_path)

    def make_options_frames(self, options, options_file):
        options_frame = OptionsFrame(self, options)
        options_file_frame = OptionsFileFrame(self, options_file)
        options_file_frame.link_to_options_frame(options_frame)
        return options_frame, options_file_frame

    def make_widgets(self):
        # Main Scoring plugin frame
        label = Label(self, text="Scoring Plugin: ", justify=LEFT)
        label.grid(sticky=EW, column=0, row=self.row)

        if not self.plugins:
            default = 'No plugins detected'
            popup_menu = OptionMenu(self, StringVar(), default, *[default])
            popup_menu.grid(sticky=E, column=1, row=self.row)
            self.increment_row()
        else:
            self.make_drop_down_widget()

    def make_drop_down_widget(self):
        choices = [n for n, _ in self.plugins.items()]
        menu_var = StringVar(self)

        switch = lambda v: self.update_options_view(v)
        popup_menu = OptionMenu(self, menu_var, self.current_view,
                                *choices, command=switch)
        popup_menu.grid(sticky=E, column=1, row=self.row)
        self.increment_row()

        details = lambda v=menu_var: self.show_plugin_details(v.get())
        btn = Button(self, text='Plugin Details', command=details)
        btn.grid(sticky=E, column=1, row=self.row)
        self.increment_row()

    def make_buttons(self):
        btn_frame = Frame(self)
        log_btn = Button(btn_frame, text='Print to Log',
                         command=self.log_parameters)
        save_btn = Button(btn_frame, text='Save As...',
                          command=self.save_config)
        log_btn.grid(row=0, column=0, sticky=E)
        save_btn.grid(row=0, column=1, sticky=E)
        self.btn_frame = btn_frame

    def increment_row(self):
        # self.rowconfigure(self.row, weight=1)
        self.row += 1

    def update_options_view(self, next_view):
        self.hide_current_view()
        self.show_new_view(next_view)
        self.current_view = next_view

    def hide_current_view(self):
        _, options_frame, options_file_frame, _ = \
            self.plugins[self.current_view]
        if options_frame.has_options():
            options_frame.grid_forget()
            self.row -= 1
            options_file_frame.grid_forget()
            self.row -= 1
            self.btn_frame.grid_forget()
            self.row -= 1

    def show_new_view(self, next_view):
        _, options_frame, options_file_frame, _ = self.plugins[next_view]
        if options_frame.has_options():
            options_frame.grid(sticky=NSEW, row=self.row,
                               columnspan=2, pady=(12, 0))
            self.increment_row()

            options_file_frame.grid(sticky=NSEW, row=self.row,
                                    columnspan=2, pady=(12, 0))
            self.increment_row()

            self.btn_frame.grid(row=self.row, columnspan=2,
                                sticky=E, pady=(12, 0))
            self.increment_row()

    def get_class_and_attrs(self, keep_defult_bool=False):
        if not self.plugins:
            return None, None

        attrs = {}
        klass, opt_frame, opt_file_frame, _ = self.plugins[self.current_view]
        options_cfg = opt_frame.get_option_cfg()
        for k, (v, default) in options_cfg.items():
            if keep_defult_bool:
                attrs[k] = (v, default)
            else:
                attrs[k] = v
        return klass, attrs

    def save_config(self):
        fp = asksaveasfile()
        if fp:
            _, attrs = self.get_class_and_attrs()
            if attrs and attrs is not None:
                json_cfg = {'scorer_options': attrs}
                json.dump(json_cfg, fp)
            else:
                messagebox.showwarning(
                    "Nothing to save.",
                    "No plugin loaded or no attributes to save."
                )

    def log_parameters(self):
        _, cfg = self.get_class_and_attrs(keep_defult_bool=True)
        if not cfg or cfg is None:
            messagebox.showwarning(
                "Nothing to log.",
                "No plugin loaded or no attributes to log."
            )
            return
        msg = "Parsing parameters...\nFormat: (value, type) "
        msg += nested_format(cfg, False, tab_level=0)
        logging.info(msg, extra={'oname': self.__class__.__name__})
        messagebox.showinfo("Parameters logged!",
                            "See log for loaded parameters.")

    def show_plugin_details(self, name):
        klass, _, _, path = self.plugins[name]
        messagebox.showinfo(
            '{} Information\n\n'.format(name),
            'Name: {}\n\nVersion: {}\n\nAuthors: '
            '{}\n\nPath: {}'.format(klass.name,
                                    klass.version, klass.author, path)
        )
