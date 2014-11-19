# -*- coding: utf-8 -*-

from plone import api
from ploneintranet.notifications.interfaces import INotificationsQueues
from ploneintranet.notifications.interfaces import INotificationsTool
from ploneintranet.notifications.testing import \
    PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING
from zope.component import queryUtility
import unittest2 as unittest


class TestNetworkTool(unittest.TestCase):

    layer = PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_tool_available(self):
        tool = queryUtility(INotificationsTool)
        self.assertTrue(INotificationsQueues.providedBy(tool))

    def test_tool_uninstalled(self):
        qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=['ploneintranet.notifications'])
        self.assertNotIn('ploneintranet_notifications', self.portal)
        tool = queryUtility(INotificationsTool, None)
        self.assertIsNone(tool)
