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


import logging
import threading
import multiprocessing

import tkinter.simpledialog
import tkinter.messagebox
import tkinter.filedialog




class AnalysisThread(threading.Thread):
    """
    Dialog box for blocking input while running the analysis.
    """
    def __init__(self, parent_window):
        threading.Thread.__init__(self)
        self.pw = parent_window
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        # gray out the "Run" button
        for btn in self.pw.treeview_buttons:
            btn.config(state='disabled')
        self.pw.go_button.config(state='disabled')
        self.pw.treeview.bind("<Button-2>", lambda event: event)

        try:
            scorer_class = self.pw.get_selected_scorer_class()
            scorer_class_attrs = self.pw.get_selected_scorer_attrs()
            scorer_path = self.pw.get_selected_scorer_path()

            # set the analysis options
            self.pw.root_element.force_recalculate = \
                self.pw.force_recalculate.get()
            self.pw.root_element.component_outliers = \
                self.pw.component_outliers.get()

            self.pw.root_element.scorer_class = scorer_class
            self.pw.root_element.scorer_class_attrs = scorer_class_attrs
            self.pw.root_element.scorer_path = scorer_path
            self.pw.root_element.tsv_requested = self.pw.tsv_requested.get()

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
            logging.exception(e, extra={'oname': self.pw.root_element.name})
            tkinter.messagebox.showerror(
                "Enrich2 Error", "Enrich2 encountered an error:\n{}".format(e)
            )

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
                    logging.exception(
                        e, extra={'oname': self.pw.root_element.name})

            # show the dialog box
            tkinter.messagebox.showinfo("Analysis", "Analysis completed.")

        finally:
            # close the HDF5 files
            self.pw.treeview.bind("<Button-2>", self.pw.treeview_context_menu)
            self.pw.go_button.config(state='normal')
            for btn in self.pw.treeview_buttons:
                btn.config(state='normal')
            logging.info("Closing stores...", extra={"oname": self.name})
            self.pw.root_element.store_close(children=True)
            logging.info("Done!", extra={"oname": self.name})

        for btn in self.pw.treeview_buttons:
            btn.config(state='normal')
        self.pw.go_button.config(state='normal')
        self.pw.treeview.bind("<Button-2>", self.pw.treeview_context_menu)
