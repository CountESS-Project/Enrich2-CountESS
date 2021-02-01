#  Copyright 2016-2017 Alan F Rubin, Daniel Esposito
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
Enrich2 configuration constants module
======================================

This module contains all the constants used as keys in configuration files.
"""


NAME = "name"
CONDITIONS = "conditions"
LIBRARIES = "libraries"
SELECTIONS = "selections"
TIMEPOINT = "timepoint"
OUTPUT_DIR = "output directory"
REPORT_FILTERED_READS = "report filtered reads"
STORE = "store"
OVERLAP = "overlap"

FASTQ = "fastq"
READS = "reads"
REVERSE = "reverse"
FILTERS = "filters"
FILTERS_MAX_N = "max N"
FILTERS_MIN_COUNT = "min count"
FILTERS_AVG_Q = "avg quality"
FILTERS_MIN_Q = "min quality"
FILTERS_CHASTITY = "chastity"
TRIM_START = "start"
TRIM_LENGTH = "length"
SCORER = "scorer"
SCORER_PATH = "scorer path"
SCORER_OPTIONS = "scorer options"


COUNTS_FILE = "counts file"
IDENTIFIERS = "identifiers"
IDENTIFIERS_MIN_COUNT = "min count"

VARIANTS = "variants"
VARIANTS_MIN_COUNT = "min count"
VARIANTS_MAX_MUTATIONS = "max mutations"
USE_ALIGNER = "use aligner"
WILDTYPE = "wild type"
CODING = "coding"
REF_OFFSET = "reference offset"
SEQUENCE = "sequence"

BARCODES = "barcodes"
BARCODE_MAP_FILE = "map file"
BARCODE_MIN_COUNT = "min count"

FORCE_RECALCULATE = "force_recalculate"
COMPONENT_OUTLIERS = "component_outliers"
TSV_REQUESTED = "tsv_requested"
OUTPUT_DIR_OVERRIDE = "output_dir_override"
