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
import logging
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from tkinter.filedialog import askopenfilename

from ..plugins.options import ScorerOptions, Option
from ..plugins.options import ScorerOptionsFiles, OptionsFile
from ..plugins import load_scoring_class_and_options


LabelFrame = ttk.LabelFrame
Frame = ttk.Frame
Label = ttk.Label
Entry = ttk.Entry
Button = ttk.Button
Checkbutton = ttk.Checkbutton
OptionMenu = ttk.OptionMenu


class OptionFrame(LabelFrame):
    def __init__(self, parent, options: ScorerOptions, **kw):
        super().__init__(parent, **kw)
        self.parent = parent
        self.row = 0
        self.widgets = []
        self.option_vars = []
        self.labels = []
        self.parse_options(options)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

    def parse_options(self, options: ScorerOptions) -> None:
        if not len(options):
            label_text = "No options found."
            label = Label(self, text=label_text, justify=LEFT)
            label.grid(sticky=EW, columnspan=1, row=self.row, padx=5, pady=5)
            self.rowconfigure(self.row, weight=1)
            self.row += 1

        for option in options:
            try:
                option.validate(option.default)
            except TypeError:
                warn = "The default value for option {} has type" \
                       " '{}' and does not match the specified expected " \
                       "type '{}'. The program may behave unexpectedly."
                messagebox.showwarning(
                    title="Default option type does not match dtype.",
                    message=warn.format(option.name,
                                        type(option.default).__name__,
                                        option.dtype.__name__))
            self.create_widget_from_option(option)
            self.rowconfigure(self.row, weight=1)
            self.row += 1

        btn = Button(self, text='Show Parameters', command=self.log_parameters)
        btn.grid(row=self.row, column=1, sticky=SE, padx=5, pady=5)
        self.rowconfigure(self.row, weight=1)
        self.row += 1
        return

    def create_widget_from_option(self, option: Option) -> None:
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

    def make_choice_menu_widget(self, option: Option) -> None:
        menu_var = StringVar(self)
        menu_var.set(option.default)

        label_text = "{}: ".format(option.name)
        label = Label(self, text=label_text, justify=LEFT)
        label.grid(sticky=EW, column=0, row=self.row, padx=5, pady=5)

        choices = option.choices
        choices = list(choices.keys())

        popup_menu = OptionMenu(
            self, menu_var, option.default, *choices)
        popup_menu.grid(sticky=E, column=1, row=self.row, padx=5, pady=5)

        self.option_vars.append((option, menu_var))
        self.widgets.append(popup_menu)
        self.labels.append(label)

    def make_entry(self, variable: Variable, option: Option) -> Entry:
        label_text = "{}: ".format(option.name)
        label = Label(self, text=label_text, justify=LEFT)
        label.grid(sticky=EW, column=0, row=self.row, padx=5, pady=5)

        bad_input_msg = "Invalid type for entry {}. " \
                        "Expected type {}.".format(
            option.name, option.dtype.__name__)

        def validate_entry():
            try:
                value = variable.get()
                option.validate(value)
                variable.set(option.dtype(value))
            except (TclError, TypeError):
                messagebox.showwarning(
                    title="Invalid {} Entry".format(option.name),
                    message=bad_input_msg)
                variable.set(option.dtype(option.default))
                return False
            return True

        entry = Entry(
            self, textvariable=variable,
            validate="focusout", validatecommand=validate_entry
        )
        entry.grid(sticky=EW, column=1, row=self.row, padx=5, pady=5)
        self.option_vars.append((option, variable))
        self.widgets.append(entry)
        self.labels.append(label)
        return entry

    def make_string_entry_widget(self, option: Option) -> None:
        variable = StringVar(self)
        variable.set(option.dtype(option.default))
        self.make_entry(variable, option)

    def make_int_entry_widget(self, option: Option) -> None:
        variable = IntVar(self)
        variable.set(option.dtype(option.default))
        self.make_entry(variable, option)

    def make_float_entry_widget(self, option: Option) -> None:
        variable = DoubleVar(self)
        variable.set(option.dtype(option.default))
        self.make_entry(variable, option)

    def make_bool_entry_widget(self, option: Option) -> None:
        variable = BooleanVar(self)
        variable.set(option.default)

        label_text = "{}: ".format(option.name)
        label = Label(self, text=label_text, justify=LEFT)
        label.grid(sticky=EW, column=0, row=self.row, padx=5, pady=5)

        checkbox = Checkbutton(self, variable=variable)
        checkbox.grid(sticky=E, column=1, row=self.row, padx=5, pady=5)

        self.option_vars.append((option, variable))
        self.widgets.append(checkbox)
        self.labels.append(label)

    def get_option_cfg(self) -> dict:
        cfg = {}
        for option, var in self.option_vars:
            value = var.get()
            if option.choices:
                value = option.choices[var.get()]
            option.validate(value)
            cfg[option.varname] = value
        return cfg

    def log_parameters(self):
        if not self.has_options():
            messagebox.showinfo("Nothing to see here...", "No options to log.")
            return

        msg = "Parsing parameters...\n"
        for opt, var in self.option_vars:
            v = var.get()
            if opt.choices:
                v = opt.choices[v]
            n = opt.varname
            n, v, t = str(n), str(v), type(v).__name__
            msg += "{}: (value, type) -> ({}, {})\n".format(n, v, t)

        logging.info(msg)
        messagebox.showinfo("Parameters logged!",
                            "See log for loaded parameters.")

    def has_options(self):
        return bool(self.option_vars)


