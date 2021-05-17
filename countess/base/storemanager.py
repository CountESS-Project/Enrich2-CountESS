"""
Enrich2 base storemanager module
================================

Contains the abstract data-containing class StoreManager
"""


import os
import time
import getpass
import collections
import pandas as pd

from .utils import nested_format
from ..base.utils import fix_filename
from .config_constants import SCORER, SCORER_PATH
from ..base.constants import ELEMENT_LABELS
from countess.store.hdf import HdfStore

import logging
from ..base.utils import log_message


__all__ = ["StoreManager"]


class StoreManager(object):
    """
    Abstract class for all data-containing classes

    Contains common operations for all data-containing classes, such as HDF5
    store and directory management.
    
    Class Attributes
    ----------------
    store_suffix : str
        The string suffix to place before ``name``.
    has_store : bool
        Indicates if the object is currently managing a store.
    treeview_class_name : str
        Class name used by the GUI treeview to render a readable name.
    
    Attributes
    ----------
    name : str
        Name of the object, usually set through a configuration file or 
        the GUI.
    parent : :py:class:`StoreManager`
        The parent :py:class:`StoreManager` of this instance.
    
    username : str
        Username as returned by the :py:func:`getpass.getuser()` method.
    creationtime : str
        The ASCII time string generated at instantiation.
    
    store_cfg : dict
        The `dict` used to instantiate the object via the ``configuration`` 
        method, and modified by the ``serialize`` method.
    store_path : str
        The filepath to the store being managed by this instance.
    store : :py:class:`enrich2.base.store_interface.HDFStore`
        The store being managed by this instance.
    chunksize: int
        Chunksize used when iterating and selecting rows/columns from an
        open store.
    
    scorer_class : :py:class:`enrich2.plugins.scoring.BaseScorerPlugin`
        The class that has been loaded from a plugin script.
    scorer_class_attrs : dict
        The attributes required by ``scorer_class`` to run score computation. 
    scorer_path : str
        The filepath pointing to the python script used to load the current
        plugin.
    
    treeview_id : int
        Numeric id for an instance used internally by 
        :py:class:`~tkinter.ttk.Treeview`
    treeview_info : str
        String descriptor for use by :py:class:`~tkinter.ttk.Treeview` to
        provide information in the GUI
    
    Methods
    -------
    child_labels
        Returns a list of labels shared by every child.
    labels
        Property for returning labels shared by all children.
    force_recalculate
        Property for ``_force_recalculate`` private attribute. Sets/gets the
        boolean indicating if all data will be recomputed despite previous
        stores being foundl
    component_outliers
        Property for ``_component_outliers`` private attribute. Sets/gets the
        boolean indicating if outliers will be computed.
    tsv_requested
        Property for ``_tsv_requested`` private attribute. Sets/gets the
        boolean indicating if tsv files will be written.
    scoring_method
        Property for ``_scoring_method`` private attribute. Sets/gets the name
        of the current ``scoring_class`` if present.
    output_dir
        Property for ``_output_dir`` private attribute. Sets/gets the current
        output directory.
    output_dir_override 
        Property for ``_output_dir_override`` private attribute. Sets/gets 
        the boolean indicating if the output directory will be overridden.
    tsv_dir 
        Property for ``_tsv_dir`` private attribute. Sets/gets 
        the tsv output directory.
    logr_method
        Property for ``_logr_method`` private attribute. Sets/gets the name
        of the current normalization method if it has been defined in the 
        currently loaded plugin.
    children
        Returns the list of child objects owned by this instance.
    _children 
        Virtual method that must be overriden by a concrete implementation.
    remove_child_id
        Removes the child with the specified ``treeview_id`` 
    add_child
        Adds a child to this instance's children.
    child_names
        Returns a list of child names owned by this instance.
    add_label
        Add a string element label to this object.
    configure
        Configures the object from an dictionary loaded from a configuration 
        file.
    serialize
        Returns a `dict` with all configurable attributes stored that can
        be used to reconfigure a new instance.
    validate
        Validates the attributes of this instance.
    store_open
        Opens the currently owned store.
    store_close
        Closes the currently owned store.
    get_metadata
        Returns the metadata of this instance.
    set_metadata
        Sets the metadata of this instance.
    calculate
        Compute variant/barcode/identifier/synonymous scores. Delegates the
        computation to the currently loaded scoring class.
    write_tsv
        Write results to tsv.
    write_table_tsv
        Write a specific table to tsv.
    get_table
        Returns the table located a specific key from the current store.
    check_store
        Checks the current store for the existence of a table with some key.
    map_table
        Maps a table by applying a callback function to a new table.
    combined_index
        Return an index containing all elements in a list of tables.
    get_root
        Get the root object owning this instance.
        
        
    See Also
    --------
    :py:class:`~enrich2.seqlib.seqlib.SeqLib`
    :py:class:`~enrich2.selection.selection.Selection`
    :py:class:`~enrich2.experiment.experiment.Experiment`
    """

    store_suffix = None
    has_store = True
    treeview_class_name = None

    def __init__(self):
        # general data members
        self._name = None
        self.name = "Unnamed" + self.__class__.__name__
        self.parent = None
        self._labels = list()

        # metadata members
        self.username = getpass.getuser()
        self.creationtime = time.asctime()

        # HDF5 data
        self.store_cfg = None
        self.store_path = None
        self.store = None
        self.chunksize = 100000

        # output locations
        self._output_dir = None
        self._output_dir_override = None
        self._tsv_dir = None

        # analysis parameters
        self._scoring_method = None
        self.scorer_class = None
        self.scorer_class_attrs = None
        self.scorer_path = None
        self._force_recalculate = None
        self._component_outliers = None
        self._tsv_requested = None
        self._ignore_metadata = None
        self.override_filter_stats = True

        # GUI variables
        self.treeview_id = None
        self.treeview_info = None

    # -----------------------------------------------------------------------#
    #                           Properties
    # -----------------------------------------------------------------------#
    @property
    def labels(self):
        """
        Property for returning labels shared by all children.

        If the object has no children (such as a SeqLib), the object's _labels
        are returned.
        """
        if self.children is None:
            return self._labels
        else:
            if len(self.children) > 0:
                return self.child_labels()
            else:
                return self._labels

    @property
    def force_recalculate(self):
        """
        This property should only be set for the root element. All other
        elements in the analysis should have ``None``.

        Recursively traverses up the config tree to find the root element.
        """
        if self._force_recalculate is None:
            if self.parent is not None:
                return self.parent.force_recalculate
            else:
                raise ValueError(
                    "Forced recalculation option not specified "
                    "at root [{}]".format(self.name)
                )
        else:
            return self._force_recalculate

    @force_recalculate.setter
    def force_recalculate(self, value):
        """
        Make sure the *value* is valid and set it.
        """
        if value in (True, False):
            self._force_recalculate = value
        else:
            raise ValueError(
                "Invalid setting '{}' for force_recalculate "
                "[{}]".format(value, self.name)
            )

    @property
    def component_outliers(self):
        """
        This property should only be set for the root element. All other
        elements in the analysis should have ``None``.

        Recursively traverses up the config tree to find the root element.
        """
        if self._component_outliers is None:
            if self.parent is not None:
                return self.parent.component_outliers
            else:
                raise ValueError(
                    "Calculate component outliers option not "
                    "specified at root [{}]".format(self.name)
                )
        else:
            return self._component_outliers

    @component_outliers.setter
    def component_outliers(self, value):
        """
        Make sure the *value* is valid and set it.
        """
        if value in (True, False):
            self._component_outliers = value
        else:
            raise ValueError(
                "Invalid setting '{}' for component_outliers "
                "[{}]".format(value, self.name)
            )

    @property
    def tsv_requested(self):
        """
        This property should only be set for the root element. All other
        elements in the analysis should have ``None``.

        Recursively traverses up the config tree to find the root element.
        """
        if self._tsv_requested is None:
            if self.parent is not None:
                return self.parent.tsv_requested
            else:
                raise ValueError(
                    "Write tsv option not specified at root " "[{}]".format(self.name)
                )
        else:
            return self._tsv_requested

    @tsv_requested.setter
    def tsv_requested(self, value):
        """
        Make sure the *value* is valid and set it.
        """
        if value in (True, False):
            self._tsv_requested = value
        else:
            raise ValueError(
                "Invalid setting '{}' for tsv_requested "
                "[{}]".format(value, self.name)
            )

    @property
    def scoring_method(self):
        """
        This property should only be set for the root element. All other
        elements in the analysis should have ``None``.

        Recursively traverses up the config tree to find the root element.
        """
        if self.scorer_class is None:
            if self.parent is not None:
                return self.parent.scorer_class.name
            else:
                raise ValueError(
                    "Scoring method not specified at root " "[{}]".format(self.name)
                )
        else:
            return self.parent.scorer_class.name

    @property
    def output_dir(self):
        """
        Elements that have ``None`` as their output directory value (*i.e.*
        no value set in the confic object) will automatically use the output
        directory from the parent.
        """
        if self._output_dir is None:
            if self.parent is not None:
                return self.parent.output_dir
            else:
                raise ValueError(
                    "No output directory specified at top level "
                    "[{}]".format(self.name)
                )
        else:
            return self._output_dir

    @output_dir.setter
    def output_dir(self, dirname):
        """
        Sets the object's base output directory to *dirname* and creates the
        directory if it doesn't exist.
        """
        try:
            dirname = os.path.expanduser(dirname)  # handle leading '~'
        except AttributeError as e:
            raise AttributeError("Invalid input for output directory: " "{}".format(e))
        try:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        except OSError as e:
            raise OSError("Failed to create output directory: {}".format(e))
        self._output_dir = dirname

    @property
    def output_dir_override(self):
        """
        This property should only be set for the root element. All other
        elements in the analysis should have ``None``.

        Recursively traverses up the config tree to find the root element.
        """
        if self._output_dir_override is None:
            if self.parent is not None:
                return self.parent.output_dir_override
            else:
                raise ValueError(
                    "Output directory override not specified at "
                    "root [{}]".format(self.name)
                )
        else:
            return self._output_dir_override

    @output_dir_override.setter
    def output_dir_override(self, value):
        """
        Make sure the *value* is valid and set it.
        """
        if value in (True, False):
            self._output_dir_override = value
        else:
            raise ValueError(
                "Invalid setting '{}' for output_dir_override "
                "[{}]".format(value, self.name)
            )

    @property
    def tsv_dir(self):
        """
        Creates the tsv directory when first requested if it doesn't exist.

        The plot directory is ``<output directory>/tsv/<object name>/``.
        """
        if self._tsv_dir is None:
            dirname = os.path.join(
                self.output_dir,
                "tsv",
                "{}_{}".format(fix_filename(self.name), self.store_suffix),
            )
            try:
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
            except OSError as e:
                raise OSError("Failed to create tsv directory: {}".format(e))
            self._tsv_dir = dirname
        return self._tsv_dir

    @property
    def children(self):
        """
        Property for returning all children of this element.

        Calls the objects :py:meth:`_children` method. This allows the
        property to be overloaded without creating a new property in the
        derived classes.
        """
        return self._children()

    # -----------------------------------------------------------------------#
    #                       Tree Structure Methods
    # -----------------------------------------------------------------------#
    def child_labels(self):
        """
        Returns a list of labels shared by every child.

        Returns
        -------
        list
            list of labels shared by every child.
        """
        shared = list()
        for x in self.children:
            shared.extend(x.labels)
        shared = collections.Counter(shared)
        shared = [x for x in shared.keys() if shared[x] == len(self.children)]
        return sorted(shared, key=lambda a: ELEMENT_LABELS.index(a))

    def _children(self):
        """
        Pure virtual method for returning children.
        """
        raise NotImplementedError("must be implemented by subclass")

    def remove_child_id(self, tree_id):
        """
        Pure virtual method for removing a child with Treeview id *tree_id*
        from this element's children.
        """
        raise NotImplementedError("must be implemented by subclass")

    def add_child(self, child):
        """
        Pure virtual method for adding a child.
        """
        raise NotImplementedError("must be implemented by subclass")

    def child_names(self):
        """
        Return a list of the ``name`` attributes for all children.
        
        Returns
        -------
        list
            List of children names
        """
        try:
            names = [x.name for x in self.children]
        except AttributeError:
            raise AttributeError("No name set for child [{}]".format(self.name))
        else:
            return names

    def get_root(self):
        """
        Returns the root owner of this object, other self if this object
        has no parents.

        Returns
        -------
        :py:class:`StoreManager`
        """
        if self.parent is not None:
            return self.parent.get_root()
        else:
            return self

    # -----------------------------------------------------------------------#
    #                       Class Configuration
    # -----------------------------------------------------------------------#
    def configure(self, cfg):
        """
        Set up the object using the config object *cfg*, usually derived from
        a ``.json`` file.
        
        Parameters
        ----------
        cfg : :class:`enrich2.config.types.StoreConfiguration` or `dict`
            Either a configuration object or a dictionary to initialise
            a configuration object.
                         
        Raises
        ------
        raises TypeError if ``cfg`` is not a :py:class:`dict` or
            :py:class:`enrich2.config.types.StoreConfiguration`
        """
        from ..config.types import StoreConfiguration

        if isinstance(cfg, dict):
            has_scorer = bool(cfg.get(SCORER, {}).get(SCORER_PATH, ""))
            cfg = StoreConfiguration(cfg, has_scorer=has_scorer)
        elif not isinstance(cfg, StoreConfiguration):
            raise TypeError("`cfg` was neither a StoreConfiguration or dict.")

        self.name = cfg.name
        if cfg.has_output_dir and self.output_dir_override:
            log_message(
                logging_callback=logging.warning,
                msg="Using command line supplied output "
                "directory instead of config file output "
                "directory",
                extra={"oname": self.name},
            )
        elif cfg.has_output_dir and not self.output_dir_override:
            self.output_dir = cfg.output_dir

        if cfg.has_store_path:
            self.store_cfg = True
            self.store_path = cfg.store_path
            log_message(
                logging_callback=logging.info,
                msg='Using specified HDF5 data store "{}"'.format(self.store_path),
                extra={"oname": self.name},
            )
        else:
            self.store_cfg = False
            self.store_path = None

        if cfg.has_scorer:
            self.scorer_path = cfg.scorer_cfg.scorer_path
            self.scorer_class = cfg.scorer_cfg.scorer_class
            self.scorer_class_attrs = cfg.scorer_cfg.get_options(False)

            print_cfg = cfg.scorer_cfg.get_options(keep_defaults=True)
            if print_cfg:
                msg = "Scorer parameters "
                msg += nested_format(print_cfg, False, tab_level=0)
            else:
                msg = "No options for scorer detected."

            log_message(
                logging_callback=logging.info,
                msg="Scorer detected.",
                extra={"oname": self.name},
            )
            log_message(
                logging_callback=logging.info, msg=msg, extra={"oname": self.name}
            )

    def serialize(self):
        """
        Format this object as a config object suitable for
        dumping to a config file.

        Returns
        -------
        `dict`
            Attributes of this instance and that of inherited classes
            in a dictionary.
        """
        cfg = {"name": self.name}
        if self.store_cfg:
            cfg["store"] = self.store_path
        if self.output_dir is not None:
            if self.parent is not None:
                if self.output_dir != self.parent.output_dir:
                    cfg["output directory"] = self.output_dir
            else:
                cfg["output directory"] = self.output_dir
        return cfg

    def validate(self):
        """
        Pure virtual method for making sure configured object is valid.
        """
        raise NotImplementedError("must be implemented by subclass")

    # -----------------------------------------------------------------------#
    #                           Store I/O
    # -----------------------------------------------------------------------#
    def store_open(self, children=False, force_delete=False):
        """
        Open the HDF5 file associated with this object. If the
        ``force_recalculate`` option is selected and ``force_delete`` is
        ``True``, the existing tables under ``'/main'`` will be deleted upon
        opening.

        This method needs a lot more error checking.
        
        Parameters
        ----------
        children : `bool`
            Open the stores of all children objects
            
        force_delete : `bool`
            Delete existing tables under ``'/main'`` upon store opening.
        """
        if children and self.children is not None:
            for child in self.children:
                child.store_open(children=True)

        clear = False
        if self.has_store:
            if self.store is not None and self.store.is_open():
                raise ValueError("Store is still open.")

            if not self.store_cfg:
                fname = fix_filename(self.name)
                self.store_path = os.path.join(
                    self.output_dir, "{}_{}.h5".format(fname, self.store_suffix)
                )
            log_message(
                logging_callback=logging.info,
                msg="Loading from store path '{}'.".format(self.store_path),
                extra={"oname": self.name},
            )
            if os.path.exists(self.store_path):
                store = HdfStore(self.store_path, mode="a")
                for key in store.keys():
                    clear |= not self.check_metadata(key, store)
                if clear:
                    msg = (
                        'Found existing HDF5 data store "{}", but '
                        "metadata did not match with this "
                        "instance.".format(self.store_path)
                    )
                    log_message(
                        logging_callback=logging.info,
                        msg=msg,
                        extra={"oname": self.name},
                    )
                    if not store.is_empty():
                        try:
                            store.clear()
                        except ValueError:
                            raise IOError(
                                "Store '{}' currently has an open"
                                "file handle not owned by Enrich2. "
                                "Cannot overwrite existing "
                                "data.".format(self.store_path)
                            )
                else:
                    log_message(
                        logging_callback=logging.info,
                        msg='Found existing HDF5 data store "{}" with matching'
                        " metadata.".format(self.store_path),
                        extra={"oname": self.name},
                    )
                    self.override_filter_stats = False
                store.close()

            else:
                log_message(
                    logging_callback=logging.info,
                    msg='Creating new HDF5 data store "{}"'.format(self.store_path),
                    extra={"oname": self.name},
                )

            self.store = HdfStore(self.store_path, mode="a")

            if self.force_recalculate or force_delete:
                if "/main" in self.store:
                    log_message(
                        logging_callback=logging.info,
                        msg="Deleting existing calculated values",
                        extra={"oname": self.name},
                    )
                    self.store.remove("/main")
                else:
                    log_message(
                        logging_callback=logging.warning,
                        msg="No existing calculated values in file",
                        extra={"oname": self.name},
                    )

    def store_close(self, children=False):
        """
        Close the HDF5 file associated with this object, and children objects
        if ``children`` is set to ``True``

        This method needs a lot more error checking.

        Parameters
        ----------
        children : `bool`
            Close the stores of all children objects

        """
        # needs more error checking
        if children and self.children is not None:
            for child in self.children:
                child.store_close(children=True)

        if self.has_store and self.store is not None and self.store.is_open():
            # Set the metadata. Resets if it already exists, but that should
            # be fine since if it already exists, then it should match.
            for key in self.store.keys():
                self.set_metadata(key, self.metadata(), update=False)
            self.store.close()
            self.store = None

    def get_table(self, key):
        """
        Checks to see if a particular data frame in the HDF5 store already
        exists and returns it.

        Parameters
        ----------
        key : `str`
            Key for the requested data frame

        Returns
        -------
        :py:class:`~pandas.HDFStore` 
            True if the key exists in the HDF5 store, else False.
        """
        if not self.check_store(key):
            raise ValueError("Store {} does not exist [{}]".format(key, self.name))
        else:
            return self.store[key]

    def check_store(self, key):
        """
        Checks to see if a particular data frame in the HDF5 store already
        exists.

        Parameters
        ----------
        key : `str`
            Key for the requested data frame

        Returns
        -------
        `bool` 
            True if the key exists in the HDF5 store, else False.
        """
        if key in list(self.store.keys()):
            log_message(
                logging_callback=logging.info,
                msg="Found existing '{}'".format(key),
                extra={"oname": self.name},
            )
            return True
        else:
            return False

    def map_table(
        self,
        source,
        destination,
        source_query=None,
        row_callback=None,
        row_callback_args=None,
        destination_data_columns=None,
    ):
        """
        Converts source table into destination table.
        This method really needs a better name.

        Parameters
        ----------
        source : `str`
            The key to access the table to map
        destination : `str`:
            The key to put the newly mapped table
        source_query : `str`
            A query string used as a predicate during mapping
        row_callback : `Callable`
            Callback function applied to each row.
        row_callback_args : `Iterable`
            Arguments required by *row_callback*
        destination_data_columns : `Iterable`
            Iterable of column names
        """
        if destination in list(self.store.keys()):
            # remove the current destination table because we are using append
            # append takes the "min_itemsize" argument, and put doesn't
            log_message(
                logging_callback=logging.info,
                msg="Overwriting existing '{}'".format(destination),
                extra={"oname": self.name},
            )
            self.store.remove(destination)

        # turn the single table name into a list to use select_as_multiple
        if isinstance(source, str):
            source = [source]

        # assumes the source tables all have the same index
        # find the min_itemsize
        max_index_length = self.store.get_column(source[0], "index").map(len).max()

        selections = self.store.select_as_multiple(
            keys=source, where=source_query, selector=source[0], chunk=True
        )
        for df in selections:
            if row_callback is not None:
                df = df.apply(row_callback, args=row_callback_args, axis="columns")
            if destination not in self.store:
                if destination_data_columns is None:
                    # if not specified, index all columns
                    destination_data_columns = list(df.columns)
                self.store.append(
                    destination,
                    df,
                    min_itemsize={"index": max_index_length},
                    data_columns=destination_data_columns,
                )
            else:
                self.store.append(destination, df)

    def combined_index(self, tables):
        """
        Return an index containing all elements in *tables*

        Parameters
        ----------
        tables : `Iterable`
            Iterable object containing :py:class:`~pd.HDFStore` objects.
        """
        shared = pd.Index()
        for t in tables:
            shared = shared.union(pd.Index(self.store.get_column(t, "index")))
        return shared

    # -----------------------------------------------------------------------#
    #                       Metadata/Computations
    # -----------------------------------------------------------------------#
    def add_label(self, x):
        """
        Add element label to this object.

        Parameters
        ----------
        x : `str`
            Label to add to labels, which must be present in ELEMENT_LABELS

        Raises
        ------
        raises ValueError if the label is not in {'barcodes', 'identifiers', 
            'variants', 'synonymous'}
        raises AttributeError if label is not a :py:class:`str`
        """
        labels = set(self._labels)
        if isinstance(x, str):
            if x in ELEMENT_LABELS:
                labels.update([x])
            else:
                raise ValueError("Invalid element label '{}' [{}]".format(x, self.name))
        else:
            raise AttributeError("Failed to add labels [{}]".format(self.name))
        # sort based on specified order
        self._labels = sorted(labels, key=lambda a: ELEMENT_LABELS.index(a))

    def metadata(self):
        """
        Creates the metadata `dict` which contains the configuration
        for this store, along with creation time and creation user.
        
        Returns
        -------
        `dict`
            Metadata dictionary.
        """
        cfg = self.serialize()
        metadata = {"cfg": cfg, "time": self.creationtime, "user": self.username}
        return metadata

    def check_metadata(self, key, store=None):
        """
        Check if the metadata of this instance (serialized configuration) is
        equal to the metadata stored in the managed store.
        
        Parameters
        ----------
        key : `str`
            The key to the current table
        store : :py:class:`~HdfStore`
            The store object to check

        Returns
        -------
        `bool`
            ``True`` according to the `dict` equality object implementation.

        """
        if store is None:
            store = self.store

        this = self.metadata()
        other = self.get_metadata(key, store)
        this_cfg = this.get("cfg", {})
        if other is None:
            return False
        other_cfg = other.get("cfg", {})
        return this_cfg == other_cfg

    def get_metadata(self, key, store=None):
        """
        Retrieve the Enrich2 metadata dictionary from the HDF5 store.

        Returns the metadata dictionary for *key*. If no metadata has been set
        for *key*, returns ``None``.

        *store* can be an external open HDFStore (used when copying metadata
        from raw counts). If it is ``None``, use this object's store.
        
        Parameters
        ----------
        key : `str`
            The name of the group or node in the HDF5 data store.
        store : :py:class:`~HDFStore`, optional, default None
            Can be an external open HDFStore (used when copying metadata
            from raw counts). If it is ``None``, use this object's store.
        
        Returns
        -------
        `dict`
            The metadata held by the given store or None if *key* in 
            store does not exist.
        
        Raises
        ------
        raises AttributeError if there no store is passed and this object's 
            store is also ``None``.
        """
        if store is None and self.store is None:
            raise AttributeError("Store has not yet been configured.")

        if store is None:
            store = self.store
        return store.get_metadata(key)

    def set_metadata(self, key, d, update=True):
        """
        Replace or update the metadata dictionary from the HDF5 store.
       
        Parameters
        ----------
        key : `str`
            The name of the group or node in the HDF5 data store.
        d : `dict`
            The dictionary containing the new metadata.
        update : `bool`, default: True
            If *update* is ``False``, *d* completely replaces the existing 
            metadata for *key*. Otherwise, *d* updates the existing 
            metadata using standard dictionary update
        """
        self.store.set_metadata(key, d, update)

    def calculate(self):
        """
        Pure virtual method that defines how the data are calculated.
        """
        raise NotImplementedError("must be implemented by subclass")

    # -----------------------------------------------------------------------#
    #                              File I/O
    # -----------------------------------------------------------------------#
    def write_tsv(self, subdirectory=None, keys=None):
        """
        Pure virtual method for writing tsv files.
        """
        raise NotImplementedError("must be implemented by subclass")

    def write_table_tsv(self, key):
        """
        Write the table under *key* as a tsv file.

        Files are written to a ``tsv`` directory in the default output
        location.

        File names are the HDF5 key with ``'_'`` substituted for ``'/'``.
        
        Parameters
        ----------
        key : str
            *key* in this object's store to write as a tsv file.        
        """
        fname = key.strip("/")  # remove leading slash
        fname = fname.replace("/", "_") + ".tsv"
        self.store[key].to_csv(
            os.path.join(str(self.tsv_dir), fname), sep="\t", na_rep="NA"
        )
