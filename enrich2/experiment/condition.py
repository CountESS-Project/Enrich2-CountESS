#  Copyright 2016-2017 Alan F Rubin
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


from enrich2.base.storemanager import StoreManager
from enrich2.selection.selection import Selection


class Condition(StoreManager):
    """
    Dummy class for experimental conditions within an 
    :py:class:`~experiment.Experiment`. Required for proper GUI behavior.
    """

    has_store = False  # don't create an HDF5 for Conditions
    treeview_class_name = "Condition"

    def __init__(self):
        StoreManager.__init__(self)
        self.selections = list()

    def configure(self, cfg, configure_children=True, init_from_gui=False):
        from ..config.types import ConditonConfiguration

        if isinstance(cfg, dict):
            cfg = ConditonConfiguration(cfg, init_from_gui)
        elif not isinstance(cfg, ConditonConfiguration):
            raise TypeError("`cfg` was neither a ConditonConfiguration or dict.")

        StoreManager.configure(self, cfg.store_cfg)
        if configure_children:
            if len(cfg.selection_cfgs) == 0:
                raise KeyError("Missing required config value "
                               "{} [{}]".format('selections', self.name))
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
        cfg['selections'] = [child.serialize() for child in self.children]
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
        :py:class:`~selection.Selection` objects belonging to this object, 
        sorted by name.
        """
        return sorted(self.selections, key=lambda x: x.name)

    def add_child(self, child):
        """
        Add a :py:class:`~selection.Selection`.
        """
        if child.name in self.child_names():
            raise ValueError("Non-unique selection "
                             "name '{}' [{}]".format(child.name, self.name))
        child.parent = self
        self.selections.append(child)

    def remove_child_id(self, tree_id):
        """
        Remove the reference to a :py:class:`~selection.Selection` with 
        Treeview id *tree_id*.
        """
        self.selections = [
            x for x in self.selections
            if x.treeview_id != tree_id
        ]