class OptionsFileFrame(LabelFrame):
    def __init__(self, parent, options_files: ScorerOptionsFiles, **config):
        super().__init__(parent, **config)
        self.row = 0
        self.widgets = []
        self.labels = []
        self.scorer_parameter_dicts = []
        self.make_widgets(options_files)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def make_widgets(self, options_files: ScorerOptionsFiles):
        if not len(options_files):
            label_text = "No options found."
            label = Label(self, text=label_text, justify=LEFT)
            label.grid(sticky=EW, columnspan=1, row=self.row, padx=5, pady=5)
            self.rowconfigure(self.row, weight=1)
            self.row += 1

            btn = Button(self, text='Show Parameters',
                         command=self.no_options_message)
            btn.grid(row=self.row, column=1, sticky=SE, padx=5, pady=5)
            self.rowconfigure(self.row, weight=1)
            self.row += 1
            return

        for options_file in options_files:
            self._make_label(options_file)
            self._make_button(options_file)
            self.rowconfigure(self.row, weight=1)
            self.row += 1

        btn = Button(self, text='Show Parameters', command=self.log_parameters)
        btn.grid(row=self.row, column=1, sticky=SE, padx=5, pady=5)
        self.rowconfigure(self.row, weight=1)
        self.row += 1
        return

    def _make_label(self, options_file: OptionsFile):
        label_text = "{}: ".format(options_file.name)
        label = Label(self, text=label_text, justify=LEFT)
        label.grid(row=self.row, column=0, sticky=EW, padx=5, pady=5)

    def _make_button(self, options_file: OptionsFile):
        command = lambda opt=options_file: self.load_file(opt)
        button = Button(self, text='Choose...', command=command)
        button.grid(row=self.row, column=1, sticky=E, padx=5, pady=5)

    def load_file(self, options_file: OptionsFile):
        file_path = askopenfilename()
        if not file_path:
            return
        cfg_error_msg = "There was an error parsing file {}. " \
                        "\n\nPlease see log for details.".format(file_path)
        validation_error_msg = "There was an error during validation. " \
                               "\n\nPlease see log for details."
        type_error = "Parsing functions must return a python dictionary."
        empty_error = "Parsing function returned an empty dictionary"
        success = 'Successfully parsed and validated file: \n\n{}'.format(
            file_path)

        try:
            cfg = options_file.parse_to_dict(file_path)
            if not isinstance(cfg, dict):
                raise TypeError(type_error)
            if not cfg:
                raise ValueError(empty_error)
        except BaseException as error:
            logging.exception(error)
            messagebox.showerror('Parse Error', cfg_error_msg)
            return

        try:
            options_file.validate_cfg(cfg)
            self.scorer_parameter_dicts.append((options_file.name, cfg))
        except BaseException as error:
            logging.exception(error)
            messagebox.showerror('Validation Error', validation_error_msg)
            return
        messagebox.showinfo('Success!', success)

    def get_option_cfgs(self):
        return self.scorer_parameter_dicts

    def no_options_message(self):
        msg = "No options were found in the loaded plugin script."
        messagebox.showinfo("Nothing to see here...", msg)
        return

    def str_nested(self, data, tab_level=1):
        msg = ""
        if isinstance(data, list) or isinstance(data, tuple):
            if not data:
                msg += 'Empty Iterable'
            else:
                msg += "-> Iterable"
                for i, item in enumerate(data):
                    msg += '\n' + '\t' * tab_level + '@index {}: '.format(i)
                    msg += self.str_nested(item, tab_level)
                msg += '\n' + '\t' * tab_level + '@end of list'
        elif isinstance(data, dict):
            if not data:
                msg += 'Empty Dictionary'
            else:
                msg += "-> Dictionary"
                for key, value in data.items():
                    msg += '\n' + "\t" * tab_level + "{}: ".format(key)
                    msg += self.str_nested(value, tab_level + 1)
        else:
            if isinstance(data, str):
                data = "'{}'".format(data)
            dtype = type(data).__name__
            msg += "({}, {})".format(data, dtype)
        return msg

    def log_parameters(self):
        if not self.scorer_parameter_dicts:
            messagebox.showinfo(
                "Nothing to see here...",
                "Please select files to parse first.")
            return
        for name, cfg in self.scorer_parameter_dicts:
            msg = "Parsing parameters...\n{}: (value, type) ".format(name)
            msg += self.str_nested(cfg, tab_level=0)
            logging.info(msg)
        messagebox.showinfo("Parameters logged!",
                            "See log for loaded parameters.")

    def has_options(self):
        return bool(self.labels)


