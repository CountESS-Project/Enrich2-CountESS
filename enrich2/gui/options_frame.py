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
import tkinter.messagebox as messagebox
from tkinter.filedialog import askopenfilename, asksaveasfile

from ..plugins.options import Options, Option, HiddenOptions
from ..plugins.options import OptionsFile
from ..plugins import load_scoring_class_and_options
from ..base.utils import nested_format


LabelFrame = ttk.LabelFrame
Frame = ttk.Frame
Label = ttk.Label
Entry = ttk.Entry
Button = ttk.Button
Checkbutton = ttk.Checkbutton
OptionMenu = ttk.OptionMenu


class OptionFrame(Frame):
    def __init__(self, parent, options: Options, hidden_options: HiddenOptions,
                 show_btn=False, **kw):
        super().__init__(parent, **kw)
        self.parent = parent
        self.row = 0
        self.widgets = []
        self.labels = []
        self.show_btn = show_btn

        self.options = Options() \
            if options is None else options
        self.hidden_options = HiddenOptions() \
            if hidden_options is None else hidden_options
        self.vname_option_tkvars_map = {}
        self.vname_hidden_option_var_map = {}

        if options is not None:
            self.parse_options(options)
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=3)

        if hidden_options is not None:
            self.parse_hidden_options(hidden_options)

    def parse_hidden_options(self, options: HiddenOptions) -> None:
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
            data = (option, option.default)
            self.vname_hidden_option_var_map[option.varname] = data

    def parse_options(self, options: Options) -> None:
        if not len(options):
            label_text = "No options found."
            label = Label(self, text=label_text, justify=LEFT)
            label.grid(sticky=EW, columnspan=1, row=self.row)
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

        if self.show_btn:
            btn = Button(self, text='Show', command=self.log_parameters)
            btn.grid(row=self.row, column=1, sticky=SE)
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
        label.grid(sticky=EW, column=0, row=self.row)

        choices = option.choices
        choices = list(choices.keys())

        popup_menu = OptionMenu(
            self, menu_var, option.default, *choices)
        popup_menu.grid(sticky=E, column=1, row=self.row)

        self.vname_option_tkvars_map[option.varname] = (option, menu_var)
        self.widgets.append(popup_menu)
        self.labels.append(label)

    def make_entry(self, variable: Variable, option: Option) -> Entry:
        label_text = "{}: ".format(option.name)
        label = Label(self, text=label_text, justify=LEFT)
        label.grid(sticky=EW, column=0, row=self.row)

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
        entry.grid(sticky=EW, column=1, row=self.row)
        self.vname_option_tkvars_map[option.varname] = (option, variable)
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
        label.grid(sticky=EW, column=0, row=self.row)

        checkbox = Checkbutton(self, variable=variable)
        checkbox.grid(sticky=E, column=1, row=self.row)

        self.vname_option_tkvars_map[option.varname] = (option, variable)
        self.widgets.append(checkbox)
        self.labels.append(label)

    def get_option_cfg(self) -> dict:
        cfg = {}
        for vname, (option, var) in self.vname_option_tkvars_map.items():
            value = var.get()
            default = option.default
            if option.choices:
                default = option.choices[option.get_choice_key(option.default)]
                value = option.choices[var.get()]
            option.validate(value)
            cfg[vname] = (value, value == default)

        for vname, (option, value) in self.vname_hidden_option_var_map.items():
            option.validate(value)
            cfg[vname] = (value, value == option.default)
        return cfg

    def log_parameters(self):
        if not self.has_options():
            messagebox.showinfo("Nothing to see here...", "No options to log.")
            return

        msg = "Parsing parameters...\n"
        for vname, (option, var) in self.vname_option_tkvars_map.items():
            value = var.get()
            if option.choices:
                value = option.choices[value]
            vname, value, t = str(vname), str(value), type(value).__name__
            msg += "{}: (value, type) -> ({}, {})\n".format(vname, value, t)

        logging.info(msg, extra={'oname': self.__class__.__name__})
        messagebox.showinfo("Parameters logged!",
                            "See log for loaded parameters.")

    def has_options(self):
        return bool(self.labels)


