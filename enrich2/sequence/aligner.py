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
Enrich2 aligner module
======================
Module for alignment of variants to the wild type sequence.

This module is optional, and using it will dramatically increase runtime when
counting variants. It is only recommended for users who need to count
insertion and deletion variants (i.e. not coding sequences).
"""

import logging
import numpy as np

try:
    from ambivert.ambivert import gapped_alignment_to_cigar
    from ambivert import align

    # Reset the logging handlers after loading ambivert
    for handler in logging.getLogger("ambivert").handlers:
        handler.close()
    logging.getLogger('ambivert').handlers = []
    logging.captureWarnings(False)
    USE_AMBIVERT = True
except ImportError:
    USE_AMBIVERT = False


__all__ = [
    "Aligner"
]


#: Default similarity matrix used by the aligner.
#: User-defined matrices must have this format.
_simple_similarity = {
    'A': {'A': 1, 'C': -1, 'G': -1, 'T': -1, 'N': 0, 'X': 0},
    'C': {'A': -1, 'C': 1, 'G': -1, 'T': -1, 'N': 0, 'X': 0},
    'G': {'A': -1, 'C': -1, 'G': 1, 'T': -1, 'N': 0, 'X': 0},
    'T': {'A': -1, 'C': -1, 'G': -1, 'T': 1, 'N': 0, 'X': 0},
    'N': {'A': 0, 'C': 0, 'G': 0, 'T': 0, 'N': 0, 'X': 0},
    'X': {'A': 0, 'C': 0, 'G': 0, 'T': 0, 'N': 0, 'X': 0},
    'gap': -1
}


class Aligner(object):
    """
    Class for performing local alignment of two DNA sequences.

    This class implements `Needleman-Wunsch <http://en.wikipedia.org/wiki/
    Needleman%E2%80%93Wunsch_algorithm>`_ local alignment.

    The :py:class:`~enrich2.sequence.aligner.Aligner` requires a scoring matrix 
    when created. The format is a nested dictionary, with a special ``'gap'`` 
    entry for the gap penalty (this value is used for both gap opening and gap
    extension).

    The ``'X'`` nucleotide is a special case for unresolvable mismatches in
    :py:class:`~enrich2.libraries.overlap.OverlapSeqLib` variant data.
    
    Parameters
    ----------
    similarity : `dict`
        Similarity matrix used by the aligner, must contain a cost mapping 
        between each of 'A', 'C', 'G', 'T', 'N', 'X'.
            
    Attributes
    ----------
    similarity : `dict`
        Similarity matrix used by the aligner, must contain a cost mapping 
        between each of 'A', 'C', 'G', 'T', 'N', 'X'.
    matrix : :py:class:`~numpy.ndarray`
        The dynamically computed cost matrix.
    seq1 : `str`
        Reference sequence.
    seq2 : `str`
        The sequence that is to be aligned.
    calls : `int`
        Number of times `align` has been performed.
    
    Methods
    -------
    align
        Align two sequences using ``Needleman-Wusch``.
    
    Notes
    -----
    This class implements `Needleman-Wunsch <http://en.wikipedia.org/wiki/
    Needleman%E2%80%93Wunsch_algorithm>`_ local alignment.
    """
    _MAT = 1    # match
    _INS = 2    # insertion (with respect to wild type)
    _DEL = 3    # deletion (with respect to wild type)
    _END = 4    # end of traceback

    def __init__(self, similarity=_simple_similarity):
        similarity_keys = list(similarity.keys())
        if 'gap' in similarity_keys:
            similarity_keys.remove('gap')
        for key in similarity_keys:
            keys_map_to_dicts = all(x in similarity[key]
                                    for x in similarity_keys)
            symmetrical = len(similarity[key]) != len(similarity_keys)
            if not keys_map_to_dicts or symmetrical:
                raise ValueError("Asymmetrical alignment scoring matrix")

        self.similarity = similarity
        if 'gap' not in self.similarity:
            raise ValueError("No gap penalty in alignment scoring matrix.")

        self.matrix = None
        self.seq1 = None
        self.seq2 = None
        self.calls = 0

        global USE_AMBIVERT
        if USE_AMBIVERT:
            self.align = self.align_ambivert
        else:
            self.align = self.align_enrich2

    def align_ambivert(self, seq1, seq2):
        """
        Aligns the two sequences, *seq1* and *seq2* and returns a list of
        tuples describing the differences between the sequences.

        The tuple format is ``(i, j, type, length)``, where ``i`` and ``j``
        are the positions in *seq1* and *seq2*, respectively, and type is one
        of ``"match"``, ``"mismatch"``, ``"insertion"``, or ``"deletion"``.
        For indels, the ``length`` value is the number of bases inserted or
        deleted with respect to *seq1* starting at ``i``.

        Parameters
        ----------
        seq1 : `str`
            Reference sequence.
        seq2 : `str`
            The sequence that is to be aligned.

        Returns
        -------
        `list`
            list of tuples describing the differences between the sequences.
        """
        a1, a2, *_ = needleman_wunsch(seq1, seq2)
        backtrace, *_ = cigar_to_backtrace(
            seq1, seq2,
            gapped_alignment_to_cigar(a1, a2)[0]
        )
        return backtrace

    def align_enrich2(self, seq1, seq2):
        """
        Aligns the two sequences, *seq1* and *seq2* and returns a list of
        tuples describing the differences between the sequences.

        The tuple format is ``(i, j, type, length)``, where ``i`` and ``j``
        are the positions in *seq1* and *seq2*, respectively, and type is one
        of ``"match"``, ``"mismatch"``, ``"insertion"``, or ``"deletion"``.
        For indels, the ``length`` value is the number of bases inserted or
        deleted with respect to *seq1* starting at ``i``.
        
        Parameters
        ----------
        seq1 : `str`
            Reference sequence.
        seq2 : `str`
            The sequence that is to be aligned.
            
        Returns
        -------
        `list`
            list of tuples describing the differences between the sequences.
        """
        if not isinstance(seq1, str):
            raise TypeError("First sequence must be a str type")
        if not isinstance(seq2, str):
            raise TypeError("Second sequence must be a str type")
        if not seq1:
            raise ValueError("First sequence must not be empty.")
        if not seq2:
            raise ValueError("Second sequence must not be empty.")

        self.matrix = np.ndarray(
            shape=(len(seq1) + 1, len(seq2) + 1),
            dtype=np.dtype([('score', np.int), ('trace', np.byte)])
        )
        seq1 = seq1.upper()
        seq2 = seq2.upper()

        # build matrix of scores/traceback information
        for i in range(len(seq1) + 1):
            self.matrix[i, 0] = (self.similarity['gap'] * i, Aligner._DEL)
        for j in range(len(seq2) + 1):
            self.matrix[0, j] = (self.similarity['gap'] * j, Aligner._INS)
        for i in range(1, len(seq1) + 1):
            for j in range(1, len(seq2) + 1):
                match = (self.matrix[i - 1, j - 1]['score'] +
                         self.similarity[seq1[i - 1]][seq2[j - 1]],
                         Aligner._MAT)
                delete = (self.matrix[i - 1, j]['score'] +
                          self.similarity['gap'], Aligner._DEL)
                insert = (self.matrix[i, j - 1]['score'] +
                          self.similarity['gap'], Aligner._INS)
                self.matrix[i, j] = max(delete, insert, match,
                                        key=lambda x: x[0])
        self.matrix[0, 0] = (0, Aligner._END)

        # calculate alignment from the traceback
        i = len(seq1)
        j = len(seq2)
        traceback = list()
        while i > 0 or j > 0:
            if self.matrix[i, j]['trace'] == Aligner._MAT:
                if seq1[i - 1] == seq2[j - 1]:
                    traceback.append((i - 1, j - 1, "match", None))
                else:
                    traceback.append((i - 1, j - 1, "mismatch", None))
                i -= 1
                j -= 1
            elif self.matrix[i, j]['trace'] == Aligner._INS:
                traceback.append((i - 1, j - 1, "insertion", 1))
                j -= 1
            elif self.matrix[i, j]['trace'] == Aligner._DEL:
                traceback.append((i - 1, j - 1, "deletion", 1))
                i -= 1
            elif self.matrix[i, j]['trace'] == Aligner._END:
                pass
            else:
                raise RuntimeError("Invalid value in alignment traceback.")
        traceback.reverse()

        # combine indels
        indel = None
        traceback_combined = list()
        for t in traceback:
            if t[2] == "insertion" or t[2] == "deletion":
                if indel is not None:
                    if t[2] == indel[2]:
                        indel[3] += t[3]
                    else:
                        raise RuntimeError("Aligner failed to combine indels. "
                                           "Check gap penalty.")
                else:
                    indel = list(t)
            else:
                if indel is not None:
                    traceback_combined.append(tuple(indel))
                    indel = None
                traceback_combined.append(t)
        if indel is not None:
            traceback_combined.append(tuple(indel))

        self.calls += 1
        return traceback_combined


def needleman_wunsch(seq1, seq2):
    """
    Wrapper method for Needleman-Wunsch alignment using
    the plumb.bob C implementation

    Parameters
    ----------
    seq1 : `str`
        an ascii DNA sequence string.  This is the query
        sequence and must be all upper case
    seq2 : `str`
        an ascii DNA sequence string.  This is the reference
        sequence and may contain lower case soft masking

    Returns
    -------
    `tuple`
        A tuple containing aligned seq1, aligned seq2, start position
        in seq1 and start position in seq2
    """
    DNA_MAP = align.align_ctypes.make_map('ACGTN', 'N', True)
    DNA_SCORE = align.align_ctypes.make_DNA_scoring_matrix(
        match=1, mismatch=-1, nmatch=0)

    alignment = align.global_align(
        bytes(seq1, 'ascii'),
        len(seq1),
        bytes(seq2.upper(), 'ascii'),
        len(seq2),
        DNA_MAP[0],
        DNA_MAP[1],
        DNA_SCORE,
        -1, 0  # gap open, gap extend
    )

    if '-' in seq1 or '-' in seq2:
        raise RuntimeError('Aligning Sequences with gaps is not supported',
                           seq1, seq2)
    start_seq1 = 0
    start_seq2 = 0
    frag = alignment[0].align_frag
    align_seq1 = ''
    align_seq2 = ''

    while frag:
        frag = frag[0]

        if frag.type == align.MATCH:
            f1 = seq1[frag.sa_start:frag.sa_start + frag.hsp_len]
            f2 = seq2[frag.sb_start:frag.sb_start + frag.hsp_len]
            align_seq1 += f1
            align_seq2 += f2

        elif frag.type == align.A_GAP:
            align_seq1 += '-' * frag.hsp_len
            align_seq2 += seq2[frag.sb_start:frag.sb_start + frag.hsp_len]

        elif frag.type == align.B_GAP:
            align_seq1 += seq1[frag.sa_start:frag.sa_start + frag.hsp_len]
            align_seq2 += '-' * frag.hsp_len

        frag = frag.next

    assert len(align_seq1) == len(align_seq2)
    align.alignment_free(alignment)
    return align_seq1, align_seq2, start_seq1, start_seq2


def smith_waterman(seq1, seq2):
    """
    Wrapper method for Smith-Waterman alignment using
    the plumb.bob C implementation

    Parameters
    ----------
    seq1 : `str`
        an ascii DNA sequence string.  This is the query
        sequence and must be all upper case
    seq2 : `str`
        an ascii DNA sequence string.  This is the reference
        sequence and may contain lower case soft masking

    Returns
    -------
    `tuple`
        A tuple containing aligned seq1, aligned seq2, start position
        in seq1 and start position in seq2
    """
    DNA_MAP = align.align_ctypes.make_map('ACGTN', 'N', True)
    DNA_SCORE = align.align_ctypes.make_DNA_scoring_matrix(
        match=1, mismatch=-1, nmatch=0)

    alignment = align.local_align(
        bytes(seq1, 'ascii'), len(seq1),
        bytes(seq2.upper(), 'ascii'), len(seq2),
        DNA_MAP[0],
        DNA_MAP[1],
        DNA_SCORE,
        -1, 0  # gap open, gap extend
    )
    if '-' in seq1 or '-' in seq2:
        raise RuntimeError('Aligning Sequences with gaps is not supported',
                           seq1, seq2)

    start_seq1 = alignment.contents.align_frag.contents.sa_start
    start_seq2 = alignment.contents.align_frag.contents.sb_start
    frag = alignment[0].align_frag
    align_seq1 = ''
    align_seq2 = ''

    while frag:
        frag = frag[0]

        if frag.type == align.MATCH:
            f1 = seq1[frag.sa_start:frag.sa_start + frag.hsp_len]
            f2 = seq2[frag.sb_start:frag.sb_start + frag.hsp_len]
            align_seq1 += f1
            align_seq2 += f2

        elif frag.type == align.A_GAP:
            align_seq1 += '-' * frag.hsp_len
            align_seq2 += seq2[frag.sb_start:frag.sb_start + frag.hsp_len]

        elif frag.type == align.B_GAP:
            align_seq1 += seq1[frag.sa_start:frag.sa_start + frag.hsp_len]
            align_seq2 += '-' * frag.hsp_len
        frag = frag.next

    assert len(align_seq1) == len(align_seq2)
    align.alignment_free(alignment)
    return align_seq1, align_seq2, start_seq1, start_seq2


def cigar_to_backtrace(seq1, seq2, cigar):
    """
    Converts a cigar sequence into an enrich2 backtrace

    The tuple format is ``(i, j, type, length)``, where ``i`` and ``j``
    are the positions in *seq1* and *seq2*, respectively, and type is one
    of ``"match"``, ``"mismatch"``, ``"insertion"``, or ``"deletion"``.
    For indels, the ``length`` value is the number of bases inserted or
    deleted with respect to *seq1* starting at ``i``.


    Parameters
    ----------
    seq1 :  `str`
        The string used during alignment for ``seq1``
    seq2 : `str`
        The string used during alignment for ``seq2``
    cigar : `str`
        The cigar string expecting characters {'M', 'I', 'D'}

    Returns
    -------
    `list`
        The tuple format is ``(i, j, type, length)``, where ``i`` and ``j``
        are the positions in *seq1* and *seq2*, respectively, and type is one
        of ``"match"``, ``"mismatch"``, ``"insertion"``, or ``"deletion"``.
        For indels, the ``length`` value is the number of bases inserted or
        deleted with respect to *seq1* starting at ``i``.
    """
    letters = cigar[1::2]
    numbers = [int(x) for x in cigar[0::2]]
    backtrace = []
    seq1_pos = 0
    seq2_pos = 0
    for num, char in zip(numbers, letters):
        if char == 'M':
            for i in range(num):
                if seq1[seq1_pos + i] == seq2[seq2_pos + i]:
                    match_str = 'match'
                else:
                    match_str = 'mismatch'
                backtrace.append((seq1_pos + i, seq2_pos + i, match_str, None))
            seq1_pos += num - 1
            seq2_pos += num - 1
        elif char == 'I':
            backtrace.append((seq1_pos, seq2_pos + num, 'insertion', num))
            seq1_pos += 1
            seq2_pos += num + 1
        elif char == 'D':
            backtrace.append((seq1_pos + num, seq2_pos, 'deletion', num))
            seq1_pos += num + 1
            seq2_pos += 1
    return backtrace
