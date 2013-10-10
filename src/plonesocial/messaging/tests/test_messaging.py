# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import getToolByName
from plonesocial.messaging.testing import \
    PLONESOCIAL_MESSAGING_INTEGRATION_TESTING
from zope.component import getUtility
from zope.interface.verify import verifyClass

import unittest2 as unittest


class TestMessagingLocator(unittest.TestCase):

    layer = PLONESOCIAL_MESSAGING_INTEGRATION_TESTING

    def setUp(self):
        self.site = self.layer['portal']
        self.tool = getToolByName(self.site, 'plonesocial_messaging')

    def test_messaginglocator_interface(self):
        from plonesocial.messaging.interfaces import IMessagingLocator
        from plonesocial.messaging.messaging import MessagingLocator
        verifyClass(IMessagingLocator, MessagingLocator)

    def test_tool_installed(self):
        from plonesocial.messaging.tool import MessagingTool
        self.assertTrue('plonesocial_messaging' in self.site)

        self.assertTrue(isinstance(self.tool, MessagingTool))

    def test_tool_provides_inboxes(self):
        from plonesocial.messaging.interfaces import IInboxes
        self.assertTrue(IInboxes.providedBy(self.tool))

    def test_messaginglocator(self):
        from plonesocial.messaging.interfaces import IMessagingLocator
        self.assertTrue(getUtility(IMessagingLocator))

    def test_messaginglocator_returns_tool(self):
        from plonesocial.messaging.interfaces import IMessagingLocator
        from plonesocial.messaging.tool import MessagingTool
        locator = getUtility(IMessagingLocator)
        tool = locator.get_inboxes()
        self.assertTrue(isinstance(tool, MessagingTool))
