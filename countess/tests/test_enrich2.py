import unittest
import cProfile, pstats
from io import StringIO

# pr = cProfile.Profile()
#
# pr.enable()

loader = unittest.TestLoader()
tests = loader.discover(start_dir="./", pattern="test_*.py")
test_runner = unittest.TextTestRunner()
test_runner.run(tests)

# pr.disable()
#
# s = StringIO()
# sortby = 'cumulative'
# ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
# ps.print_stats()
# print(s.getvalue())
