import unittest
from ploneintranet.simplesharing.testing import PLONEINTRANET_SIMPLESHARING_INTEGRATION_TESTING


class BaseTestCase(unittest.TestCase):

    layer = PLONEINTRANET_SIMPLESHARING_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST
