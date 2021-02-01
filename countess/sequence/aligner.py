"""
Enrich2 aligner module
======================
Module for alignment of variants to the wild type sequence.

This module is optional, and using it will dramatically increase runtime when
counting variants. It is only recommended for users who need to count
insertion and deletion variants (i.e. not coding sequences).
"""

from ctypes import c_int
import numpy as np
import logging

from ..base.utils import log_message


_AMBIVERT = False
try:
    from ambivert.ambivert import gapped_alignment_to_cigar
    from ambivert import align

    # Reset the logging handlers after loading ambivert
    for handler in logging.getLogger("ambivert").handlers:
        handler.close()
    logging.getLogger("ambivert").handlers = []
    for handler in logging.getLogger().handlers:
        handler.close()
    logging.getLogger().handlers = []
    logging.captureWarnings(False)
    _AMBIVERT = True
except ImportError:
    pass


__all__ = ["Aligner"]


#: Default similarity matrix used by the aligner.
#: User-defined matrices must have this format.
_simple_similarity = {
    "A": {"A": 1, "C": -1, "G": -1, "T": -1, "N": 0, "X": 0},
    "C": {"A": -1, "C": 1, "G": -1, "T": -1, "N": 0, "X": 0},
    "G": {"A": -1, "C": -1, "G": 1, "T": -1, "N": 0, "X": 0},
    "T": {"A": -1, "C": -1, "G": -1, "T": 1, "N": 0, "X": 0},
    "N": {"A": 0, "C": 0, "G": 0, "T": 0, "N": 0, "X": 0},
    "X": {"A": 0, "C": 0, "G": 0, "T": 0, "N": 0, "X": 0},
    "gap_open": -1,
    "gap_extend": 0,
}