class OptionsFileFrame(Frame):
    def __init__(self, parent, options_file: OptionsFile,
                 show_btn=False, **config):
        super().__init__(parent, **config)
        self.row = 0
        self.widgets = []
        self.labels = []
        self.active_cfg = {}
        self.option_frame = None
        self.show_btn = show_btn
        if options_file is not None:
            self._make_widgets(options_file)
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=3)

    def _make_widgets(self, options_file: OptionsFile):
        self._make_label(options_file)
        self._make_button(options_file)
        self.rowconfigure(self.row, weight=1)
        self.row += 1

        if self.show_btn:
            btn = Button(self, text='Print to Log', command=self.log_parameters)
            btn.grid(row=self.row, column=1, sticky=SE)
            self.rowconfigure(self.row, weight=1)
            self.row += 1
        return

    def _make_label(self, options_file: OptionsFile):
        label_text = "{}: ".format(options_file.name)
        label = Label(self, text=label_text, justify=LEFT)
        label.grid(row=self.row, column=0, sticky=EW)
        self.labels.append(label)

    def _make_button(self, options_file: OptionsFile):
        command = lambda opt=options_file: self.load_from_file(opt)
        button = Button(self, text='Load...', command=command)
        button.grid(row=self.row, column=1, sticky=E)
        self.widgets.append(button)

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
        if self.option_frame:
            if self.update_option_frame(cfg):
                self.active_cfg = cfg
                if not self.options_file_incomplete():
                    messagebox.showinfo('Success!', success)
        else:
            self.active_cfg = cfg
            messagebox.showinfo('Success!', success)

    def load_from_file(self, options_file: OptionsFile):
        file_path = askopenfilename()
        if not file_path:
            return

        self.active_cfg = {}
        cfg_error_msg = "There was an error parsing file {}. " \
                        "\n\nPlease see log for details.".format(file_path)
        validation_error_msg = "There was an error during validation. " \
                               "\n\nPlease see log for details."
        success = 'Successfully parsed and validated file: \n\n{}'.format(
            file_path)
        unused_keys_msg = "The following keys in the configuration file " \
                          "could not be not found in the plugin " \
                          "options definitions: \n\n{}\n\n" \
                          "They will not be used by the scoring plugin."
        try:
            cfg = options_file.parse_to_dict(file_path)
        except BaseException as error:
            logging.exception(error, extra={'oname': self.__class__.__name__})
            messagebox.showerror('Parse Error', cfg_error_msg)
            return

        try:
            options_file.validate_cfg(cfg)
        except BaseException as error:
            logging.exception(error, extra={'oname': self.__class__.__name__})
            messagebox.showerror('Validation Error', validation_error_msg)
            return

        self.active_cfg = cfg
        unused_keys = self.unused_options()
        if unused_keys:
            unused_keys = '\n'.join(["'{}'".format(n) for n in unused_keys])
            messagebox.showinfo(
                "Unused configuration options.",
                unused_keys_msg.format(unused_keys)
            )
        else:
            messagebox.showinfo('Success!', success)

    def apply_to_options(self):
        success = 'Successfully applied configuration file to GUI options.'
        if self.option_frame and self.active_cfg:
            if self.update_option_frame(self.active_cfg):
                incomplete_opt = self.options_file_incomplete()
                incomplete_hopt = self.hidden_options_file_incomplete()
                if not (incomplete_opt and incomplete_hopt):
                    messagebox.showinfo('Apply Options', success)
        else:
            messagebox.showinfo('Apply Options', "Nothing to apply.")

    def options_file_incomplete(self):
        if self.option_frame and self.active_cfg:
            mapping = self.option_frame.vname_option_tkvars_map
            option_vnames = list(mapping.keys())
            cfg_vnames = self.active_cfg.keys()
            unique_vnames = [n for n in option_vnames if n not in cfg_vnames]
            unique_names = [mapping[n][0].name for n in unique_vnames]
            if unique_vnames:
                unique_str = '\n'.join(["'{}'".format(n) for n in unique_names])
                message = "There are options in the plugin not found in the " \
                          "loaded configuration file. The following " \
                          "options have not been altered: \n\n" \
                          "{}".format(unique_str)
                messagebox.showwarning(
                    "Incomplete configuration file...",
                    message
                )
                return True
            return False
        return False

    def hidden_options_file_incomplete(self):
        if self.option_frame and self.active_cfg:
            mapping = self.option_frame.vname_hidden_option_var_map
            option_vnames = list(mapping.keys())
            cfg_vnames = self.active_cfg.keys()
            unique_vnames = [n for n in option_vnames if n not in cfg_vnames]
            if unique_vnames:
                unique_str = '\n'.join(["'{}'".format(n) for n in unique_vnames])
                message = "There are hidden options in the plugin not found " \
                          "in the loaded configuration file. The following " \
                          "options have not been altered: \n\n" \
                          "{}".format(unique_str)
                messagebox.showwarning(
                    "Incomplete configuration file...",
                    message
                )
                return True
            return False
        return False

    def unused_options(self):
        unused = set()
        used_keys = set(
            list(self.option_frame.vname_hidden_option_var_map.keys()) +
            list(self.option_frame.vname_option_tkvars_map.keys())
        )
        if self.option_frame:
            for vname in self.active_cfg.keys():
                if vname not in used_keys:
                    unused.add(vname)
        return unused

    def update_option_frame(self, cfg):
        for option_varname, value in cfg.items():
            try:
                self.update_option_frame_tkvar(option_varname, value)
                self.update_option_frame_hidden(option_varname, value)
            except BaseException as err:
                logging.exception(
                    err, extra={"oname": self.__class__.__name__})
                messagebox.showerror(
                    'Setting Override Error...',
                    "Couldn't set option with variable name '{}'. "
                    "Aborting parse, see log for further "
                    "details.".format(option_varname)
                )
                return False
        return True

    def update_option_frame_tkvar(self, option_varname, value):
        mapping = self.option_frame.vname_option_tkvars_map
        option, tkvar = mapping.get(option_varname, (None, None))
        if tkvar is not None:
            current_value = tkvar.get()
            try:
                if option.choices:
                    value = option.get_choice_key(value)
                option.validate(value)
                tkvar.set(value)
            except (TypeError, ValueError) as err:
                tkvar.set(current_value)
                raise BaseException(err)
        return

    def update_option_frame_hidden(self, vname, value):
        mapping = self.option_frame.vname_hidden_option_var_map
        option, old_value = mapping.get(vname, (None, None))
        if old_value is not None:
            try:
                option.validate(value)
                data = (option, value)
                self.option_frame.vname_hidden_option_var_map[vname] = data
            except (TypeError, ValueError) as err:
                raise BaseException(err)
        return

    def get_option_cfg(self):
        return self.active_cfg

    def log_parameters(self):
        if not self.active_cfg:
            messagebox.showinfo(
                "Nothing to see here...",
                "Please select files to parse first.")
            return
        msg = "Parsing parameters...\nFormat: (value, type) "
        msg += nested_format(self.active_cfg, False, tab_level=0)
        logging.info(msg, extra={'oname': self.__class__.__name__})
        messagebox.showinfo("Parameters logged!",
                            "See log for loaded parameters.")

    def link_to_options_frame(self, options_frame: OptionFrame):
        self.option_frame = options_frame

    def has_options(self):
        return bool(self.labels)


