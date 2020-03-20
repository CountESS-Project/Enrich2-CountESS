"""
Enrich2 experiment experiment module
====================================

This module contains the class used by ``Enrich2`` to represent a condition. 
This class coordinates experimental selections.
"""


from ..base.storemanager import StoreManager
from ..selection.selection import Selection


__all__ = ["Condition"]


class Condition(StoreManager):
    """
    Dummy class for experimental conditions within an 
    :py:class:`~enrich2.experiment.experiment.Experiment`. 
    
    Required for proper GUI behavior.
    
    Attributes
    ----------
    selections : `list`
        List of :py:class:`enrich2.selection.selection.Selection` objects.
        
    Methods
    -------
    configure
        Configures the object from an dictionary loaded from a configuration 
        file.
    serialize
        Returns a `dict` with all configurable attributes stored that can
        be used to reconfigure a new instance.
    validate
        Validates the attributes of this instance.
    _children 
        Concrete method returning sorted selections.
    remove_child_id
        Removes the child with the specified ``treeview_id`` 
    add_child
        Adds a child to this instance's children.
    """

    has_store = False  # don't create an HDF5 for Conditions
    treeview_class_name = "Condition"

    def __init__(self):
        StoreManager.__init__(self)
        self.selections = list()

    def configure(self, cfg, configure_children=True, init_from_gui=False):
        """
        Set up the :py:class:`~enrich2.experiment.condition.Condition` 
        using the *cfg* object, usually from a ``.json`` configuration file.

        Parameters
        ----------
        cfg : `dict` or :py:class:`~enrich2.config.types.ExperimentConfiguration`
            The object used to configure this instance.
        configure_children : `bool`
            Traverse children and configure each one.
        init_from_gui : `bool` 
            Allow this instance to be configured from a GUI.

        """
        from ..config.types import ConditonConfiguration

        if isinstance(cfg, dict):
            cfg = ConditonConfiguration(cfg, init_from_gui)
        elif not isinstance(cfg, ConditonConfiguration):
            raise TypeError("`cfg` was neither a ConditonConfiguration or dict.")

        StoreManager.configure(self, cfg.store_cfg)
        if configure_children:
            if len(cfg.selection_cfgs) == 0:
                raise KeyError(
                    "Missing required config value "
                    "{} [{}]".format("selections", self.name)
                )
            for sel_cfg in cfg.selection_cfgs:
                sel = Selection()
                sel.configure(sel_cfg)
                self.add_child(sel)

    def serialize(self):
        """
        Format this object (and its children) as a config object suitable
        for dumping to a config file.
        """
        cfg = StoreManager.serialize(self)
        cfg["selections"] = [child.serialize() for child in self.children]
        return cfg

    def validate(self):
        """
        Calls validate on all child Selections.
        """
        for child in self.children:
            child.validate()

    def _children(self):
        """
        Method bound to the ``children`` property. Returns a list of all 
        :py:class:`~enrich2.selection.selection.Selection` objects belonging 
        to this object, sorted by name.
        
        Returns
        -------
        `list`
            List of sorted selection objects, sorted by name.
        """
        return sorted(self.selections, key=lambda x: x.name)

    def add_child(self, child):
        """
        Add a :py:class:`~enrich2.selection.selection.Selection`
        """
        if child.name in self.child_names():
            raise ValueError(
                "Non-unique selection " "name '{}' [{}]".format(child.name, self.name)
            )
        child.parent = self
        self.selections.append(child)

    def remove_child_id(self, tree_id):
        """
        Remove the reference to a 
        :py:class:`~enrich2.selection.selection.Selection` with 
        Treeview id *tree_id*.
        """
        self.selections = [x for x in self.selections if x.treeview_id != tree_id]
