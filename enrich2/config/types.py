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

# -*- coding: utf-8 -*-

"""
This module contains classes representing the data model of an Enrich2
configuration file. Each class represents a `yaml`/`json` dictionary
and contains validation methods to format input from a GUI configurator.

Example
-------


Notes
-----


Attributes
----------


"""

import re
import os
import sys
from abc import ABC, abstractclassmethod
from .config_check import *


NAME = 'name'
CONDITIONS = 'conditions'
LIBRARIES = 'libraries'
SELECTIONS = 'selections'
TIMEPOINT = 'timepoint'
OUTPUT_DIR = 'output directory'
REPORT_FILTERED_READS = 'report filtered reads'
STORE = 'store'

FASTQ = 'fastq'
READS = 'reads'
REVERSE = 'reverse'
FILTERS = 'filters'
FILTERS_MAX_N = 'max N'
FILTERS_MIN_COUNT = 'min count'
FILTERS_AVG_Q = 'avg quality'
FILTERS_MIN_Q = 'min quality'
FILTERS_CHASTITY = 'chastity'

COUNTS_FILE = 'counts file'
IDENTIFIERS = 'identifiers'
IDENTIFIERS_MIN_COUNT = 'min count'

VARIANTS = 'variants'
VARIANTS_MIN_COUNT = 'min count'
VARIANTS_MAX_MUTATIONS = 'max mutations'
USE_ALIGNER = 'use aligner'
WILDTYPE = 'wild type'
CODING = 'coding'
REF_OFFSET = 'reference offset'
SEQUENCE = 'sequence'

BARCODES = 'barcodes'
BARCODE_MAP_FILE = 'map file'
BARCODE_MIN_COUNT = 'min count'


class Configuration(ABC):
    """
    Abtract class representing required operations on the data model.
    """

    def __rdict__(self):
        repr_dict = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Configuration):
                repr_dict[k] = v.__rdict__()
            else:
                repr_dict[k] = v
        return repr_dict

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str(self.__rdict__())

    @abstractclassmethod
    def validate(self):
        pass


