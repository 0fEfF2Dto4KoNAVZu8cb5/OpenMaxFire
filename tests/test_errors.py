import unittest

import openmaxfire
from openmaxfire.errors import (
    CapabilityUnavailableError,
    LoaderUnavailableError,
    OpenMaxFireError,
)


class ErrorTaxonomyTests(unittest.TestCase):
    def test_public_errors_share_one_catchable_base(self):
        self.assertTrue(issubclass(CapabilityUnavailableError, OpenMaxFireError))
        self.assertTrue(issubclass(LoaderUnavailableError, CapabilityUnavailableError))
        self.assertIs(openmaxfire.OpenMaxFireError, OpenMaxFireError)


if __name__ == "__main__":
    unittest.main()
