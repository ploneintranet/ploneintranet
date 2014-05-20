import unittest
from datetime import datetime, timedelta

from ploneintranet.invitations.testing import \
    PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING
from ploneintranet.invitations.token import Token


class TestToken(unittest.TestCase):

    layer = PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING

    def test_create_token(self):
        expiry = datetime.now() + timedelta(seconds=300)
        token = Token(1, expiry)
        self.assertEqual(token.uses, 1)
        self.assertEqual(token.expiry, expiry)
        self.assertIsInstance(token.id, basestring)