class ScorerScriptsDropDown(Frame):
    def __init__(self, parent=None, scripts_dir='plugins/', **config):
        super().__init__(parent, **config)
        self.parent = parent
        self.row = 0
        self.current = 'Regression'
        self.plugins_frame = None
        self.diagnostics_frame = None
        self.apply_btn = None

        self.plugins = {}
        for path in glob.glob("{}/*.py".format(scripts_dir)):
            path = path.replace("\\", '/')
            full_path = os.path.join(os.getcwd(), path)
            if "__init__.py" in path:
                continue
            try:
                result = self.load_plugin(path)
                klass, options_frame, options_file_frame = result
            except Exception as e:
                logging.error(e, extra={'oname': self.__class__.__name__})
                messagebox.showerror(
                    "Error loading plugin...",
                    "There was an error loading the script:\n\n{}." \
                    "\n\nSee log for details.".format(full_path))
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

        if not self.plugins:
            frame = ttk.LabelFrame(self, text='Scoring Options')
            frame.grid(sticky=NSEW, columnspan=1, row=self.row)
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=3)
            label = Label(frame, text="Scoring Plugin: ", justify=LEFT)
            label.grid(sticky=EW, column=0, row=0)

            default = 'No plugins detected'
            popup_menu = OptionMenu(frame, StringVar(), default, *[default])
            popup_menu.grid(sticky=E, column=1, row=0)

        else:
            self.make_drop_down_menu(self.plugins)
            _, options_frame, options_file_frame, _ = \
                self.plugins[self.current]
            self.show_frame(options_frame)
            self.show_frame(options_file_frame)

    def increment_row(self):
        # self.rowconfigure(self.row, weight=1)
        self.row += 1

    def get_class_and_attrs(self, keep_defult_bool=False):
        if not self.plugins:
            return None, None
        attrs = {}
        klass, opt_frame, opt_file_frame, _ = self.plugins[self.current]
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

    def load_plugin(self, path):
        result = load_scoring_class_and_options(path)
        klass, options, hidden_options, options_file = result
        options_frame = OptionFrame(self, options, hidden_options)
        options_file_frame = OptionsFileFrame(self, options_file)
        options_file_frame.link_to_options_frame(options_frame)
        return klass, options_frame, options_file_frame

    def make_drop_down_menu(self, plugins):
        choices = [n for n, _ in plugins.items()]
        menu_var = StringVar(self)

        frame = ttk.LabelFrame(self, text='Scoring Options')
        label = Label(frame, text="Scoring Plugin: ", justify=LEFT)
        label.grid(sticky=EW, column=0, row=0)

        switch = lambda v: self.update_options_view(v)
        popup_menu = OptionMenu(
            frame, menu_var, self.current, *choices, command=switch)
        popup_menu.grid(sticky=E, column=1, row=0)

        details = lambda v=menu_var: self.show_plugin_details(v.get())
        btn = Button(frame, text='Plugin Details', command=details)
        btn.grid(sticky=E, column=1, row=1)

        frame.grid(sticky=NSEW, columnspan=1, row=self.row)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)

        self.plugins_frame = frame
        self.row += 1

        frame = LabelFrame(self, text='')
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        btn = Button(frame, text='Print to Log', command=self.log_parameters)
        btn.grid(row=0, column=0, sticky=E)
        btn = Button(frame, text='Apply')
        btn.grid(row=0, column=1, sticky=E)

        self.diagnostics_frame = frame
        self.apply_btn = btn

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

    def update_options_view(self, new_name):
        if self.current:
            _, options_frame, options_file_frame, _ = \
                self.plugins[self.current]
            self.hide_frame(options_frame)
            self.hide_frame(options_file_frame)

        _, options_frame, options_file_frame, _ = self.plugins[new_name]
        self.show_frame(options_frame)
        self.show_frame(options_file_frame)

        self.current = new_name

    def hide_frame(self, frame):
        if frame.has_options():
            frame.grid_forget()
            self.row -= 1
            self.diagnostics_frame.grid_forget()
            self.row -= 1

    def show_frame(self, frame):
        if frame.has_options():
            frame.grid(sticky=NSEW, row=self.row, column=0, pady=(12, 0))
            self.increment_row()
            self.diagnostics_frame.grid(
                sticky=NSEW, row=self.row, column=0)
            self.increment_row()

            if isinstance(frame, OptionsFileFrame):
                self.apply_btn.config(command=frame.apply_to_options)
