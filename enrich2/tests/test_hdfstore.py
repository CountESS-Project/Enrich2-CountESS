import unittest

from enrich2.store.interface import HDFStore
import enrich2.tests.config as config

config.StoreInterfaceBeingTested = HDFStore
from enrich2.tests.store_interface_tests import (
    TestStore,
    TestStoreAppend,
    TestStoreCheckKeyExists,
    TestStoreFileOps,
    TestStoreGetKey,
    TestStoreMetadata,
    TestStorePut,
    TestStoreRemove,
    TestStoreSelect,
)

# create a list of all the imported test cases
test_cases = [
    TestStore,
    TestStoreAppend,
    TestStoreCheckKeyExists,
    TestStoreFileOps,
    TestStoreGetKey,
    TestStoreMetadata,
    TestStorePut,
    TestStoreRemove,
    TestStoreSelect,
]

# overwrite the test case's source module so it reports this file in unittest output
for tc in test_cases:
    tc.__module__ = "enrich2.tests.test_hdfstore"


def load_tests(loader, tests, pattern) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    for tc in test_cases:
        tests = loader.loadTestsFromTestCase(tc)
        suite.addTests(tests)
    return suite


if __name__ == "__main__":
    unittest.main()
