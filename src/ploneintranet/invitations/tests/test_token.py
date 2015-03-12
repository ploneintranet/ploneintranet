import unittest
from datetime import datetime, timedelta

from ploneintranet.invitations.testing import \
    PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING
from ploneintranet.invitations.token import Token


class TestToken(unittest.TestCase):

    layer = PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_create_token(self):
        expiry = datetime.now() + timedelta(seconds=300)
        token = Token(1, expiry, 'a/b/c')
        self.assertEqual(token.uses_remaining, 1)
        self.assertEqual(token.expiry, expiry)
        self.assertIsInstance(token.id, basestring)
        url = '%s/@@accept-token/%s' % (
            self.portal.absolute_url(),
            token.id,
        )
        self.assertEqual(
            token.invite_url,
            url
        )
        self.assertEqual(token.redirect_path, 'a/b/c')
