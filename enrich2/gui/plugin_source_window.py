#  Copyright 2016-2017 Alan F Rubin, Daniel C Esposito
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
#  along with Enrich2. If not, see <http://www.gnu.org/licenses/>.


from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askdirectory

import os
import logging
from hashlib import md5


from ..base.utils import log_message


SOURCES = os.path.join(os.path.expanduser('~'), '.enrich2/sources.txt')


class SourceWindow(Toplevel):
    def __init__(self, master=None, sources_file=SOURCES, **kwargs):
        Toplevel.__init__(self, master, **kwargs)
        self.row = 0
        self.visible = False
        self.title = 'Plugin Sources'

        self.sources_file = sources_file
        self.current_stamp = md5(open(sources_file, 'rb').read())

        self.sources = set()
        self.sources = self.load_sources_from_file()

        self.listbox = None

        self._setup_scrollbar_and_listbox()
        self._setup_buttons()

        self.protocol("WM_DELETE_WINDOW", self.hide)

    def _setup_scrollbar_and_listbox(self):
        list_box_frame = Frame(self)
        list_box_frame.rowconfigure(0, weight=1)
        list_box_frame.columnconfigure(0, weight=1)
        list_box_frame.columnconfigure(1, weight=0)
        list_box_frame.grid(row=0, column=0, sticky=NSEW)

        self.listbox = Listbox(list_box_frame)
        self.listbox.grid(sticky=NSEW, row=0, column=0, padx=(2, 2),
                          pady=(2, 2))

        list_ysb = Scrollbar(list_box_frame, orient="vertical",
                             command=self.listbox.yview)
        list_xsb = Scrollbar(list_box_frame, orient="horizontal",
                             command=self.listbox.xview)
        list_ysb.grid(row=0, column=1, sticky=N + S + W, padx=(0, 2),
                      pady=(2, 0))
        list_xsb.grid(row=1, column=0, sticky=E + W + N, padx=(2, 0),
                      pady=(0, 0))
        self.listbox.config(yscroll=list_ysb.set, xscroll=list_xsb.set)

        list_box_frame.grid(sticky=NSEW, row=0, column=0)
        self.rowconfigure(self.row, weight=1)
        self.columnconfigure(0, weight=1)
        self.row += 1

        for source in self.sources:
            self.listbox.insert(END, source)

    def _setup_buttons(self):
        buttons = Frame(self)
        delete = Button(buttons, text="Remove", command=self.remove_item)
        delete.grid(sticky=W, row=0, column=1, padx=5, pady=5)
        insert = Button(buttons, text="Add", command=self.insert_item)
        insert.grid(sticky=W, row=0, column=0, padx=5, pady=5)
        save = Button(buttons, text="Done", command=self.save_and_quit)
        save.grid(sticky=E, row=0, column=2, padx=5, pady=5)

        buttons.grid(sticky=EW, row=self.row, column=0)
        buttons.columnconfigure(2, weight=3)
        self.row += 1

    def _source_is_valid(self, source_path):
        return source_path and os.path.exists(source_path)

    def toggle_show(self):
        if not self.visible:
            self.show()
        else:
            self.hide()

    def hide(self):
        self.visible = False
        self.withdraw()

    def show(self):
        self.visible = True
        self.poll_file_changes()
        self.update()
        self.deiconify()
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)

    def save_and_quit(self):
        with open(self.sources_file, 'wt') as fp:
            for source in self.sources:
                fp.write('{}\n'.format(source))
        self.hide()

    def poll_file_changes(self):
        stamp = md5(open(self.sources_file, 'rb').read())
        if stamp != self.current_stamp:
            self.update_listbox()
            self.current_stamp = stamp

    def load_sources_from_file(self):
        sources = set()
        with open(self.sources_file, 'rt') as fp:
            for line in fp:
                path = line.strip()
                if not self._source_is_valid(path):
                    log_message(
                        logging_callback=logging.warning,
                        msg='{} is not a valid source.'.format(path),
                        extra={'oname': self.__class__.__name__}
                    )
                else:
                    sources.add(path)
        return sources

    def update_listbox(self):
        self.sources |= self.load_sources_from_file()
        self.listbox.delete(0, END)
        for source in self.sources:
            self.listbox.insert(END, source)

    def remove_item(self):
        if self.listbox.curselection():
            item_idx = self.listbox.curselection()[0]
            item = self.listbox.get(item_idx)
            self.listbox.delete(ANCHOR)
            self.sources = set([x for x in self.sources if x != item])

    def insert_item(self):
        source_folder = askdirectory()
        if self._source_is_valid(source_folder):
            self.listbox.insert(END, source_folder)
            self.sources.add(source_folder)

    def active_plugin_sources(self):
        return self.sources