"""
Enrich2 libraries barcodevariant module
=======================================

Contains the concrete class ``BcvSeqLib`` which represents a sequencing
library containing variants which are also barcode sequences.
"""


import logging
import pandas as pd

from ..base.utils import compute_md5, log_message
from ..libraries.barcodemap import BarcodeMap
from .barcode import BarcodeSeqLib
from .variant import VariantSeqLib


__all__ = ["BcvSeqLib"]


class BcvSeqLib(VariantSeqLib, BarcodeSeqLib):
    """
    Class for counting variant data from barcoded sequencing libraries. 
    Creating a :py:class:`~enrich2.libraries.barcodevariant.BcvSeqLib` requires
    a valid *config* object with an ``'barcodes'`` entry and information 
    about the wild type sequence.

    The ``barcode_map`` keyword argument can be used to pass an existing 
    :py:class:`~enrich2.libraries.barcodemap.BarcodeMap`. Ensuring this is the 
    right BarcodeMap is the responsibility of the caller.
    
    Class Attributes
    ----------------
    treeview_class_name :  `str`
        String used to render object in the GUI.
    
    Attributes
    ----------
    barcode_map : :py:class:`~enrich2.libraries.barcodemap.BarcodeMap`
        Barcode map associated with the library.
    
    Methods
    -------
    configure
        Configures the object from an dictionary loaded from a configuration 
        file.
    serialize
        Returns a `dict` with all configurable attributes stored that can
        be used to reconfigure a new instance.
    calculate
        Counts the barcodes and combines them into variant counts using a
        :py:class:`~enrich2.libraries.barcodemap.BarcodeMap` object.
    
    See Also
    --------
    :py:class:`~enrich2.libraries.variant.VariantSeqLib`
    :py:class:`~enrich2.libraries.barcode.BarcodeSeqLib`
    """

    treeview_class_name = "Barcoded Variant SeqLib"

    def __init__(self):
        VariantSeqLib.__init__(self)
        BarcodeSeqLib.__init__(self)
        self.barcode_map = None

    def configure(self, cfg, barcode_map=None):
        """
        Set up the object using the config object *cfg*, usually derived from
        a ``.json`` file.

        Parameters
        ----------
        cfg : `dict` or :py:class:`~enrich2.config.types.BcvSeqLibConfiguration`
            The object to configure this instance with.
        barcode_map : :py:class:`~enrich2.libraries.barcodemap.BarcodeMap`
            An existing barcode map associated with the library.
        """
        from ..config.types import BcvSeqLibConfiguration

        if isinstance(cfg, dict):
            init_fastq = bool(cfg.get("fastq", {}).get("reads", ""))
            cfg = BcvSeqLibConfiguration(cfg, init_fastq)
        elif not isinstance(cfg, BcvSeqLibConfiguration):
            raise TypeError("`cfg` was neither a " "BcvSeqLibConfiguration or dict.")

        VariantSeqLib.configure(self, cfg)
        BarcodeSeqLib.configure(self, cfg)
        if barcode_map is not None:
            if barcode_map.filename == cfg.barcodes_cfg.map_file:
                self.barcode_map = barcode_map
            else:
                raise ValueError(
                    "Attempted to assign non-matching "
                    "barcode map [{}]".format(self.name)
                )
        else:
            self.barcode_map = BarcodeMap(cfg.barcodes_cfg.map_file, is_variant=True)

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
        cfg = VariantSeqLib.serialize(self)
        cfg.update(BarcodeSeqLib.serialize(self))

        # required for creating new objects in GUI
        if self.barcode_map is not None:
            cfg["barcodes"]["map file"] = self.barcode_map.filename
            cfg["barcodes"]["map file md5"] = compute_md5(self.barcode_map.filename)
        return cfg

    def calculate(self):
        """
        Counts the barcodes using :py:meth:`BarcodeSeqLib.count`
        and combines them into variant counts using the 
        :py:class:`~enrich2.libraries.barcodemap.BarcodeMap`
        """
        if not self.check_store("/main/variants/counts"):
            BarcodeSeqLib.calculate(self)  # count the barcodes
            df_dict = dict()
            barcode_variants = dict()

            log_message(
                logging_callback=logging.info,
                msg="Converting barcodes to variants",
                extra={"oname": self.name},
            )

            # store mapped barcodes
            self.save_filtered_counts(
                label="barcodes",
                query="index in {} & count >= {}".format(
                    list(self.barcode_map.keys()), self.barcode_min_count
                ),
            )

            # count variants associated with the barcodes
            max_mut_barcodes = 0
            max_mut_variants = 0
            for bc, count in self.store["/main/barcodes/counts"].iterrows():
                count = count["count"]
                variant = self.barcode_map[bc]
                mutations = self.count_variant(variant)
                if mutations is None:  # variant has too many mutations
                    max_mut_barcodes += 1
                    max_mut_variants += count
                    if self.report_filtered:
                        self.report_filtered_variant(variant, count)
                else:
                    try:
                        df_dict[mutations] += count
                    except KeyError:
                        df_dict[mutations] = count
                    barcode_variants[bc] = mutations

            # save counts, filtering based on the min count
            counts = {k: v for k, v in df_dict.items() if v >= self.variant_min_count}
            self.save_counts("variants", counts, raw=False)
            del df_dict

            # write the active subset of the BarcodeMap to the store
            barcodes = list(barcode_variants.keys())
            data = {"value": [barcode_variants[bc] for bc in barcodes]}
            barcode_variants = pd.DataFrame(data, index=barcodes)
            del barcodes

            barcode_variants.sort_values("value", inplace=True)
            self.store.put(
                key="/raw/barcodemap",
                value=barcode_variants,
                data_columns=barcode_variants.columns,
            )
            del barcode_variants

            if self.aligner is not None:
                log_message(
                    logging_callback=logging.info,
                    msg="Aligned {} variants".format(self.aligner.calls),
                    extra={"oname": self.name},
                )
                self.aligner_cache = None

            # self.report_filter_stats()
            log_message(
                logging_callback=logging.info,
                msg="Removed {} unique barcodes ({} total variants) with "
                "excess mutations".format(max_mut_barcodes, max_mut_variants),
                extra={"oname": self.name},
            )
            self.save_filter_stats()

        self.count_synonymous()
