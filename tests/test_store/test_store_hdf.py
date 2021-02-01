import unittest

from countess.store.hdf import HdfStore
from tests.test_store.store_interface_tests import create_test_classes


def load_tests(loader, tests, pattern) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    test_classes = create_test_classes(HdfStore)
    for tc in test_classes:
        tc.__module__ = __name__
        tc.__qualname__ = tc.__name__
        tests = loader.loadTestsFromTestCase(tc)
        suite.addTests(tests)
    return suite


if __name__ == "__main__":
    unittest.main()
