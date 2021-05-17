from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import askokcancel
from tkinter.filedialog import asksaveasfile
import logging


LOG_FORMAT = "%(asctime)-15s [%(oname)s] %(message)s"


class ScrolledText(Frame):
    """
    Class representing a tk widget for scrolling text. For use in 
    a logging window.
    
    Parameters
    ---------- 
    parent : :py:class:`~tkinter.ttk.Frame` or :py:class:`~tkinter.TopLevel`
        The parent frame or window of this object.
        
    Attributes
    ----------
    parent : :py:class:`~tkinter.ttk.Frame` or :py:class:`~tkinter.TopLevel`
        The parent frame or window of this object.
    text : :py:class:`tkinter.Text`
        Text object inside this frame.
    menu : :py:class:`tkinter.Menu`
        The menu of the frame.
        
    Methods
    -------
    _make_scrolling_text : 
        Makes the scrolling text widget and grid-packs it into this Frame.
    show_menu
        Creates a popup-menu on right button click.
    copy_text:
        Copies the current text in selection.
    get_text:
        Gets all the text in `text`.
    set_text:
        Adds new text to the widget.
    save_text:
        Asks to save all text to a file.
    set_text_widget_state:
        Sets the text widget state.
        
    See Also
    --------
    :py:class:`~tkinter.Text`
    :py:class:`~tkinter.Menu`
    """

    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.text = self._make_scrolling_text()
        self.text.bind("<Key>", lambda e: "break")
        self.pack(expand=YES, fill=BOTH)

        self.menu = Menu(self, tearoff=0)
        self.menu.add_command(label="Copy", command=self.copy_text)
        self.parent.bind_class("Text", "<Button-2>", self.show_menu)

    def _make_scrolling_text(self):
        """
        Makes the scrolling text widget and grid-packs it into this Frame.
        """
        sbar = Scrollbar(self)
        text = Text(self, relief=SUNKEN)

        # Cross-link and move scrollbar to follow text
        sbar.config(command=text.yview)
        text.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        text.pack(side=LEFT, expand=YES, fill=BOTH)
        return text

    def show_menu(self, event):
        """
        Creates a popup-menu on right button click.
        
        Parameters
        ----------
        event : :py:class:`~tkinter.Event`
            An event object passed in by a mouse-click.
        """
        self.menu.post(event.x_root, event.y_root)
        return self

    def copy_text(self):
        """
        Copies the current text in selection.
        """
        try:
            selection = self.text.selection_get()
            self.parent.clipboard_clear()
            self.parent.clipboard_append(str(selection))
        except TclError:
            return
        return self

    def set_text(self, text=""):
        """
        Appends *text* to the current Text widget's text.
        
        Parameters
        ----------
        text : `str`
            Text to append.
        """
        self.set_text_widget_state("normal")
        self.text.insert(END, text)
        self.text.see(END)
        # self.set_text_widget_state("disabled")
        return self

    def get_text(self):
        """
        Gets all the text inside the Text widget.
        """
        return self.text.get("1.0", END + "-1c")

    def save_text(self):
        """
        Asks to save text to a file.
        """
        fp = asksaveasfile()
        if fp is not None:
            fp.write(self.get_text())
            fp.close()
        return self

    def set_text_widget_state(self, state):
        """
        Sets the state of the text widget.
        
        Parameters
        ----------
        state : `str`
            The state string used by tkinter.
        """
        self.text.config(state=state)
        return self


