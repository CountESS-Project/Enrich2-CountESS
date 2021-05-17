from .dialog import CustomDialog
from tkinter.ttk import *
from tkinter import E


def subtree_ids(treeview, x, level=0):
    """
    Return a list of tuples containing the ids and levels for *x* 
    and every element below it in the Treeview *treeview*.

    The level of *x* is 0, children of *x* are 1, and so forth.
    
    Parameters
    ----------
    treeview : `Treeview`
        The treeview to traverse
    x : `object`
        enrich2 object id.
    level : `int`, default: 0
        The level in the tree to start at.
    """
    id_list = list()
    id_list.append((x, level))
    for y in treeview.get_children(x):
        id_list.extend(subtree_ids(treeview, y, level + 1))
    return id_list


class DeleteDialog(CustomDialog):
    """
    Confirmation dialog box for deleting the selected items from the Treeview.
    
    
    Parameters
    ----------
    parent_window : `TopLevel` or `Tk`
        Parent Tk window managing this dialog
    tree : `Tk`
        Tk object containing a treeview the delete dialog box should reference. 
    title : `str`: default: 'Create Root Object'
        The title of the dialog window.
        
    Attributes
    ----------
    tree : `Treeview`
        The treeview of the main app.
    id_tuples: `list`
        A list of tuples containing (id, object) to house an elements
        id and related instance.
    
    Methods
    -------
    body
        Creates the body for the root dialog, laying out the radio boxes
        choices for each root object type (experiment, selection, library).
    buttonbox
        Creates a buttonbox to handles the radio box selection.
    apply
        Applies the root configuration to the selected root element upon
        clicking `ok`.
      
    See Also
    --------
    :py:class:`~enrich2.gui.dialog.CustomDialog`
    """

    def __init__(self, parent_window, tree, title="Confirm Deletion"):
        self.tree = tree
        self.id_tuples = list()
        for x in self.tree.treeview.selection():
            if x not in [y[0] for y in self.id_tuples]:
                self.id_tuples.extend(subtree_ids(self.tree.treeview, x))
        CustomDialog.__init__(self, parent_window, title)

    def body(self, master):
        """
        Generates the required text listing all elements that will be deleted.

        Displays the "OK" and "Cancel" buttons.
                
        Parameters
        ----------
        master : `TopLevel` or `Tk`
            Master window.
        """
        if len(self.id_tuples) == 0:
            message_string = "No elements selected."
        elif len(self.id_tuples) == 1:
            message_string = 'Delete "{}"?'.format(
                self.tree.get_element(self.id_tuples[0][0]).name
            )
        else:
            message_string = "Delete the following items?\n"
            for x, level in self.id_tuples:
                if level == 0:
                    bullet = "    " + u"\u25C6"
                else:
                    bullet = "    " * (level + 1) + u"\u25C7"
                message_string += u"{bullet} {name}\n".format(
                    bullet=bullet, name=self.tree.get_element(x).name
                )
        message = Label(master, text=message_string, justify="left")
        message.grid(row=0, sticky="w")

    def buttonbox(self):
        """
        Display only one button if there's no selection. 
        Otherwise, use the default method to display two buttons.
        """
        if len(self.id_tuples) == 0:
            box = self.button_box
            w = Button(box, text="OK", width=10, command=self.cancel, anchor=E)
            w.pack(side="left", padx=5, pady=5)
            self.bind("<Return>", self.cancel)
        else:
            CustomDialog.buttonbox(self)

    def apply(self):
        """
        Called when the user chooses "OK". Performs the deletion.
        """
        for tree_id, _ in self.id_tuples:
            self.tree.delete_element(tree_id)
        self.tree.refresh_treeview()
