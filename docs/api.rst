Appendix: API documentation
###########################

This page contains automatically generated documentation from the Enrich2 codebase. It is intended for developers and advanced users.

:py:mod:`~enrich2.base.constants` --- Constants used by Enrich2
===============================================================

.. py:module:: constants
	:synopsis: Constant definitions

This module contains constant defitions used throughout Enrich2.


:py:mod:`~enrich2.base.storemanager` --- Abstract class for Enrich2 data
========================================================================

.. py:module:: storemanager
	:synopsis: Abstract class for Enrich2 data.

This module contains the class definition for the :py:class:`~enrich2.base.storemanager.StoreManager.StoreManager` abstract class, the shared base class for most classes in the `Enrich2 <index.html>`_ project. This class provides general behavior for the GUI and for handling HDF5 data files.

:py:class:`~enrich2.base.storemanager.StoreManager` class
---------------------------------------------------------
.. autoclass:: enrich2.base.storemanager.StoreManager
	:members:


:py:mod:`~enrich2.libraries.seqlib` --- Sequencing library file handling and element counting
===================================================================================

.. py:module:: seqlib
	:synopsis: Sequencing library file handling and element counting.

This module provides class definitions for the various types of sequencing library designs usable by `Enrich2 <index.html>`_. Data for each FASTQ_ file (or pair of overlapping FASTQ_ files for overlapping paired-end data) is read into its own :py:class:`~enrich2.libraries.seqlib.SeqLib` object. If necessary, FASTQ_ files should be split by index read before being read by a :py:class:`~enrich2.libraries.seqlib.SeqLib` object. :py:class:`~enrich2.libraries.seqlib.SeqLib` objects are coordinated by :py:mod:`~enrich2.selection.selection.Selection` objects.

:py:class:`~enrich2.libraries.seqlib.SeqLib` and :py:class:`~enrich2.libraries.variant.VariantSeqLib` are abstract classes. 

:py:class:`~enrich2.libraries.seqlib.SeqLib` class
--------------------------------------------------
.. autoclass:: enrich2.libraries.seqlib.SeqLib
	:members:

:py:class:`~enrich2.libraries.variant.VariantSeqLib` class
----------------------------------------------------------
.. autoclass:: enrich2.libraries.variant.VariantSeqLib
	:members:

:py:class:`~enrich2.libraries.barcode.BarcodeSeqLib` class
----------------------------------------------------------
.. autoclass:: enrich2.libraries.barcode.BarcodeSeqLib
	:members:

:py:class:`~enrich2.libraries.barcodevariant.BcvSeqLib` class
-------------------------------------------------------------
.. autoclass:: enrich2.libraries.barcodevariant.BcvSeqLib
	:members:

:py:class:`~enrich2.libraries.barcodeid.BcidSeqLib` class
---------------------------------------------------------
.. autoclass:: enrich2.libraries.barcodeid.BcidSeqLib
	:members:

:py:class:`~enrich2.libraries.basic.BasicSeqLib` class
------------------------------------------------------
.. autoclass:: enrich2.libraries.basic.BasicSeqLib
	:members:

:py:class:`~enrich2.libraries.seqlib.SeqLib` helper classes
-----------------------------------------------------------

:py:class:`~enrich2.sequence.aligner.Aligner` class
+++++++++++++++++++++++++++++++++++++++++++++++++++
.. autoclass:: enrich2.sequence.aligner.Aligner
	:members:

:py:class:`~enrich2.wildtype.WildTypeSequence` class
++++++++++++++++++++++++++++++++++++++++++++++++++++
.. autoclass:: enrich2.sequence.wildtype.WildTypeSequence
	:members:

:py:class:`~enrich2.libraries.barcodemap.BarcodeMap` class
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
.. autoclass:: enrich2.libraries.barcodemap.BarcodeMap
	:members:

:py:mod:`~enrich2.selection.selection` --- Functional score calculation using SeqLib count data
===============================================================================================

.. py:module:: selection
	:synopsis: Functional score calculation using :py:class:`~enrich2.libraries.seqlib.SeqLib` count data.

This module provides class definitions for the :py:class:`~enrich2.selection.selection.Selection` class. This is where functional scores are calculated from the :py:class:`~enrich2.libraries.seqlib.SeqLib` count data. For time series data, each time point in the selection can have multiple :py:class:`~enrich2.libraries.seqlib.SeqLib` assigned to it, in which case the counts for each element will be added together. Each time series selection must have a time point 0 (the "input library").

:py:class:`~enrich2.selection.selection.Selection` class
--------------------------------------------------------
.. autoclass:: enrich2.selection.selection.Selection
	:members:

:py:mod:`~enrich2.experiment.condition` --- Dummy class for GUI
===============================================================

.. py:module:: condition
	:synopsis: Dummy class for GUI.

This module provides class definitions for the :py:class:`~enrich2.experiment.condition.Condition` classes. This class is required for proper GUI operation. All condition-related behaviors are in the :py:class:`~enrich2.experiment.Experiment` class.

:py:class:`~enrich2.experiment.condition.Condition` class
---------------------------------------------------------
.. autoclass:: enrich2.experiment.condition.Condition
	:members:

:py:mod:`~enrich2.experiment.experiment` --- Aggregation of replicate selections
================================================================================

.. py:module:: experiment
	:synopsis: Aggregation of replicate selections.

This module provides class definitions for the :py:class:`~enrich2.experiment.experiment.Experiment`. Functional scores for selections within the same condition are combined to generate a single functional score (and associated error) for each element in each experimental condition.

:py:class:`~enrich2.experiment.experiment.Experiment` class
-----------------------------------------------------------
.. autoclass:: enrich2.experiment.experiment.Experiment
	:members:

Utility functions
=================

Configuration object type detection
-----------------------------------

.. automodule:: enrich2.config.config_check
	:members:

.. automodule:: enrich2.config.types
	:members:

Dataframe and index helper functions
------------------------------------

.. automodule:: enrich2.base.dataframe
	:members:

.. _api-variant-helper:

Variant helper functions
------------------------

.. automodule:: enrich2.libraries.variant
	:members: mutation_count, has_indel, has_unresolvable, protein_variant

HGVS_ variant regular expressions
+++++++++++++++++++++++++++++++++

.. autodata:: enrich2.libraries.variant.re_protein

.. autodata:: enrich2.libraries.variant.re_coding

.. autodata:: enrich2.libraries.variant.re_noncoding

Plugin Scripting
================
.. automodule:: enrich2.plugins
	:members:

.. automodule:: enrich2.plugins.scoring
	:members:

.. automodule:: enrich2.plugins.options
	:members:

Enrich2 entry points
====================

.. automodule:: enrich2.main
	:members:


