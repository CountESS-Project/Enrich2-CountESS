import unittest

from enrich2.store.parquet import ParquetStore
import tests.test_store.config as config

config.StoreInterfaceBeingTested = ParquetStore

from tests.test_store.store_interface_tests import *

test_cases = [globals()[x] for x in globals().keys() if x.startswith("TestStore")]

# overwrite the test case's source module so it reports this file in unittest output
for tc in test_cases:
    tc.__module__ = __name__


def load_tests(loader, tests, pattern) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    for tc in test_cases:
        tests = loader.loadTestsFromTestCase(tc)
        suite.addTests(tests)
    return suite


if __name__ == "__main__":
    unittest.main()
