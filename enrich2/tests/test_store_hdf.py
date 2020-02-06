import unittest

from enrich2.store.hdf import HdfStore
import enrich2.tests.config as config

config.StoreInterfaceBeingTested = HdfStore
from enrich2.tests.store_interface_tests import (
    TestStorePath,
    TestStorePut,
    TestStoreDrop,
    TestStoreGet,
    TestStoreMetadata,
)

# create a list of all the imported test cases
test_cases = [
    TestStorePath,
    TestStorePut,
    TestStoreDrop,
    TestStoreGet,
    TestStoreMetadata,
]

# overwrite the test case's source module so it reports this file in unittest output
for tc in test_cases:
    tc.__module__ = "enrich2.tests.test_store_hdf"


def load_tests(loader, tests, pattern) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    for tc in test_cases:
        tests = loader.loadTestsFromTestCase(tc)
        suite.addTests(tests)
    return suite


if __name__ == "__main__":
    unittest.main()
