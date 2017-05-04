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


import logging
import pandas as pd

from ..libraries.barcodemap import BarcodeMap
from .barcode import BarcodeSeqLib


class BcidSeqLib(BarcodeSeqLib):
    """
    Class for counting data from barcoded sequencing libraries with non-variant
    identifiers. 
    Creating a :py:class:`BcidSeqLib` requires a valid *config* 
    object with an ``'barcodes'`` entry and information.

    The ``barcode_map`` keyword argument can be used to pass an existing 
    :py:class:`~seqlib.barcodemap.BarcodeMap`. Ensuring this is the 
    right :py:class:`~seqlib.barcodemap.BarcodeMap` is the responsibility 
    of the caller.
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
        """
        BarcodeSeqLib.configure(self, cfg)
        try:
            if 'min count' in cfg['identifiers']:
                self.identifier_min_count = int(
                    cfg['identifiers']['min count']
                )
            else:
                self.identifier_min_count = 0

            if barcode_map is not None:
                if barcode_map.filename == cfg['barcodes']['map file']:
                    self.barcode_map = barcode_map
                else:
                    raise ValueError("Attempted to assign "
                                     "non-matching "
                                     "barcode map [{}]".format(self.name))
            else:
                self.barcode_map = BarcodeMap(
                    mapfile=cfg['barcodes']['map file'],
                    is_variant=False
                )
        except KeyError as key:
            raise KeyError("Configuration Error: Missing "
                           "required config value "
                           "{key} [{name}]".format(key=key, name=self.name))

    def serialize(self):
        """
        Format this object (and its children) as a config
        object suitable for dumping to a config file.
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
        them into identifier counts using the :py:class:`BarcodeMap`.
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
