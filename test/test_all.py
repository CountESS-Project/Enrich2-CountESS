#  Copyright 2016 Alan F Rubin
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


import unittest
import test.test_dataframe as test_dataframe
import test.test_variant as test_variant
import test.test_seqlib_counts as test_seqlib_counts
import test.test_coding_selection as test_coding_selection
import test.test_noncoding_selection as test_noncoding_selection


def suite():
    suite = unittest.TestSuite()
    suite.addTest(test_variant.suite())
    suite.addTest(test_dataframe.suite())
    suite.addTest(test_seqlib_counts.suite())
    suite.addTest(test_coding_selection.suite())
    suite.addTest(test_noncoding_selection.suite())
    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
