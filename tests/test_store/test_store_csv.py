import unittest

from countess.store.csv import CsvStore
from tests.test_store.store_interface_tests import create_test_classes


def load_tests(loader, tests, pattern) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    test_classes = create_test_classes(CsvStore)
    for tc in test_classes:
        tc.__module__ = __name__
        tc.__qualname__ = tc.__name__
        tests = loader.loadTestsFromTestCase(tc)
        suite.addTests(tests)
    return suite


if __name__ == "__main__":
    unittest.main()