class ScorerScriptsDropDown(Frame):
    def __init__(self, parent=None, scripts_dir='plugins/', **config):
        super().__init__(parent, **config)
        self.parent = parent
        self.row = 0
        self.current = ''

        self.plugins = {}
        for path in glob.glob("{}/*.py".format(scripts_dir)):
            path = path.replace("\\", '/')
            if "__init__.py" in path:
                continue
            try:
                result = self.load_plugin(path)
            except Exception as e:
                logging.error(e)
                messagebox.showerror(
                    "Error loading plugin...",
                    "There was an error loading the script:\n\n{}." \
                    "\n\nSee log for details.".format(
                        os.path.join(os.getcwd(), path))
                )
                continue
            klass, options_frame, options_file_frame = result
            self.plugins[klass.__name__] = (
                klass, options_frame, options_file_frame)

        if not self.plugins:
            raise ImportError("No plugins could be loaded.")

        self.make_drop_down_menu(self.plugins)
        self.update_options_view('RegressionScorer')

    def increment_row(self):
        # self.rowconfigure(self.row, weight=1)
        self.row += 1

    def get_class_and_attrs(self):
        klass, options_frame, options_file_frame = self.plugins[self.current]
        options_cfg = [options_frame.get_option_cfg()]
        options_files_cfgs = [cfg for _, cfg in
                              options_file_frame.get_option_cfgs()]
        attrs = {}
        cfgs = options_cfg + options_files_cfgs
        for dict_ in cfgs:
            for k, v in dict_.items():
                attrs[k] = v
        return klass, attrs

    def load_plugin(self, path):
        result = load_scoring_class_and_options(path)
        klass, options, options_files = result
        options_frame = OptionFrame(self, options, text='Options')
        options_file_frame = OptionsFileFrame(
            self, options_files, text='Option Files')
        return klass, options_frame, options_file_frame

    def make_drop_down_menu(self, plugins):
        switch = lambda v: self.update_options_view(v)
        choices = [n for n, _ in plugins.items()]
        menu_var = StringVar(self)

        frame = ttk.LabelFrame(self, text='Plugins')
        label = Label(frame, text="Variant Scorer: ", justify=LEFT)
        label.grid(sticky=EW, column=0, row=0, padx=5, pady=5)
        popup_menu = OptionMenu(frame, menu_var, 'RegressionScorer', *choices,
                                command=switch)
        popup_menu.grid(sticky=E, column=1, row=0, padx=5, pady=5)

        frame.grid(sticky=NSEW, columnspan=1, row=self.row, padx=5, pady=5)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)
        self.row += 1

    def update_options_view(self, new_name):
        if self.current:
            _, options_frame, options_file_frame = self.plugins[self.current]
            self.hide_frame(options_frame)
            self.hide_frame(options_file_frame)

        _, options_frame, options_file_frame = self.plugins[new_name]
        self.show_frame(options_frame)
        self.show_frame(options_file_frame)

        self.current = new_name

    def hide_frame(self, frame):
        frame.grid_forget()
        self.row -= 1

    def show_frame(self, frame):
        frame.grid(sticky=NSEW, row=self.row)
        self.increment_row()