class WindowLoggingHandler(logging.Handler):
    """
    A log handler object which exists in a tkinter TopLevel window.
    
    Parameters
    ----------
    window : :py:class:`~tkinter.TopLevel`
        TopLevel window to create this logger in.
    level : logging Level.
        The logging Level set. No messages below *level* are logged.
    
    Attributes
    ----------
    window : :py:class:`~tkinter.TopLevel`
        TopLevel window to create this logger in.
    scrolling_text : :py:class:`~ScrolledText`
        The scrolling text object used to write log messages to.
        
    Methods
    -------
    close_window
        Close window. Asks for confirmation first just in case.
    show
        Show the window
    hide
        Hides the window
    emit
        Emits a :py:class:`~logging.LogRecord` when a log event is requested.
    mainloop
        Begins the main apploop of the window
    basic_handler
        Factory method for creating a basic instantiation of this handler.
    """

    def __init__(self, window=None, level=logging.NOTSET):
        logging.Handler.__init__(self, level)
        self.window = window
        self.visible = False
        if window is None:
            self.window = Tk()

        self.scrolling_text = ScrolledText(parent=self.window)
        self.scrolling_text.set_text_widget_state("disabled")
        self.scrolling_text.pack(
            side=TOP, expand=YES, fill=BOTH, padx=(2, 2), pady=(2, 2)
        )

        button_frame = Frame(self.window)
        save_btn = Button(
            master=button_frame,
            text="Save As...",
            command=self.scrolling_text.save_text,
        )
        save_btn.pack(side=RIGHT, anchor=S, padx=5, pady=5)
        close_btn = Button(master=button_frame, text="Hide", command=self.hide)
        close_btn.pack(side=RIGHT, anchor=S, padx=5, pady=5)
        button_frame.pack(side=BOTTOM, expand=NO, fill=BOTH, padx=(2, 2), pady=(2, 2))
        self.window.protocol("WM_DELETE_WINDOW", self.hide)

    def close_window(self):
        """
        Close window. Asks for confirmation first just in case.
        """
        close = askokcancel(
            "Close Logger", "Do you really want to close the logging window?"
        )
        if close:
            self.close()
            logger = logging.getLogger()
            logger.removeHandler(self)
            self.window.destroy()

    def show(self):
        """
        Show the window
        """
        self.window.update()
        self.window.deiconify()
        self.window.lift()
        self.window.attributes("-topmost", True)
        self.window.after_idle(self.window.attributes, "-topmost", False)
        self.visible = True

    def hide(self):
        """
        Hides the window
        """
        self.window.withdraw()
        self.visible = False

    def emit(self, record):
        """
        Emits a :py:class:`~logging.LogRecord` when a log event is requested.
        
        Parameters
        ----------
        record : :py:class:`~logging.LogRecord`
            The record to emit to logging module.
        """
        text = self.format(record) + "\n"
        self.scrolling_text.set_text(text)

    def mainloop(self):
        """
        Begins the main apploop of the window
        """
        self.window.mainloop()

    @classmethod
    def basic_handler(cls, toplevel=None, fmt=LOG_FORMAT, level=logging.NOTSET):
        """
        Creates a basic version of a :py:class:`WindowLoggingHandler`
        
        Parameters
        ----------
        toplevel : :py:class:`~tkinter.TopLevel`
            TopLevel window to create this logger in.
        fmt : `str`
            A string format to use during logging.
        level : logging Level.
            The logging Level set. No messages below *level* are logged.

        Returns
        -------
        :py:class:`WindowLoggingHandler`
        """
        handler = cls(window=toplevel, level=level)
        formatter = logging.Formatter(fmt=fmt)
        handler.setFormatter(formatter)
        return handler


def show_log_window():
    """
    Utility function to open a new logging window if one doesn't already exist,
    otherwise show the current one.
    """
    current_handlers = logging.getLogger().handlers
    log_windows = [
        h for h in current_handlers if h.__class__.__name__ == "WindowLoggingHandler"
    ]
    if not log_windows:
        log_win = WindowLoggingHandler.basic_handler(Toplevel())
        logging.getLogger().addHandler(log_win)
        logging.info("Starting new log...", extra={"oname": "Main"})
    else:
        log_win = log_windows[0]
        if not log_win.visible:
            log_win.show()
        else:
            log_win.hide()
