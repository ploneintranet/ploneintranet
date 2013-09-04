# -*- coding: UTF-8 -*-
import unittest2 as unittest

from zope.component import getUtility

from plonesocial.messaging.testing import \
    PLONESOCIAL_MESSAGING_INTEGRATION_TESTING


class TestMessagingLocator(unittest.TestCase):

    layer = PLONESOCIAL_MESSAGING_INTEGRATION_TESTING

    def test_messaginglocator(self):
        from plonesocial.messaging.interfaces import IMessagingLocator
        self.assertTrue(getUtility(IMessagingLocator))
