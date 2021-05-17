import logging
from hashlib import md5
from tkinter.messagebox import askyesno


from ..base.utils import log_message
from ..plugins import load_scorer_class_and_options


class Plugin(object):
    """
    Class representation of a plugin, containing the scorer 
    :py:class:`~enrich2.plugins.scoring.BaseScorerPlugin` object,
    :py:class:`~enrich2.plugins.options.Options` object, the 
    :py:class:`~enrich2.plugins.options.OptionsFile` object, the plugin path
    and the md5 hash of the parsed file.
    
    Contains utility functions for hashing a plugin (for use in the gui),
    checking plugin metadata, reloading a plugin, checking for file changes.
    
    Parameters
    ----------
    path : `str`
        The path the the python file to parse for a plugin.

    Attributes
    ----------
    klass : :py:class:`~enrich2.plugins.scoring.BaseScorerPlugin`
        Parsed scoring class from ``path``
    options : :py:class:`~enrich2.plugins.options.Options`
        Parsed options class from ``path``
    options_file : :py:class:`~enrich2.plugins.options.OptionsFile`
        Parsed options file class from ``path``
    path : `str`
        The path the the python file to parse for a plugin.
    md5_stamp : `str`
        The hexdigest of an MD5 checksum on ``path``.
    
    Methods
    -------
    metadata
        Returns a tuple of a scoring plugin's (name, version, author, path)
    md5_has_changed
        Returns a boolean indicating if a plugin's MD5 hash has changed.
    refresh
        Asks user wether to reload a plugin if MD5 changes have been detected.
    _reload
        Reloads the plugin from ``path`` and creates a new MD5 checksum.
    
    """

    def __init__(self, path):
        result = load_scorer_class_and_options(path)
        klass, options, options_file = result

        self.klass = klass
        self.options = options
        self.options_file = options_file
        self.path = path
        self.md5_stamp = md5(open(path, "rb").read()).hexdigest()

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return str(self.metadata())

    def __eq__(self, other):
        return hash(self) == hash(other) and self.md5_stamp == other.md5_stamp

    def metadata(self):
        """
        Returns a tuple of a scoring plugin's ``(name, version, author, path)``
        
        Returns
        -------
        `tuple`
            (name, version, author, path)
        """
        return self.klass.name, self.klass.version, self.klass.author, self.path

    def md5_has_changed(self):
        """
        Returns a boolean indicating if a plugin's MD5 hash has changed.
        
        Returns
        -------
        `bool`
            ``True`` if MD5 of file at ``path`` has changed.
        """
        new_plugin = Plugin(self.path)
        if (
            self.metadata() == new_plugin.metadata()
            and self.md5_stamp != new_plugin.md5_stamp
        ):
            log_message(
                logging_callback=logging.info,
                msg="Plugin at path {} has the same metadata but different "
                "file contents.".format(self.path),
                extra={"oname": self.__class__.__name__},
            )
            return True
        elif (
            self.metadata() != new_plugin.metadata()
            and self.md5_stamp != new_plugin.md5_stamp
        ):
            log_message(
                logging_callback=logging.info,
                msg="Plugin at path {} has does not match.".format(self.path),
                extra={"oname": self.__class__.__name__},
            )
            return True
        else:
            return False

    def refresh(self):
        """
        Asks user wether to reload a plugin if MD5 changes have been detected.
        
        Returns
        -------
        `bool`
            ``True`` if the plugin was reloaded from file.
        """
        yes = False
        if self.md5_has_changed():
            yes = askyesno(
                "Reload plugin?",
                "The plugin located at '{}' has been modified. Do "
                "you want to reload this plugin?".format(self.path),
            )
            if yes:
                self._reload()
        return yes

    def _reload(self):
        """
        Reloads a plugin from ``path``.
        """
        result = load_scorer_class_and_options(self.path)
        klass, options, options_file = result
        self.klass = klass
        self.options = options
        self.options_file = options_file
        self.md5_stamp = md5(open(self.path, "rb").read()).hexdigest()
        return self

    def has_options(self):
        return self.options is not None

    def has_options_files(self):
        return self.options_file is not None
