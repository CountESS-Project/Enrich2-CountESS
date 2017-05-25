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
import logging
from abc import ABC, abstractclassmethod

from .config_check import *
from ..plugins import load_scorer_class_and_options
from ..plugins.options import Options


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
TRIM_START = 'start'
TRIM_LENGTH = 'length'
SCORER = 'scorer'
SCORER_PATH = 'scorer_path'
SCORER_OPTIONS = 'scorer_options'


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
class ScorerConfiguration(Configuration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for fastq configuration.")

        if SCORER_PATH not in cfg:
            raise KeyError("Missing '{}' key from {} configuration.".format(
                SCORER_PATH, SCORER
            ))
        if SCORER_OPTIONS not in cfg:
            raise KeyError("Missing '{}' key from {} configuration.".format(
                SCORER_OPTIONS, SCORER
            ))

        path = cfg[SCORER_PATH]
        attrs = cfg[SCORER_OPTIONS]
        scorer_class, options, _ = \
            load_scorer_class_and_options(path)

        self.__options = options if options is not None else Options()
        self.scorer_class = scorer_class
        self.scorer_class_attrs = attrs
        self.scorer_path = path
        self.validate()

    def validate(self):
        if self.scorer_class is None:
            raise TypeError("Scoring class cannot be NoneType.")

        passed_varnames = set(self.scorer_class_attrs.keys())
        expected_varnames = set(self.__options.option_varnames())

        # Check for unused params in attrs and throw error
        unused = list(passed_varnames - expected_varnames)
        unused_str = ', '.join(["'{}'".format(v) for v in unused])
        if unused:
            raise ValueError("The options {} in the provided configuration are"
                             " not defined in the plugin.".format(unused_str))

        # Validate each value in passed attrs
        for varname in passed_varnames & expected_varnames:
            value = self.scorer_class_attrs[varname]
            self.__options.validate_option_by_varname(varname, value)
            self.__options.set_option_by_varname(varname, value)

        # If missing params log warning and set to default
        defaults = list(expected_varnames - passed_varnames)
        defaults_str = ', '.join(["'{}'".format(v) for v in defaults])
        if defaults:
            logging.warning("The options {} were not found in the provided"
                            " configuration file. Setting as default "
                            "values.".format(defaults_str),
                            extra={'oname': self.__class__.__name__})

        self.scorer_class_attrs = self.__options.to_dict()
        return self

    def get_options(self, keep_defaults=True):
        attrs = {}
        if keep_defaults:
            for varname, opt in self.__options.items():
                value = opt.get_value()
                default = opt.get_default_value()
                attrs[varname] = (value, value == default)
            return attrs
        else:
            return self.__options.to_dict()


class FASTQConfiguration(Configuration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for fastq configuration.")

        if READS not in cfg:
            raise KeyError("Missing '{}' key from {} configuration.".format(
                READS, FASTQ
            ))

        filters_cfg = cfg.get(FILTERS, {})
        self.reads = cfg.get(READS, "")
        self.reverse = cfg.get(REVERSE, False)
        self.trim_start = cfg.get(TRIM_START, 1)
        self.trim_length = cfg.get(TRIM_LENGTH, sys.maxsize)
        self.filters_cfg = FiltersConfiguration(filters_cfg)
        self.validate()

    def validate_reverse(self):
        if not isinstance(self.reverse, bool):
            raise TypeError("Expected bool for reverse but found {}.".format(
                type(self.reverse)
            ))

    def validate_trim_start(self):
        if not isinstance(self.trim_start, int):
            raise TypeError("FASTQ `start` must be an integer."     
                            " Found type {}.".format(type(self.trim_start)))
        if self.trim_start < 0:
            raise ValueError("FASTQ `start` must not be negative.")

    def validate_trim_length(self):
        if not isinstance(self.trim_length, int):
            raise TypeError("FASTQ `length` must be an integer."     
                            " Found type {}.".format(type(self.trim_length)))
        if self.trim_length < 0:
            raise ValueError("FASTQ `length` must not be negative.")

    def validate_reads(self):
        if not isinstance(self.reads, str):
            raise TypeError("Expected str for reads but found {}.".format(
                type(self.reads)
            ))
        if not os.path.isfile(self.reads):
            raise IOError("File {} does not exist."
                          " Try using absolute paths.".format(self.reads))

        _, tail = os.path.split(self.reads)
        _, ext = os.path.splitext(tail)
        if ext not in {'.bz2', '.gz', '.fq', '.fastq'}:
            raise IOError("Unsupported format for reads. Files"
                             "need extension to be either bz2, gz, fq or"
                             "fastq.")

    def validate(self):
        self.validate_reverse()
        self.validate_trim_start()
        self.validate_trim_length()
        self.validate_reads()
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

    def to_dict(self):
        return {
            FILTERS_CHASTITY: self.chaste,
            FILTERS_MAX_N: self.max_n,
            FILTERS_MIN_Q: self.min_base_quality,
            FILTERS_AVG_Q: self.avg_base_quality
        }


class BarcodeConfiguration(Configuration):

    def __init__(self, cfg, require_map=False):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for barcodes configuration.")
        if not isinstance(require_map, bool):
            raise TypeError("Argument 'require_map' must be a boolean.")

        self.min_count = cfg.get(BARCODE_MIN_COUNT, 0)
        self.map_file = cfg.get(BARCODE_MAP_FILE, None)

        if require_map and not self.map_file:
            raise ValueError("Map file cannot be empty.")

        self.barcodemap = None
        self.validate()

    def validate_map_file(self):
        if self.map_file and not isinstance(self.map_file, str):
            raise TypeError("Expected str for map file but found {}.".format(
                type(self.map_file)
            ))
        if self.map_file and not os.path.isfile(self.map_file):
            raise IOError("File {} does not exist."
                          " Try using absolute paths.".format(self.map_file))
        elif self.map_file and os.path.isfile(self.map_file):
            _, tail = os.path.split(self.map_file)
            _, ext = os.path.splitext(tail)
            if ext not in {'.bz2', '.gz', '.txt'}:
                raise IOError("Unsupported format for map file. Files"
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

    DEFAULT_MAX_MUTATIONS = 10

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for variants configuration.")

        if WILDTYPE not in cfg:
            raise KeyError("Missing '{}' key from {} configuration.".format(
                WILDTYPE, VARIANTS
            ))

        wildtype_cfg = cfg.get(WILDTYPE, {})
        self.use_aligner = cfg.get(USE_ALIGNER, False)
        self.max_mutations = cfg.get(VARIANTS_MAX_MUTATIONS,
                                     self.DEFAULT_MAX_MUTATIONS)
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

        if self.max_mutations > self.DEFAULT_MAX_MUTATIONS:
            raise ValueError("Variants `max mutations` should not be higher "
                             "than {}.".format(self.DEFAULT_MAX_MUTATIONS))

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

        if SEQUENCE not in cfg:
            raise KeyError("Missing '{}' from base library "
                             "configuration.".format(SEQUENCE))

        self.coding = cfg.get(CODING, False)
        self.reference_offset = cfg.get(REF_OFFSET, 0)
        self.sequence = cfg.get(SEQUENCE, "")
        self.validate()

    def validate_coding(self):
        if not isinstance(self.coding, bool):
            raise TypeError("Wildtype `coding` must be a boolean."
                            " Found type "
                            "{}.".format(type(self.coding).__name__))

    def validate_reference_offset(self):
        if not isinstance(self.reference_offset, int):
            raise TypeError("Wildtype `reference offset` "
                            "must be an integer. Found type "
                            "{}.".format(type(self.reference_offset).__name__))
        if self.reference_offset < 0:
            raise ValueError("Wildtype `reference offset` "
                             "must not be negative.")

        multple_of_three = self.reference_offset % 3 == 0
        if self.coding and not multple_of_three:
            logging.warning(
                "Reference offset is not a multiple of three when setting "
                "`protein coding` as True. Setting to reference offset to 0.",
                extra={'oname': self.__class__.__name__}
            )
            self.reference_offset = 0
            # raise ValueError("If `protein coding` is selected, "
            #                  "`reference offset` must be a multiple of 3.")

    def validate_sequence(self):
        if not isinstance(self.sequence, str):
            raise TypeError("Variants `sequence` must be a string. "
                            "Found type "
                            "{}".format(type(self.sequence).__name__))

        if not self.sequence:
            raise ValueError(
                "Cannot have an empty sequence [{}].".format(
                    type(self.sequence).__name__))

        if self.sequence and os.path.isfile(self.sequence):
            _, tail = os.path.split(self.sequence)
            _, ext = os.path.splitext(tail)
            if ext not in {'.bz2', '.gz', '.fa', 'fasta'}:
                raise IOError("Unsupported format for fasta file. Files"
                                 " need extension to be either bz2, gz, "
                                 "fa or fasta.")

        if os.path.isfile(self.sequence):
            with open(self.sequence, 'rt') as fp:
                # TODO: replace with fasta reader
                self.sequence = fp.read().strip()

        self.sequence = self.sequence.upper()
        atcg_chars_only = "^[ACGT]+$"
        if self.sequence:
            if not re.match(atcg_chars_only, self.sequence):
                raise ValueError("'sequence' contains unexpected "
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

    def __init__(self, cfg, init_fastq=False):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for base library configuration.")
        if not isinstance(init_fastq, bool):
            raise TypeError("'init_fastq' needs to be a boolean.")

        if TIMEPOINT not in cfg:
            raise KeyError("Missing '{}' from base library "
                             "configuration.".format(TIMEPOINT))

        if init_fastq and FASTQ not in cfg:
            raise KeyError("Missing '{}' from base library "
                             "configuration.".format(FASTQ))

        if not init_fastq and COUNTS_FILE not in cfg:
            raise KeyError("Missing '{}' from base library "
                             "configuration.".format(COUNTS_FILE))

        fastq_cfg = cfg.get(FASTQ, None)
        self.counts_file = cfg.get(COUNTS_FILE, None)
        if init_fastq:
            self.fastq_cfg = FASTQConfiguration(fastq_cfg).validate()
        else:
            self.fastq_cfg = None

        self.seqlib_type = seqlib_type(cfg)
        if self.seqlib_type is None:
            raise ValueError("Unrecognized SeqLib config")

        self.timepoint = cfg.get(TIMEPOINT)
        self.report_filtered_reads = cfg.get(REPORT_FILTERED_READS, False)
        if not self.counts_file:
            self.counts_file = None

        if init_fastq and self.counts_file is not None:
            raise ValueError("Cannot define both a counts file and reads file "
                             "at the same time. It's one or the other, buddy.")
        if fastq_cfg is None and self.counts_file is None:
            raise ValueError("Must have either a fastq definition or counts file.")

        self.store_cfg = StoreConfiguration(cfg, has_scorer=False).validate()
        self.validate()

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

    def validate_counts_file(self):
        if self.fastq_cfg is None and not self.counts_file:
            raise ValueError("Must provide a counts file if not using fastq.")

        if self.counts_file and not isinstance(self.counts_file, str):
            raise TypeError("Expected str for `counts file` but "
                            "found {}.".format(type(self.counts_file)))

        if self.counts_file and not os.path.isfile(self.counts_file):
            raise IOError("File {} does not exist. Try using "
                          "absolute paths.".format(self.counts_file))
        elif self.counts_file and os.path.isfile(self.counts_file):
            _, tail = os.path.split(self.counts_file)
            _, ext = os.path.splitext(tail)
            if ext not in {'.tsv', '.txt'}:
                raise IOError("Unsupported format for `counts file`. Files"
                                 "need extension to be either bz2, gz or txt.")

    def validate(self):
        self.validate_report_filtered_reads()
        self.validate_timepoint()
        self.validate_counts_file()
        return self


class BaseVariantSeqLibConfiguration(BaseLibraryConfiguration):

    def __init__(self, cfg, init_fastq=False):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for BaseVariantSeqLibConfiguration.")
        BaseLibraryConfiguration.__init__(self, cfg, init_fastq)

        if VARIANTS not in cfg:
            raise KeyError("Key {} missing for BcvSeqLib "
                           "configuration.".format(VARIANTS))

        variants_cfg = cfg.get(VARIANTS, {})
        if not variants_cfg:
            raise ValueError("Variants configuration cannot be empty.")

        self.variants_cfg = VariantsConfiguration(variants_cfg).validate()
        self.validate()


class BarcodeSeqLibConfiguration(BaseLibraryConfiguration):

    def __init__(self, cfg, init_fastq=True, reqiure_map=False):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for BarcodeSeqLibConfiguration.")
        BaseLibraryConfiguration.__init__(self, cfg, init_fastq)

        if BARCODES not in cfg:
            raise KeyError("Key {} missing for BcidSeqLib "
                           "configuration.".format(BARCODES))
        barcodes_cfg = cfg.get(BARCODES)

        self.barcodes_cfg = BarcodeConfiguration(
            barcodes_cfg, reqiure_map).validate()
        self.validate()


class BcidSeqLibConfiguration(BarcodeSeqLibConfiguration):

    def __init__(self, cfg, init_fastq=True):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for BcidSeqLibConfiguration.")

        if IDENTIFIERS not in cfg:
            raise KeyError("Key {} missing for BcidSeqLib "
                           "configuration.".format(IDENTIFIERS))

        BarcodeSeqLibConfiguration.__init__(
            self, cfg, init_fastq, reqiure_map=True)

        identifers_cfg = cfg.get(IDENTIFIERS)
        identifers_cfg = IdentifiersConfiguration(identifers_cfg).validate()

        self.validate()
        self.identifers_cfg = identifers_cfg


class BcvSeqLibConfiguration(BaseVariantSeqLibConfiguration,
                             BarcodeSeqLibConfiguration):

    def __init__(self, cfg, init_fastq=True):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for BcvSeqLibConfiguration.")

        BaseVariantSeqLibConfiguration.__init__(
            self, cfg, init_fastq)
        BarcodeSeqLibConfiguration.__init__(
            self, cfg, init_fastq, reqiure_map=True)

        self.validate()


class IdOnlySeqLibConfiguration(BaseLibraryConfiguration):

    def __init__(self, cfg):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for IdOnlySeqLib configuration.")

        BaseLibraryConfiguration.__init__(self, cfg, init_fastq=False)
        identifiers_cfg = cfg.get(IDENTIFIERS, {})
        identifiers_cfg = IdentifiersConfiguration(identifiers_cfg).validate()

        self.identifiers_cfg = identifiers_cfg
        self.validate()


class BasicSeqLibConfiguration(BaseVariantSeqLibConfiguration):

    def __init__(self, cfg, init_fastq=True):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for BasicSeqLibConfiguration.")

        BaseVariantSeqLibConfiguration.__init__(self, cfg, init_fastq)

        self.validate()


# -------------------------------------------------------------------------- #
#
#                      Root Configuration Classes
#
# -------------------------------------------------------------------------- #
class ExperimentConfiguration(Configuration):

    def __init__(self, cfg, init_from_gui=False):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for experiment configuration.")

        if CONDITIONS not in cfg:
            raise KeyError("Missing required config value `{}` [{}]"
                           "".format(CONDITIONS, self.__class__.__name__))

        has_scorer = not init_from_gui
        if not init_from_gui:
            if SCORER not in cfg:
                raise KeyError("Missing required config value `{}` [{}]"
                               "".format(SCORER, self.__class__.__name__))

        self.store_cfg = StoreConfiguration(cfg, has_scorer).validate()
        condition_cfgs = cfg.get(CONDITIONS)
        self.condition_cfgs = []

        for cfg in condition_cfgs:
            self.condition_cfgs.append(
                ConditonConfiguration(cfg, init_from_gui))
        self.validate()

    def validate(self):
        if not isinstance(self.condition_cfgs, list):
            raise TypeError("Experiment `conditions` must be a list.")

        if len(self.condition_cfgs) == 0:
            raise ValueError("At least 1 experimental condition must be "
                             "present in an experiment.")

        condition_names = []
        for cfg in self.condition_cfgs:
            cfg.validate()
            condition_names.append(cfg.store_cfg.name)

        if len(set(condition_names)) != len(condition_names):
            raise ValueError("Non-unique condition names in Experiment "
                             "[{}].".format(self.__class__.__name__))

        selection_names = [
            s_cfg.store_cfg.name
            for c_cfg in self.condition_cfgs
            for s_cfg in c_cfg.selection_cfgs
        ]
        if len(set(selection_names)) != len(selection_names):
            raise ValueError("Non-unique selection names across conditions "
                             "[{}].".format(self.__class__.__name__))

        self.store_cfg.validate()
        return self


class ConditonConfiguration(Configuration):

    def __init__(self, cfg, init_from_gui=False):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for condition configuration.")

        if SELECTIONS not in cfg:
            raise KeyError("Configuration is missing required config value "
                           "`{}` [{}]".format(SELECTIONS,
                                              self.__class__.__name__))

        self.selection_cfgs = []
        self.init_from_gui = init_from_gui
        self.store_cfg = StoreConfiguration(cfg, has_scorer=False)
        selection_cfgs = cfg.get(SELECTIONS, [])

        for cfg in selection_cfgs:
            self.selection_cfgs.append(
                SelectionConfiguration(
                    cfg, has_scorer=False, init_from_gui=init_from_gui))
        self.validate()

    def validate(self):
        if not isinstance(self.selection_cfgs, list):
            raise TypeError("Condition `selections` must be a list.")

        if not self.init_from_gui:
            if len(self.selection_cfgs) == 0:
                raise ValueError("At least 1 selection must be "
                                 "present in a condition.")

        for cfg in self.selection_cfgs:
            cfg.validate()

        self.store_cfg.validate()
        return self


class SelectionConfiguration(Configuration):

    _lib_constructors = {
        "BarcodeSeqLib": BarcodeSeqLibConfiguration,
        "BcidSeqLib": BcidSeqLibConfiguration,
        "BcvSeqLib": BcvSeqLibConfiguration,
        "IdOnlySeqLib": IdOnlySeqLibConfiguration,
        "BasicSeqLib": BasicSeqLibConfiguration
    }

    def __init__(self, cfg, has_scorer=True, init_from_gui=False):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for selection configuration.")

        self.lib_cfgs = []
        self.timepoints = []
        self.init_from_gui = init_from_gui
        has_scorer = has_scorer and not init_from_gui
        self.store_cfg = StoreConfiguration(cfg, has_scorer).validate()

        if LIBRARIES not in cfg:
            raise KeyError("Selection has no `{}` element.".format(
                LIBRARIES))

        library_cfgs = cfg.get(LIBRARIES)
        if not isinstance(library_cfgs, list):
            raise TypeError("Selection library config must be a list.")

        for libraries_cfg in library_cfgs:
            library_type = seqlib_type(libraries_cfg)
            if library_type is None:
                raise ValueError("Unrecognized SeqLib config")
            library_constructor = self._lib_constructors[library_type]
            self.lib_cfgs.append(library_constructor(libraries_cfg))
        self.validate()

    def validate(self):
        if not self.init_from_gui:
            if len(self.lib_cfgs) == 0:
                raise ValueError("At least 1 library must be "
                                 "present in a selection.")

            self.timepoints = set([l.timepoint for l in self.lib_cfgs])
            if 0 not in self.timepoints:
                raise ValueError("Missing timepoint 0 [{}].".format(
                    self.__class__.__name__))

            if len(self.timepoints) < 2:
                raise ValueError(
                    "Multiple timepoints required [{}].".format(
                        self.__class__.__name__))

            if self.store_cfg.has_scorer:
                name = self.store_cfg.scorer_cfg.scorer_class.name
                if len(self.timepoints) < 3 and name == 'Regression':
                    raise ValueError("Insufficient number of timepoints for "
                                     "regression scoring "
                                     "[{}].".format(self.__class__.__name__))

        num_names = len(
            set([lib_cfg.store_cfg.name for lib_cfg in self.lib_cfgs]))
        if num_names != len(self.lib_cfgs):
            raise ValueError("Libraries must have unique names within a "
                             "selection [{}].".format(self.__class__.__name__))

        for lib_cfg in self.lib_cfgs:
            lib_cfg.validate()

        self.store_cfg.validate()
        return self


class StoreConfiguration(Configuration):

    def __init__(self, cfg, has_scorer=True):
        if not isinstance(cfg, dict):
            raise TypeError("dict required for store configuration.")
        if not isinstance(has_scorer, bool):
            raise TypeError("Boolean required for 'has_storer'.")

        if has_scorer and SCORER not in cfg:
            raise KeyError("Missing '{}' key from store configuration.".format(
                SCORER
            ))
        if NAME not in cfg:
            raise KeyError("Missing '{}' key from store configuration.".format(
                NAME
            ))

        self.scorer_cfg = cfg.get(SCORER, {})
        self.name = cfg.get(NAME)
        self.output_dir = cfg.get(OUTPUT_DIR, "")
        self.store_path = cfg.get(STORE, "")
        self.has_scorer = has_scorer

        if not isinstance(self.name, str):
            raise TypeError("Store `name` must be a str.")

        if not isinstance(self.output_dir, str):
            raise TypeError("Store `output_dir` must be a str.")

        if not isinstance(self.store_path, str):
            raise TypeError("Store `store_path` must be a str.")

        if not isinstance(self.scorer_cfg, dict):
            raise TypeError("Store `scorer_cfg` must be a dict.")

        if not self.name:
            raise ValueError("Store does not have a name.")

        if self.has_scorer and not self.scorer_cfg:
            raise ValueError("Scorer configuration cannot be empty.")

        self.has_store_path = bool(self.store_path)
        self.has_output_dir = bool(self.output_dir)
        if self.has_scorer:
            self.scorer_cfg = ScorerConfiguration(self.scorer_cfg)
        else:
            self.scorer_cfg = None
        self.validate()

    def validate(self):
        if self.has_scorer and self.scorer_cfg is not None:
            self.scorer_cfg.validate()

        if self.has_scorer and self.scorer_cfg is None:
            raise ValueError("Scorer config cannot be NoneType.")

        if self.has_store_path and not os.path.exists(self.store_path):
            raise IOError('Specified store file "{}" not found'.format(
                self.store_path))

        elif self.has_store_path \
                and os.path.splitext(self.store_path)[-1].lower() != ".h5":
            raise IOError('Unrecognized store file extension for '
                          '"{}"'.format(self.store_path))

        if self.has_output_dir:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

        return self
