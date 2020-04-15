"""
Enrich2 libraries barcodemap module
===================================

Contains the BarcodeMap class which subclasses `dict` to provide a basic
way to map barcodes to variants.
"""


import re
import bz2
import gzip
import os.path


__all__ = ["re_barcode", "re_variant_dna", "re_identifier", "BarcodeMap"]


re_barcode = re.compile("^[ACGT]+$")
re_variant_dna = re.compile("^[ACGTN]+$")
re_identifier = re.compile("^.+$")


class BarcodeMap(dict):
    """
    Dictionary-derived class for storing the relationship between barcodes
    (keys) and variants (values). Requires the path to a *mapfile*, containing
    lines in the format ``'barcode<whitespace>variant'`` for each barcode
    expected in the library. This file can be plain text or compressed
    (``.bz2`` or ``.gz``).

    Barcodes must only contain the characters ``ACGT`` and variants must only
    contain the characters ``ACGTN`` (lowercase characters are converted to
    uppercase).

    Blank lines and lines that begin with ``#`` (comments) are ignored.

    *is_variant* is a boolean that is ``True`` if the barcodes are assigned to
    variant DNA sequences, or ``False`` if the barcodes are assigned to
    arbitrary identifiers. If this is ``True``, additional error checking
    is performed on the variant DNA sequences.
    
    Attributes
    ----------
    name : `str`
        Name of the object, which includes the base of `filename`.
    filename : `str`
        File path pointing to the map file to load.
    is_variant : `bool`, Default ``False``
        Boolean that is ``True`` if the barcodes are assigned to
        variant DNA sequences, or ``False`` if the barcodes are assigned to
        arbitrary identifiers
    """

    def __init__(self, mapfile, is_variant=False):
        super(BarcodeMap, self).__init__()
        self.name = "barcodemap_{}".format(os.path.basename(mapfile))
        self.filename = mapfile
        self.is_variant = is_variant

        # open the file
        try:
            ext = os.path.splitext(mapfile)[-1].lower()
            if ext in (".bz2"):
                handle = bz2.open(mapfile, "rt")
            elif ext in (".gz"):
                handle = gzip.open(mapfile, "rt")
            else:
                handle = open(mapfile, "rt")
        except IOError:
            raise IOError(
                "Could not open barcode map file '{}' [{}]".format(mapfile, self.name)
            )

        # handle each line
        for line in handle:
            # skip comments and whitespace-only lines
            if len(line.strip()) == 0 or line[0] == "#":
                continue

            try:
                barcode, value = line.strip().split()
            except ValueError:
                raise ValueError(
                    "Unexpected barcode map line format " "[{}]".format(self.name)
                )

            if len(value) == 0 or len(barcode) == 0:
                raise ValueError(
                    "Missing either the barcode or map value." " [{}]".format(self.name)
                )

            barcode = barcode.upper()
            if not re_barcode.match(barcode):
                raise ValueError(
                    "Barcode DNA sequence contains unexpected "
                    "characters [{}]".format(self.name)
                )
            if self.is_variant:
                value = value.upper()
                if not re_variant_dna.match(value):
                    raise ValueError(
                        "Variant DNA sequence contains unexpected"
                        " characters [{}]".format(self.name)
                    )
            else:
                if not re_identifier.match(value):
                    raise ValueError(
                        "Identifier contains unexpected "
                        "characters [{}]".format(self.name)
                    )

            if barcode in self:
                if self[barcode] != value:
                    raise ValueError(
                        "Barcode '{}' assigned to multiple "
                        "unique values".format(barcode, self.name)
                    )
            else:
                self[barcode] = value

        handle.close()
