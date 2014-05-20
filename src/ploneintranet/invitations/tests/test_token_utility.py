import unittest
from zope.component import getUtility
from ploneintranet.invitations.interfaces import ITokenUtility

from ploneintranet.invitations.testing import \
    PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING


class TestExample(unittest.TestCase):

    layer = PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING

    def setUp(self):
        self.util = getUtility(ITokenUtility)
        self.token1 = self.util.get_new_token()

    def test_get_new_token(self):
        self.assertIsInstance(self.token1, basestring)

    def test_get_uses(self):
        self.assertEqual(self.util.get_uses(self.token1), 1)
        self.util._consume_token(self.token1)
        self.assertIsNone(self.util.get_uses(self.token1))
        token2 = self.util.get_new_token(uses=2)
        self.assertEqual(self.util.get_uses(token2), 2)

    def test_get_expiry(self):
        self.assertEqual(self.util.get_expiry(self.token1), 300)
        self.util._consume_token(self.token1)
        self.assertIsNone(self.util.get_expiry(self.token1))
        token2 = self.util.get_new_token(expiry=20)
        self.assertEqual(self.util.get_expiry(token2), 20)

    def test__consume_token(self):
        self.assertTrue(self.util._consume_token(self.token1))
        self.assertFalse(self.util._consume_token(self.token1))