class Aligner(object):
    """
    Class for performing local alignment of two DNA sequences.

    This class implements `Needleman-Wunsch <http://en.wikipedia.org/wiki/
    Needleman%E2%80%93Wunsch_algorithm>`_ local alignment.

    The :py:class:`~enrich2.sequence.aligner.Aligner` requires a scoring matrix 
    when created. The format is a nested dictionary, with a special ``'gap_open'`` 
    entry for the gap_open penalty (this value is used for both gap_open opening and gap_open
    extension).

    The ``'X'`` nucleotide is a special case for unresolvable mismatches in
    :py:class:`~enrich2.libraries.overlap.OverlapSeqLib` variant data.
    
    Parameters
    ----------
    similarity : `dict`
        Similarity matrix used by the aligner, must contain a cost mapping 
        between each of 'A', 'C', 'G', 'T', 'N', 'X'.
    backend : {'ambivert', 'enrich2'}, default: 'ambivert'
        Select the alignment backend. If backend is 'ambivert' then
        similarity is ignored. 
            
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

    _MAT = 1  # match
    _INS = 2  # insertion (with respect to wild type)
    _DEL = 3  # deletion (with respect to wild type)
    _END = 4  # end of traceback

    def __init__(self, similarity=_simple_similarity, backend="ambivert"):
        similarity_keys = list(similarity.keys())
        if "gap_open" in similarity_keys:
            similarity_keys.remove("gap_open")
        if "gap_extend" in similarity_keys:
            similarity_keys.remove("gap_extend")

        for key in similarity_keys:
            keys_map_to_dicts = all(x in similarity[key] for x in similarity_keys)
            symmetrical = len(similarity[key]) != len(similarity_keys)
            if not keys_map_to_dicts or symmetrical:
                raise ValueError("Asymmetrical alignment scoring matrix")

        self.similarity = similarity
        if "gap_open" not in self.similarity:
            raise ValueError("No gap_open open penalty in alignment scoring matrix.")
        if "gap_extend" not in self.similarity:
            raise ValueError("No gap_open extend penalty in alignment scoring matrix.")

        self.matrix = None
        self.seq1 = None
        self.seq2 = None
        self.calls = 0

        # TODO: uncomment aligner backend
        # global _AMBIVERT
        # if backend == 'ambivert' and _AMBIVERT:
        #     self.align = self.align_ambivert
        #     log_message(
        #         logging_callback=logging.info,
        #         msg="Using ambivert alignment backend.",
        #         extra={'oname': 'Aligner'}
        #     )
        # else:
        #     self.align = self.align_enrich2
        #     log_message(
        #         logging_callback=logging.info,
        #         msg="Using enrich2 alignment backend.",
        #         extra={'oname': 'Aligner'}
        #     )

        self.align = self.align_enrich2
        log_message(
            logging_callback=logging.info,
            msg="Using enrich2 alignment backend.",
            extra={"oname": "Aligner"},
        )

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
            dtype=np.dtype([("score", np.int), ("trace", np.byte)]),
        )
        seq1 = seq1.upper()
        seq2 = seq2.upper()

        a1, a2, *_ = self.needleman_wunsch(
            seq1,
            seq2,
            gap_open=self.similarity["gap_open"],
            gap_extend=self.similarity["gap_extend"],
        )
        backtrace = cigar_to_backtrace(seq1, seq2, gapped_alignment_to_cigar(a1, a2)[0])
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
            dtype=np.dtype([("score", np.int), ("trace", np.byte)]),
        )
        seq1 = seq1.upper()
        seq2 = seq2.upper()

        # build matrix of scores/traceback information
        for i in range(len(seq1) + 1):
            self.matrix[i, 0] = (self.similarity["gap_open"] * i, Aligner._DEL)
        for j in range(len(seq2) + 1):
            self.matrix[0, j] = (self.similarity["gap_open"] * j, Aligner._INS)
        for i in range(1, len(seq1) + 1):
            for j in range(1, len(seq2) + 1):
                match = (
                    self.matrix[i - 1, j - 1]["score"]
                    + self.similarity[seq1[i - 1]][seq2[j - 1]],
                    Aligner._MAT,
                )
                delete = (
                    self.matrix[i - 1, j]["score"] + self.similarity["gap_open"],
                    Aligner._DEL,
                )
                insert = (
                    self.matrix[i, j - 1]["score"] + self.similarity["gap_open"],
                    Aligner._INS,
                )

                # traces = [delete, insert, match]
                # max_score = max(delete, insert, match, key=lambda x: x[0])[0]
                # possible_traces = [t for t in traces if t[0] == max_score]
                # priority_move = sorted(possible_traces, key=lambda x: x[1])[0]
                # self.matrix[i, j] = priority_move

                # def dotype(lol):
                #     if lol == self._MAT:
                #         return 'match'
                #     if lol == self._INS:
                #         return 'insertion'
                #     if lol == self._DEL:
                #         return 'deletion'
                # print(i, j)
                # print("Possible Scores: {}".format([t[0] for t in possible_traces]))
                # print("Possible Tracebacks: {}".format([dotype(t[1]) for t in possible_traces]))
                # print("Chosen Traceback: {}".format(dotype(priority_move[1])))

                max_score = max(delete, insert, match, key=lambda x: x[0])
                self.matrix[i, j] = max_score

        self.matrix[0, 0] = (0, Aligner._END)

        # calculate alignment from the traceback
        i = len(seq1)
        j = len(seq2)
        traceback = list()
        while i > 0 or j > 0:
            if self.matrix[i, j]["trace"] == Aligner._MAT:
                if seq1[i - 1] == seq2[j - 1]:
                    traceback.append((i - 1, j - 1, "match", None))
                else:
                    traceback.append((i - 1, j - 1, "mismatch", None))
                i -= 1
                j -= 1
            elif self.matrix[i, j]["trace"] == Aligner._INS:
                pos_1 = 0 if (i - 1) < 0 else (i - 1)
                traceback.append((pos_1, j - 1, "insertion", 1))
                j -= 1
            elif self.matrix[i, j]["trace"] == Aligner._DEL:
                pos_2 = 0 if (j - 1) < 0 else (j - 1)
                traceback.append((i - 1, pos_2, "deletion", 1))
                i -= 1
            elif self.matrix[i, j]["trace"] == Aligner._END:
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
                        raise RuntimeError(
                            "Aligner failed to combine indels. "
                            "Check 'gap_open' penalty."
                        )
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

    def needleman_wunsch(self, seq1, seq2, gap_open=-1, gap_extend=0):
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
        gap_open : `int`
            Cost for a gap_open open.
        gap_extend : `int`
            Cost for a gap_open extension.
    
        Returns
        -------
        `tuple`
            A tuple containing aligned seq1, aligned seq2, start position
            in seq1 and start position in seq2
        """
        DNA_MAP = align.align_ctypes.make_map("ACGTNX", "N", True)
        DNA_SCORE = make_dna_scoring_matrix(self.similarity)

        alignment = align.global_align(
            bytes(seq1, "ascii"),
            len(seq1),
            bytes(seq2.upper(), "ascii"),
            len(seq2),
            DNA_MAP[0],
            DNA_MAP[1],
            DNA_SCORE,
            gap_open,
            gap_extend,
        )

        if "-" in seq1 or "-" in seq2:
            raise RuntimeError(
                "Aligning Sequences with gaps is not supported", seq1, seq2
            )
        start_seq1 = 0
        start_seq2 = 0
        frag = alignment[0].align_frag
        align_seq1 = ""
        align_seq2 = ""

        while frag:
            frag = frag[0]

            if frag.type == align.MATCH:
                f1 = seq1[frag.sa_start : frag.sa_start + frag.hsp_len]
                f2 = seq2[frag.sb_start : frag.sb_start + frag.hsp_len]
                align_seq1 += f1
                align_seq2 += f2

            elif frag.type == align.A_GAP:
                align_seq1 += "-" * frag.hsp_len
                align_seq2 += seq2[frag.sb_start : frag.sb_start + frag.hsp_len]

            elif frag.type == align.B_GAP:
                align_seq1 += seq1[frag.sa_start : frag.sa_start + frag.hsp_len]
                align_seq2 += "-" * frag.hsp_len

            frag = frag.next

        assert len(align_seq1) == len(align_seq2)
        align.alignment_free(alignment)
        return align_seq1, align_seq2, start_seq1, start_seq2

    def smith_waterman(self, seq1, seq2, gap_open=-1, gap_extend=0):
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
        gap_open : `int`
            Cost for a gap_open open.
        gap_extend : `int`
            Cost for a gap_open extension.
    
        Returns
        -------
        `tuple`
            A tuple containing aligned seq1, aligned seq2, start position
            in seq1 and start position in seq2
        """
        DNA_MAP = align.align_ctypes.make_map("ACGTNX", "N", True)
        DNA_SCORE = make_dna_scoring_matrix(self.similarity)

        alignment = align.local_align(
            bytes(seq1, "ascii"),
            len(seq1),
            bytes(seq2.upper(), "ascii"),
            len(seq2),
            DNA_MAP[0],
            DNA_MAP[1],
            DNA_SCORE,
            gap_open,
            gap_extend,
        )
        if "-" in seq1 or "-" in seq2:
            raise RuntimeError(
                "Aligning Sequences with gaps is not supported", seq1, seq2
            )

        start_seq1 = alignment.contents.align_frag.contents.sa_start
        start_seq2 = alignment.contents.align_frag.contents.sb_start
        frag = alignment[0].align_frag
        align_seq1 = ""
        align_seq2 = ""

        while frag:
            frag = frag[0]

            if frag.type == align.MATCH:
                f1 = seq1[frag.sa_start : frag.sa_start + frag.hsp_len]
                f2 = seq2[frag.sb_start : frag.sb_start + frag.hsp_len]
                align_seq1 += f1
                align_seq2 += f2

            elif frag.type == align.A_GAP:
                align_seq1 += "-" * frag.hsp_len
                align_seq2 += seq2[frag.sb_start : frag.sb_start + frag.hsp_len]

            elif frag.type == align.B_GAP:
                align_seq1 += seq1[frag.sa_start : frag.sa_start + frag.hsp_len]
                align_seq2 += "-" * frag.hsp_len
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
    i = len(seq1)
    j = len(seq2)
    traceback = []
    for num, char in reversed(list(zip(numbers, letters))):
        if char == "M":
            for _ in range(num):
                if seq1[i - 1] == seq2[j - 1]:
                    traceback.append((i - 1, j - 1, "match", None))
                else:
                    traceback.append((i - 1, j - 1, "mismatch", None))
                i -= 1
                j -= 1
        elif char == "I":
            pos_1 = 0 if (i - 1) < 0 else (i - 1)
            traceback.append((pos_1, j - num, "insertion", num))
            j -= num
        elif char == "D":
            pos_2 = 0 if (j - 1) < 0 else (j - 1)
            traceback.append((i - num, pos_2, "deletion", num))
            i -= num
        else:
            raise RuntimeError("Invalid value in alignment traceback.")
    traceback.reverse()
    return traceback


def make_dna_scoring_matrix(similarity, ordering="ACGTNX"):
    """
    Make a ctype DNA scoring matrix for alignment.
    
    Parameters
    ----------
    similarity : `dict`
        Similarity matrix used by the aligner, must contain a cost mapping 
        between each of 'A', 'C', 'G', 'T', 'N', 'X'.
    ordering : `str`
        String representing the key order the dictionary should be 
        traversed to build the square similarity matrix.

    Returns
    -------
    `list`
        Matrix in single list format.

    """
    similarity_matrix = []
    n = len(ordering)
    for key_fr in ordering:
        for key_to in ordering:
            cost = similarity[key_fr][key_to]
            similarity_matrix.append(cost)
    return (c_int * (n * n))(*similarity_matrix)


def test(seq1, seq2):
    from countess.sequence.aligner import Aligner

    amb = Aligner(backend="ambivert")
    aen = Aligner(backend="enrich2")
    print("Enrich2: {}".format(aen.align(seq1, seq2)))
    print("AmBiVert: {}".format(amb.align(seq1, seq2)))


def build_aligners():
    from countess.sequence.aligner import Aligner

    amb = Aligner(backend="ambivert")
    aen = Aligner(backend="enrich2")
    return amb, aen
