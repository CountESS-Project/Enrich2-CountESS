import unittest

from enrich2.base.store_interface import HDFStore
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

# overwrite the test case's source module so it reports this file in unittest output
for test_case in (
    TestStore,
    TestStoreAppend,
    TestStoreCheckKeyExists,
    TestStoreFileOps,
    TestStoreGetKey,
    TestStoreMetadata,
    TestStorePut,
    TestStoreRemove,
    TestStoreSelect,
):
    test_case.__module__ = "enrich2.tests.test_hdfstore"


def load_tests(loader, tests, pattern) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    for test_case in (
        TestStore,
        TestStoreAppend,
        TestStoreCheckKeyExists,
        TestStoreFileOps,
        TestStoreGetKey,
        TestStoreMetadata,
        TestStorePut,
        TestStoreRemove,
        TestStoreSelect,
    ):
        tests = loader.loadTestsFromTestCase(test_case)
        suite.addTests(tests)
    return suite


if __name__ == "__main__":
    unittest.main()
