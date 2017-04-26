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


from tkinter import *
import tkinter.messagebox as messagebox
from tkinter.ttk import *

from ..plugins.options import ScoringOptions, Option


class OptionFrame(Frame):
    def __init__(self, options: ScoringOptions, master, **kw):
        super().__init__(master, **kw)
        self.row = 1
        self.widgets = []
        self.labels = []
        self.parse_options(options)

        def get_vars():
            print(self.get_option_cfg())

        Button(master=self, text='Validate', command=get_vars).grid(
            sticky=E, column=1, row=self.row)

    def parse_options(self, options: ScoringOptions) -> None:
        for option in options:
            self.create_widget_from_option(option)
            self.row += 1

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
            raise ValueError("Unrecognised option "
                             "dtype {}.".format(option.dtype))

    def make_choice_menu_widget(self, option: Option) -> None:
        menu_var = StringVar(self)
        menu_var.set(option.default)

        label_text = "{}: ".format(option.name)
        label = Label(self, text=label_text, justify=LEFT)
        label.grid(sticky=W, column=0, row=self.row)

        popup_menu = OptionMenu(
            self, menu_var, option.default, *option.choices)
        popup_menu.grid(sticky=E, column=1, row=self.row)

        self.widgets.append((option, menu_var))
        self.labels.append(label)

    def make_entry(self, variable: Variable, option: Option) -> Entry:
        label_text = "{}: ".format(option.name)
        label = Label(self, text=label_text, justify=LEFT)
        label.grid(sticky=W, column=0, row=self.row)

        def validate_entry():
            try:
                value = variable.get()
                option.validate(value)
                variable.set(option.dtype(value))
            except (TclError, TypeError):
                messagebox.showwarning(
                    title="Invalid Entry",
                    message="Invalid type for entry {}. "
                            "Expected type {}.".format(option.name,
                                                       option.dtype.__name__)
                )
                variable.set(option.dtype(option.default))
                return False
            return True

        entry = Entry(
            self, textvariable=variable,
            validate="focusout", validatecommand=validate_entry
        )
        entry.grid(sticky=E, column=1, row=self.row)
        self.widgets.append((option, variable))
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
        label.grid(sticky=W, column=0, row=self.row)

        checkbox = Checkbutton(self, variable=variable)
        checkbox.grid(sticky=E, column=1, row=self.row)

        self.widgets.append((option, variable))
        self.labels.append(label)

    def get_option_cfg(self) -> dict:
        cfg = {}
        for option, menu_var in self.widgets:
            value = menu_var.get()
            option.validate(value)
            cfg[option.varname] = menu_var.get()
        return cfg
