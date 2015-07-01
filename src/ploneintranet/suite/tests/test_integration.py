import unittest2 as unittest
from ploneintranet.suite.testing import PLONEINTRANET_SUITE_INTEGRATION


class TestTestFixture(unittest.TestCase):
    """
    Exercise the testing setup only.
    Handy if you're debugging the setup:
    bin/test -s ploneintranet.suite -t integration -D
    """

    layer = PLONEINTRANET_SUITE_INTEGRATION

    def test_integration(self):
        self.assertTrue(True)
