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

import sys
import logging

from tkinter import *
import tkinter.ttk as ttk
import tkinter.simpledialog
import tkinter.messagebox
import tkinter.filedialog


class RunnerSavePrompt(tkinter.simpledialog.Dialog):
    """
    Dialog box for prompting the user to save before running.
    """
    def __init__(self, parent_window, title="Enrich2"):
        self.pw = parent_window

        self.dialog_text = StringVar()
        self.dialog_text.set("Would you like to save your config changes?")

        tkinter.simpledialog.Dialog.__init__(self, parent_window, title)

    def body(self, master):
        frame = ttk.Frame(master, padding=(12, 6, 12, 6))
        frame.pack()

        dialog_text_label = ttk.Label(frame, textvariable=self.dialog_text)
        dialog_text_label.grid(column=0, row=0, sticky="nsew")

    def apply(self):
        self.pw.menu_save()


class RunnerWindow(tkinter.simpledialog.Dialog):
    """
    Dialog box for blocking input while running the analysis.
    """
    def __init__(self, parent_window, title="Enrich2"):
        self.pw = parent_window
        self.run_button = None

        self.dialog_text = StringVar()
        self.dialog_text.set("Ready to start analysis...")

        tkinter.simpledialog.Dialog.__init__(self, parent_window, title)

    def body(self, master):
        frame = ttk.Frame(master, padding=(12, 6, 12, 6))
        frame.pack()

        dialog_text_label = ttk.Label(frame, textvariable=self.dialog_text)
        dialog_text_label.grid(column=0, row=0, sticky="nsew")

        self.run_button = Button(frame, text="Begin", width=10,
                                    command=self.runner, default="active")
        self.run_button.grid(column=0, row=1, sticky="nsew")

    def buttonbox(self):
        """
        Display no buttons.
        """
        pass

    def runner(self):
        # gray out the "Run" button
        self.run_button.config(state='disabled')
        self.update_idletasks()

        scorer_class = self.pw.get_selected_scorer_class()
        scorer_class_attrs = self.pw.get_selected_scorer_attrs()

        # -------------------- temp code --------------------------- #
        if scorer_class.__name__ == 'RegressionScorer':
            logr_method = scorer_class_attrs['logr_method']
            weighted = scorer_class_attrs['weighted']
            if weighted:
                scoring_method = 'WLS'
            else:
                scoring_method = 'OLS'

        elif scorer_class.__name__ == 'RatiosScorer':
            logr_method = scorer_class_attrs['logr_method']
            scoring_method = 'ratios'

        elif scorer_class.__name__ == 'SimpleScorer':
            logr_method = 'wt'
            scoring_method = 'simple'
        else:
            raise ValueError("Can't use any other plugins at the moment")

        # -------------------- end temp code ------------------------ #

        # set the analysis options
        self.pw.root_element.force_recalculate = \
            self.pw.force_recalculate.get()
        self.pw.root_element.component_outliers = \
            self.pw.component_outliers.get()

        # self.pw.root_element.scoring_method = self.pw.scoring_method.get()
        self.pw.root_element.scoring_class = scorer_class
        self.pw.root_element.scoring_class_attrs = scorer_class_attrs

        self.pw.root_element.scoring_method = scoring_method
        self.pw.root_element.logr_method = logr_method
        self.pw.root_element.tsv_requested = self.pw.tsv_requested.get()

        # run the analysis, catching any errors to display in a dialog box
        try:
            # ensure that all objects are valid
            print("Validating")
            self.pw.root_element.validate()

            # open HDF5 files for the root and all child objects
            print("Opening")
            self.pw.root_element.store_open(children=True)

            # perform the analysis
            print("Computing")
            self.pw.root_element.calculate()

        except Exception as e:
            # display error
            logging.error(e, extra={'oname': self.pw.root_element.name})
            tkinter.messagebox.showerror(
                "Enrich2 Error", "Enrich2 encountered an error:\n{}".format(e))

        else:
            # no exception occurred during calculation and setup
            # generate desired output
            if self.pw.tsv_requested.get():
                try:
                    self.pw.root_element.write_tsv()
                except Exception as e:
                    tkinter.messagebox.showwarning(
                        None, "Calculations completed, "
                              "but tsv output failed:\n{}".format(e))

            # show the dialog box
            tkinter.messagebox.showinfo("Analysis", "Analysis completed.")

        finally:
            # close the HDF5 files
            self.pw.root_element.store_close(children=True)

            # close this window
            self.destroy()
