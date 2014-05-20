import unittest2 as unittest
from zope.component import getUtility
from ploneintranet.invitations.interfaces import ITokenUtility

from ploneintranet.invitations.testing import \
    PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING


class TestExample(unittest.TestCase):

    layer = PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING

    def setUp(self):
        self.util = getUtility(ITokenUtility)

    def test_get_new_token(self):
        self.fail()

    def test_get_uses(self):
        self.fail()

    def test_get_expiry(self):
        self.fail()

    def test__consume_token(self):
        self.fail()

