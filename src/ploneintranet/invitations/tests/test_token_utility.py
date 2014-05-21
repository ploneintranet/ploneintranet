import unittest
from zope.component import getUtility
from zope.component import eventtesting
from ploneintranet.invitations.interfaces import ITokenUtility

from ploneintranet.invitations.testing import \
    PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING


class TestTokenUtility(unittest.TestCase):

    layer = PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING

    def setUp(self):
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
        # Also test the event
        eventtesting.setUp()
        self.assertTrue(self.util._consume_token(self.one_time_token))
        self.assertFalse(self.util._consume_token(self.one_time_token))
        events = eventtesting.getEvents()
        # Ensure only one event was fired
        self.assertEqual(len(events), 1)
        event_obj = events[0].object
        # The object for the event should be our one_time_token
        self.assertEqual(event_obj.id, self.one_time_token)
