import unittest
from zope.component import getUtility
from zope.component import eventtesting
from ploneintranet.invitations.interfaces import ITokenUtility
from ploneintranet.invitations.events import ITokenConsumed

from ploneintranet.invitations.testing import \
    PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING
from ploneintranet.invitations.token import Token


class TestTokenUtility(unittest.TestCase):

    layer = PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING

    def setUp(self):
        eventtesting.setUp()
        self.util = getUtility(ITokenUtility)
        self.one_time_token = self.util.generate_new_token(
            usage_limit=1
        )

    def test_generate_new_token(self):
        infinite_token = self.util.generate_new_token()
        short_lived_token = self.util.generate_new_token(
            expire_seconds=10
        )
        self.assertIsInstance(infinite_token, basestring)
        self.assertIsInstance(short_lived_token, basestring)

    def test_valid(self):
        self.assertFalse(self.util.valid('abc123'))
        self.assertTrue(self.util.valid(self.one_time_token))
        self.util._consume_token(self.one_time_token)
        self.assertFalse(self.util.valid(self.one_time_token))

    def test__consume_token(self):
        self.assertTrue(self.util._consume_token(self.one_time_token))
        self.assertFalse(self.util._consume_token(self.one_time_token))
        events = eventtesting.getEvents(ITokenConsumed)
        # Ensure only one event was fired
        self.assertEqual(len(events), 1)
        token_id = events[0].token_id
        # The object for the event should be our one_time_token
        self.assertEqual(token_id, self.one_time_token)

    def test__fetch_token(self):
        self.assertEqual(
            self.util._fetch_token(self.one_time_token).id,
            self.one_time_token
        )
        self.assertIsNone(self.util._fetch_token('abc123'))

    def test__store_token(self):
        token = Token(None, None)
        self.assertIsNone(self.util._store_token(token))

    def test__get_storage(self):
        storage = self.util._get_storage()
        key = 'foo'
        value = 'bar'
        storage[key] = value
        self.assertEqual(
            self.util._get_storage().get(key),
            value
        )
        self.assertIsNone(
            self.util._get_storage(clear=True).get(key)
        )
