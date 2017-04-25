#  Copyright 2016 Alan F Rubin, Daniel C Esposito.
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
from tkinter import END, N, S, E, W, Scrollbar, Text
from tkinter import ttk


LOG_FORMAT = "%(asctime)-15s [%(oname)s] %(message)s"


class LoggingHandler(logging.Handler):

    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.setFormatter(logging.Formatter(LOG_FORMAT))
        self.widget = widget
        self.widget.config(state='disabled')

    def emit(self, record):
        self.widget.config(state='normal')
        self.widget.insert(END, self.format(record) + "\n")
        self.widget.see(END)
        self.widget.config(state='disabled')


class LoggingFrame(ttk.Frame):

    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        self.scrollbar = Scrollbar(self)
        self.scrollbar.grid(row=0, column=1, sticky=(N, S, E))

        self.text = Text(self, yscrollcommand=self.scrollbar.set)
        self.text.grid(row=0, column=0, sticky=(N, S, E, W))

        self.scrollbar.config(command=self.text.yview)

        self.logging_handler = LoggingHandler(self.text)

    def log(self, msg):
        self.logging_handler.emit(msg)