# -------------------------------------------------------------------------- #
#
#                      Component Configuration Classes
#
# -------------------------------------------------------------------------- #
class FASTQConfiguration(Configuration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for fastq configuration.")

        if READS not in cfg:
            raise ValueError("Missing {} key from {} configuration.".format(
                READS, FASTQ
            ))

        filters_cfg = cfg.get(FILTERS, {})
        self.reads = cfg.get(READS, "")
        self.reverse = cfg.get(REVERSE, False)
        self.filters_cfg =  FiltersConfiguration(filters_cfg)
        self.validate()

    def validate(self):
        if not isinstance(self.reverse, bool):
            raise TypeError("Expected bool for reverse but found {}.".format(
                type(self.reverse)
            ))
        if not isinstance(self.reads, str):
            raise TypeError("Expected str for reads but found {}.".format(
                type(self.reads)
            ))
        if not os.path.isfile(self.reads):
            raise IOError("File {} does not exist."
                          " Try using absolute paths.".format(self.reads))

        _, tail = os.path.split(self.reads)
        _, ext = os.path.splitext(tail)
        if ext not in set(['.bz2', '.gz', '.fq', '.fastq']):
            raise ValueError("Unsupported format for reads. Files"
                             "need extension to be either bz2, gz, fq or"
                             "fastq.")
        self.filters_cfg.validate()
        return self


class FiltersConfiguration(Configuration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for filters configuration.")

        self.chaste = cfg.get(FILTERS_CHASTITY, False)
        self.max_n = cfg.get(FILTERS_MAX_N, sys.maxsize)
        self.avg_base_quality = cfg.get(FILTERS_AVG_Q, 0)
        self.min_base_quality = cfg.get(FILTERS_MIN_Q, 0)
        self.validate()

    def validate_max_n(self):
        if not isinstance(self.max_n, int):
            raise TypeError("FASTQ filter `max n` must be an integer."
                            " Found type {}.".format(type(self.max_n)))
        if self.max_n < 0:
            raise ValueError("FASTQ filter `max n` must not be negative.")

    def validate_chate(self):
        if not isinstance(self.chaste, bool):
            raise TypeError("FASTQ filter `chastity` must be a boolean."
                            " Found type {}.".format(type(self.max_n)))

    def validate_avg_base_quality(self):
        if not isinstance(self.avg_base_quality, int):
            raise TypeError("FASTQ filter `avg quality` must be an integer."
                            " Found type {}.".format(type(self.max_n)))
        if self.avg_base_quality < 0:
            raise ValueError("FASTQ filter "
                             "`avg quality` must not be negative.")

    def validate_min_base_quality(self):
        if not isinstance(self.min_base_quality, int):
            raise TypeError("FASTQ filter `min quality` must be an integer."
                            " Found type {}.".format(type(self.max_n)))
        if self.min_base_quality < 0:
            raise ValueError("FASTQ filter "
                             "`min quality` must not be negative.")

    def validate(self):
        self.validate_chate()
        self.validate_max_n()
        self.validate_avg_base_quality()
        self.validate_min_base_quality()
        return self


class BarcodeConfiguration(Configuration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for barcodes configuration.")

        self.min_count = cfg.get(BARCODE_MIN_COUNT, 0)
        self.map_file = cfg.get(BARCODE_MAP_FILE, "")
        self.validate()

    def validate_map_file(self):
        if not isinstance(self.map_file, str):
            raise TypeError("Expected str for map file but found {}.".format(
                type(self.map_file)
            ))
        if not os.path.isfile(self.map_file):
            raise IOError("File {} does not exist."
                          " Try using absolute paths.".format(self.map_file))

        _, tail = os.path.split(self.map_file)
        _, ext = os.path.splitext(tail)
        if ext not in set(['.bz2', '.gz', '.txt']):
            raise ValueError("Unsupported format for map file. Files"
                             "need extension to be either bz2, gz or txt.")

    def validate_min_count(self):
        if not isinstance(self.min_count, int):
            raise TypeError("Barcode `min count` must be an integer."
                            " Found type {}".format(type(self.min_count)))
        if self.min_count < 0:
            raise ValueError("Barcode `min count` must not be negative.")

    def validate(self):
        self.validate_min_count()
        self.validate_map_file()
        return self


class IdentifiersConfiguration(Configuration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for identifiers configuration.")
        self.min_count = cfg.get(IDENTIFIERS_MIN_COUNT, 0)
        self.validate()

    def validate_min_count(self):
        if not isinstance(self.min_count, int):
            raise TypeError("Identifers `min count` must be an integer."
                            " Found type {}".format(type(self.min_count)))
        if self.min_count < 0:
            raise ValueError("Identifers `min count` must not be negative.")

    def validate(self):
        self.validate_min_count()
        return self


class VariantsConfiguration(Configuration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for variants configuration.")

        if WILDTYPE not in cfg:
            raise ValueError("Missing {} key from {} configuration.".format(
                WILDTYPE, VARIANTS
            ))

        wildtype_cfg = cfg.get(WILDTYPE, {})
        self.use_aligner = cfg.get(USE_ALIGNER, False)
        self.max_mutations = cfg.get(VARIANTS_MAX_MUTATIONS, sys.maxsize)
        self.min_count = cfg.get(VARIANTS_MIN_COUNT, 0)
        self.wildtype_cfg = WildTypeConfiguration(wildtype_cfg)
        self.validate()

    def validate_use_aligner(self):
        if not isinstance(self.use_aligner, bool):
            raise TypeError("Variants `use aligner` must be a boolean."
                            " Found type {}.".format(type(self.use_aligner)))

    def validate_max_mutations(self):
        if not isinstance(self.max_mutations, int):
            raise TypeError("Variants `max mutations` must be an integer."
                            " Found type {}".format(type(self.min_count)))
        if self.max_mutations < 0:
            raise ValueError("Variants `max mutations` must not be negative.")

    def validate_min_count(self):
        if not isinstance(self.min_count, int):
            raise TypeError("Variants `min count` must be an integer."
                            " Found type {}".format(type(self.min_count)))
        if self.min_count < 0:
            raise ValueError("Variants `min count` must not be negative.")

    def validate(self):
        self.wildtype_cfg.validate()
        self.validate_max_mutations()
        self.validate_min_count()
        self.validate_use_aligner()
        return self


class WildTypeConfiguration(Configuration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for wildtype configuration.")

        self.coding = cfg.get(CODING, False)
        self.reference_offset = cfg.get(REF_OFFSET, 0)
        self.sequence = cfg.get(SEQUENCE, "")
        self.validate()

    def validate_coding(self):
        if not isinstance(self.coding, bool):
            raise TypeError("Wildtype `coding` must be a boolean."
                            " Found type {}.".format(type(self.coding)))

    def validate_reference_offset(self):
        if not isinstance(self.reference_offset, int):
            raise TypeError("Wildtype `reference offset` "
                            "must be an integer. Found type "
                            "{}.".format(type(self.reference_offset)))
        if self.reference_offset < 0:
            raise ValueError("Wildtype `reference offset` "
                             "must not be negative.")

        multple_of_three = self.reference_offset % 3 == 0
        if self.coding and not multple_of_three:
            raise ValueError("If `protein coding` is selected, "
                             "`reference offset` must be a multiple of 3.")

    def validate_sequence(self):
        if not isinstance(self.sequence, str):
            raise TypeError("Variants `min count` must be an integer. "
                            "Found type {}".format(type(self.sequence)))

        self.sequence = self.sequence.upper()
        atcg_chars_only = "^[ACGT]+$"
        if not re.match(atcg_chars_only, self.sequence):
            raise ValueError("`sequence` contains unexpected "
                             "characters {}".format(self.sequence))

        multple_of_three = len(self.sequence) % 3 == 0
        if self.coding and not multple_of_three:
            raise ValueError("If `protein coding` is selected "
                             "`sequence` must be a multiple of 3.")

    def validate(self):
        self.validate_coding()
        self.validate_sequence()
        self.validate_reference_offset()
        return self


# -------------------------------------------------------------------------- #
#
#                      Library Configuration Classes
#
# -------------------------------------------------------------------------- #
class BaseLibraryConfiguration(Configuration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for base library configuration.")

        if NAME not in cfg:
            raise ValueError("Missing {} from base library "
                             "configuration.".format(NAME))
        if TIMEPOINT not in cfg:
            raise ValueError("Missing {} from base library "
                             "configuration.".format(TIMEPOINT))
        if REPORT_FILTERED_READS not in cfg:
            raise ValueError("Missing {} from BarcodeSeqLib "
                             "configuration.".format(REPORT_FILTERED_READS))

        filters_cfg = cfg.get(FASTQ, {})

        self.seqlib_type = seqlib_type(cfg)
        if self.seqlib_type is None:
            raise ValueError("Unrecognized SeqLib config")

        self.name = cfg.get(NAME)
        self.timepoint = cfg.get(TIMEPOINT)
        self.report_filtered_reads = cfg.get(REPORT_FILTERED_READS, False)
        self.fastq_filters_cfg = FASTQConfiguration(filters_cfg).validate()
        self.validate()

    def validate_name(self):
        if not isinstance(self.name, str):
            raise TypeError("Library `name` must be a str."
                            " Found type {}.".format(type(self.name)))
        if not self.name:
            raise ValueError("Library `name` must not be empty.")

    def validate_timepoint(self):
        if not isinstance(self.timepoint, int):
            raise TypeError("Library `timepoint` must be an integer."
                            " Found type {}.".format(type(self.timepoint)))
        if self.timepoint < 0:
            raise ValueError("Library `timepoint` must not be negative.")

    def validate_report_filtered_reads(self):
        if not isinstance(self.report_filtered_reads, bool):
            raise TypeError("Expected bool for `report filtered reads`"
                            " but found {}.".format(
                type(self.report_filtered_reads)
            ))

    def validate(self):
        self.validate_name()
        self.validate_report_filtered_reads()
        self.validate_timepoint()
        return self


class BarcodeSeqLibConfiguration(BaseLibraryConfiguration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for BarcodeSeqLibConfiguration.")
        super(BarcodeSeqLibConfiguration, self).__init__(cfg)

        barcodes_cfg = cfg.get(BARCODES, {})
        self.barcodes_cfg = BarcodeConfiguration(barcodes_cfg).validate()
        self.validate()


class BcidSeqLibConfiguration(BaseLibraryConfiguration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for BcidSeqLibConfiguration.")
        super(BcidSeqLibConfiguration, self).__init__(cfg)

        barcodes_cfg = cfg.get(BARCODES, {})
        identifers_cfg = cfg.get(IDENTIFIERS, {})
        if not barcodes_cfg:
            raise ValueError("Key {} missing for BcidSeqLib "
                             "configuration.".format(BARCODES))
        if not identifers_cfg:
            raise ValueError("Key {} missing for BcidSeqLib "
                             "configuration.".format(IDENTIFIERS))

        barcodes_cfg = BarcodeConfiguration(barcodes_cfg).validate()
        identifers_cfg = IdentifiersConfiguration(identifers_cfg).validate()
        self.validate()
        self.barcodes_cfg = barcodes_cfg
        self.identifers_cfg = identifers_cfg


class BcvSeqLibConfiguration(BaseLibraryConfiguration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for BcvSeqLibConfiguration.")
        super(BcvSeqLibConfiguration, self).__init__(cfg)

        barcodes_cfg = cfg.get(BARCODES, {})
        variants_cfg = cfg.get(VARIANTS, {})
        if not barcodes_cfg:
            raise ValueError("Key {} missing for BcvSeqLib "
                             "configuration.".format(BARCODES))
        if not variants_cfg:
            raise ValueError("Key {} missing for BcvSeqLib "
                             "configuration.".format(VARIANTS))

        barcodes_cfg = BarcodeConfiguration(barcodes_cfg).validate()
        variants_cfg = VariantsConfiguration(variants_cfg).validate()
        self.validate()
        self.barcodes_cfg = barcodes_cfg
        self.variants_cfg = variants_cfg


class IdOnlySeqLibConfiguration(BaseLibraryConfiguration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for IdOnlySeqLib configuration.")
        super(IdOnlySeqLibConfiguration, self).__init__(cfg)
        identifiers_cfg = cfg.get(IDENTIFIERS, {})
        identifiers_cfg = IdentifiersConfiguration(identifiers_cfg).validate()
        self.counts_file = cfg.get(COUNTS_FILE, "")
        self.identifiers_cfg = identifiers_cfg
        self.validate()

    def validate_counts_file(self):
        if not isinstance(self.counts_file, str):
            raise TypeError("Expected str for `counts file` but "
                            "found {}.".format(type(self.counts_file)))

        if not os.path.isfile(self.counts_file):
            raise IOError("File {} does not exist. Try using "
                          "absolute paths.".format(self.counts_file))

        _, tail = os.path.split(self.counts_file)
        _, ext = os.path.splitext(tail)
        if ext not in set(['.tsv', '.txt']):
            raise ValueError("Unsupported format for `counts file`. Files"
                             "need extension to be either bz2, gz or txt.")

    def validate(self):
        self.validate_counts_file()
        return self


class BasicSeqLibConfiguration(BaseLibraryConfiguration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for BasicSeqLibConfiguration.")
        super(BasicSeqLibConfiguration, self).__init__(cfg)

        variants_cfg = cfg.get(VARIANTS, {})
        if not variants_cfg:
            raise ValueError("Key {} missing for BcvSeqLib "
                             "configuration.".format(VARIANTS))

        self.variants_cfg = VariantsConfiguration(variants_cfg).validate()
        self.validate()


class OverlapSeqLibConfiguration(BaseLibraryConfiguration):

    def __init__(self, cfg):
        super(OverlapSeqLibConfiguration, self).__init__(cfg)

    def validate(self):
        return self


# -------------------------------------------------------------------------- #
#
#                      Root Configuration Classes
#
# -------------------------------------------------------------------------- #
class ExperimentConfiguration(Configuration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for experiment configuration.")

        self.store_cfg = StoreConfiguration(cfg).validate()
        if CONDITIONS not in cfg:
            raise ValueError("Experiment has no conditions element.")

        conditions_cfg = cfg.get(CONDITIONS, [])
        self.conditions = []

        if not isinstance(conditions_cfg, list):
            raise ValueError("Experiment conditions must be an iterable.")
        if len(conditions_cfg) == 0:
            raise ValueError("At least 1 experimental condition must be "
                             "present in an experiment.")

        for condition_cfg in cfg[CONDITIONS]:
            self.conditions.append(ConditonsConfiguration(condition_cfg))
        self.validate()

    def validate(self):
        for condition in self.conditions:
            condition.validate()
        return self


class ConditonsConfiguration(Configuration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for condition configuration.")

        self.store_cfg = StoreConfiguration(cfg).validate()
        if SELECTIONS not in cfg:
            raise ValueError("Condition has no selection element.")

        selections_cfg = cfg.get(SELECTIONS, [])
        self.selections = []

        if not isinstance(selections_cfg, list):
            raise ValueError("Condition selections must be an iterable.")
        if len(selections_cfg) == 0:
            raise ValueError("At least 1 selection must be "
                             "present in a condition.")

        for selection_cfg in cfg[SELECTIONS]:
            self.selections.append(SelectionsConfiguration(selection_cfg))
        self.validate()

    def validate(self):
        for selection in self.selections:
            selection.validate()
        # all_libs = [lib for sel in self.selections for lib in sel.libraries]
        # lib_names = set([lib.name for lib in all_libs])
        # if len(lib_names) != len(all_libs):
        #     raise ValueError("Libraries must have unique names accross"
        #                      " conditions and selections.")
        return self


class SelectionsConfiguration(Configuration):

    _lib_constructors = {
        "BarcodeSeqLib": BarcodeSeqLibConfiguration,
        "BcidSeqLib": BcidSeqLibConfiguration,
        "BcvSeqLib": BcvSeqLibConfiguration,
        "IdOnlySeqLib": IdOnlySeqLibConfiguration,
        "BasicSeqLib": BasicSeqLibConfiguration,
        "OverlapSeqLib": OverlapSeqLibConfiguration
    }

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for selection configuration.")

        self.libraries = []
        self.timepoints = []
        self.store_cfg = StoreConfiguration(cfg).validate()

        if LIBRARIES not in cfg:
            raise ValueError("Selection has no `{}` element.".format(
                LIBRARIES))

        libraries_cfg = cfg.get(LIBRARIES, [])
        if not isinstance(libraries_cfg, list):
            raise ValueError("Selection library config must be an iterable.")
        if len(libraries_cfg) == 0:
            raise ValueError("At least 1 library must be "
                             "present in a selection.")

        for libraries_cfg in cfg[LIBRARIES]:
            library_type = seqlib_type(libraries_cfg)
            if library_type is None:
                raise ValueError("Unrecognized SeqLib config")
            library_constructor = self._lib_constructors[library_type]
            self.libraries.append(library_constructor(libraries_cfg))
        self.validate()

    def validate(self):
        for library in self.libraries:
            library.validate()

        self.timepoints = [l.timepoint for l in self.libraries]
        if 0 not in self.timepoints:
            raise ValueError("Missing timepoint 0 [{}].".format(
                self.__class__.__name__))
        if len(self.timepoints) < 2:
            raise ValueError("Multiple timepoints "
                             "required [{}].".format(self.__class__.__name__))

        num_names = len(set([library.name for library in self.libraries]))
        if num_names != len(self.libraries):
            raise ValueError("Libraries must have unique names accross"
                             " selections [{}].".format(
                self.__class__.__name__))
        return self


class StoreConfiguration(Configuration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for experiment configuration.")

        self.name = cfg.get(NAME, "")
        self.output_dir = cfg.get(OUTPUT_DIR, "")
        self.store_path = cfg.get(STORE, "")

        if not isinstance(self.name, str):
            raise ValueError("Store `name` must be a str.")
        if not isinstance(self.output_dir, str):
            raise ValueError("Store `output_dir` must be a str.")
        if not isinstance(self.store_path, str):
            raise ValueError("Store `store_path` must be a str.")
        if not self.name:
            raise ValueError("Store does not have a name.")

        self.has_store_path = bool(self.store_path)
        self.has_output_dir = bool(self.output_dir)

    def validate(self):
        if self.has_store_path and not os.path.exists(self.store_path):
            raise IOError('Specified store file "{}" not found'.format(
                self.store_path))
        elif self.has_store_path and \
                        os.path.splitext(self.store_path)[-1].lower() != ".h5":
            raise ValueError('Unrecognized store file extension for '
                             '"{}"'.format(self.store_path))
        if self.has_output_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        return self