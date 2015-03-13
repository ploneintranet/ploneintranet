# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.messaging.testing import PLONEINTRANET_MESSAGING_INTEGRATION_TESTING  # noqa
from zope.component import getUtility
from zope.interface.verify import verifyClass

import unittest


class TestMessagingLocator(unittest.TestCase):

    layer = PLONEINTRANET_MESSAGING_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.tool = api.portal.get_tool('ploneintranet_messaging')

    def test_messaginglocator_interface(self):
        from ploneintranet.messaging.interfaces import IMessagingLocator
        from ploneintranet.messaging.messaging import MessagingLocator
        verifyClass(IMessagingLocator, MessagingLocator)

    def test_tool_installed(self):
        from ploneintranet.messaging.tool import MessagingTool
        self.assertIn('ploneintranet_messaging', self.portal)
        self.assertTrue(isinstance(self.tool, MessagingTool))

    def test_tool_removed(self):
        self.qi = self.portal['portal_quickinstaller']
        PROJECTNAME = 'ploneintranet.messaging'
        with api.env.adopt_roles(['Manager']):
            self.qi.uninstallProducts(products=[PROJECTNAME])
        self.assertNotIn('ploneintranet_messaging', self.portal)

    def test_tool_provides_inboxes(self):
        from ploneintranet.messaging.interfaces import IInboxes
        self.assertTrue(IInboxes.providedBy(self.tool))

    def test_messaginglocator(self):
        from ploneintranet.messaging.interfaces import IMessagingLocator
        self.assertTrue(getUtility(IMessagingLocator))

    def test_messaginglocator_returns_tool(self):
        from ploneintranet.messaging.interfaces import IMessagingLocator
        from ploneintranet.messaging.tool import MessagingTool
        locator = getUtility(IMessagingLocator)
        tool = locator.get_inboxes()
        self.assertTrue(isinstance(tool, MessagingTool))
