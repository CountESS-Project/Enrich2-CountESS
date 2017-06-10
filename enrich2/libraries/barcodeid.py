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
#  along with Enrich2.  If not, see <http://www.gnu.org/licenses/>.


"""
Enrich2 libraries barcodeid module
==================================

Contains the concrete class ``BcidSeqLib`` which represents a barcoded 
sequencing library with non-variant identifiers. 
"""


import logging
import pandas as pd

from ..libraries.barcodemap import BarcodeMap
from .barcode import BarcodeSeqLib


__all__ = [
    "BcidSeqLib"
]


class BcidSeqLib(BarcodeSeqLib):
    """
    Class for counting data from barcoded sequencing libraries with non-variant
    identifiers. 
    
    Creating a :py:class:`BcidSeqLib` requires a valid *config* 
    object with an ``'barcodes'`` entry and information.

    The ``barcode_map`` keyword argument can be used to pass an existing 
    :py:class:`~enrich2.libraries.barcodemap.BarcodeMap`. Ensuring this is the 
    right :py:class:`~enrich2.libraries.barcodemap.BarcodeMap` is 
    the responsibility of the caller.
    
    Class Attributes
    ----------------
    treeview_class_name :  `str`
        String used to render object in the GUI.
    
    Attributes
    ----------
    barcode_map : :py:class:`~enrich2.libraries.barcodemap.BarcodeMap`
        Barcode map associated with the library.
    identifier_min_count : `int`
        Minimum count an Id must have to pass the filtering phase.
    
    Methods
    -------
    configure
        Configures the object from an dictionary loaded from a configuration 
        file.
    serialize
        Returns a `dict` with all configurable attributes stored that can
        be used to reconfigure a new instance.
    calculate
        Counts barcodes and combines them into identifier counts using a
        :py:class:`~enrich2.libraries.barcodemap.BarcodeMap` object.
    
    See Also
    --------
    :py:class:`~enrich2.libraries.barcode.BarcodeSeqLib`
    """

    treeview_class_name = "Barcoded ID SeqLib"
    
    def __init__(self):
        BarcodeSeqLib.__init__(self)
        self.barcode_map = None
        self.identifier_min_count = 0
        self.add_label('identifiers')

    def configure(self, cfg, barcode_map=None):
        """
        Set up the object using the config object *cfg*, usually derived from
        a ``.json`` file.

        Parameters
        ----------
        cfg : `dict` or :py:class:`~enrich2.config.types.BcidSeqLibConfiguration`
            The object to configure this instance with.
        barcode_map : :py:class:`~enrich2.libraries.barcodemap.BarcodeMap`
            An existing barcode map associated with the library.
        """
        from ..config.types import BcidSeqLibConfiguration

        if isinstance(cfg, dict):
            init_fastq = bool(cfg.get('fastq', {}).get("reads", ""))
            cfg = BcidSeqLibConfiguration(cfg, init_fastq)
        elif not isinstance(cfg, BcidSeqLibConfiguration):
            raise TypeError("`cfg` was neither a "
                            "BcidSeqLibConfiguration or dict.")

        BarcodeSeqLib.configure(self, cfg)
        self.identifier_min_count = cfg.identifers_cfg.min_count

        if barcode_map is not None:
            if barcode_map.filename == cfg.barcodes_cfg.map_file:
                self.barcode_map = barcode_map
            else:
                raise ValueError("Attempted to assign "
                                 "non-matching "
                                 "barcode map [{}]".format(self.name))
        else:
            self.barcode_map = BarcodeMap(
                mapfile=cfg.barcodes_cfg.map_file,
                is_variant=False
            )

    def serialize(self):
        """
        Format this object (and its children) as a config object suitable for
        dumping to a config file.

        Returns
        -------
        `dict`
            Attributes of this instance and that of inherited classes
            in a dictionary.
        """
        cfg = BarcodeSeqLib.serialize(self)

        cfg['identifiers'] = dict()
        if self.identifier_min_count > 0:
            cfg['identifiers']['min count'] = self.identifier_min_count

        # required for creating new objects in GUI
        if self.barcode_map is not None:
            cfg['barcodes']['map file'] = self.barcode_map.filename

        return cfg

    def calculate(self):
        """
        Counts the barcodes using :py:meth:`BarcodeSeqLib.count` and combines
        them into identifier counts using the 
        :py:class:`~enrich2.libraries.barcodemap.BarcodeMap`
        """
        if not self.check_store("/main/identifiers/counts"):
            BarcodeSeqLib.calculate(self) # count the barcodes
            df_dict = dict()
            barcode_identifiers = dict()

            logging.info(
                msg="Converting barcodes to identifiers",
                extra={'oname' : self.name}
            )
            # store mapped barcodes
            self.save_filtered_counts(
                label="barcodes",
                query="index in self.barcode_map.keys() & "
                      "count >= self.barcode_min_count"
            )

            # count identifiers associated with the barcodes
            for bc, count in self.store['/main/barcodes/counts'].iterrows():
                count = count['count']
                identifier = self.barcode_map[bc]
                try:
                    df_dict[identifier] += count
                except KeyError:
                    df_dict[identifier] = count
                barcode_identifiers[bc] = identifier

            # save counts, filtering based on the min count
            min_counts = {
                k: v for k, v in df_dict.items()
                if v >= self.identifier_min_count
            }
            self.save_counts('identifiers', min_counts, raw=False)
            del df_dict

            # write the active subset of the BarcodeMap to the store
            barcodes = list(barcode_identifiers.keys())
            data = {'value' : [barcode_identifiers[bc] for bc in barcodes]}
            barcode_identifiers = pd.DataFrame(data, index=barcodes)
            del barcodes
            barcode_identifiers.sort_values('value', inplace=True)
            self.store.put(
                "/raw/barcodemap",
                barcode_identifiers,
                data_columns=barcode_identifiers.columns,
                format="table"
            )
            del barcode_identifiers
            #self.report_filter_stats()
            self.save_filter_stats()
