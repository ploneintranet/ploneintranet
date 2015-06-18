# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IResourceRegistry
from plone import api
from plone.registry.interfaces import IRegistry
from ploneintranet.messaging.testing import \
    PLONEINTRANET_MESSAGING_INTEGRATION_TESTING
from zope.component import getUtility

import unittest

PROJECTNAME = 'ploneintranet.messaging'

JS = [
    ('plone.resources/resource-ploneintranet-messaging-messaging-js.js',
     '++resource++ploneintranet.messaging.messaging.js'),
]

CSS = [
    ('plone.resources/resource-ploneintranet-messaging-messaging-css.css',
     '++resource++ploneintranet.messaging.messaging.css'),
]


class InstallTestCase(unittest.TestCase):

    layer = PLONEINTRANET_MESSAGING_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_installed(self):
        qi = self.portal['portal_quickinstaller']
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_registry(self):
        records = self.portal.portal_registry.records
        msg = '{0} not installed'
        for (key, id) in JS:
            self.assertIn(key, records, msg.format(id))
            self.assertIn(id, records[key].value, msg.format(id))

    def test_cssregistry(self):
        records = self.portal.portal_registry.records
        msg = '{0} not installed'
        for (key, id) in CSS:
            self.assertIn(key, records, msg.format(id))
            self.assertIn(id, records[key].value, msg.format(id))

    def test_user_actions(self):
        user_actions = self.portal['portal_actions'].user
        self.assertIn('plone_social_menu', user_actions)

    def test_tool_installed(self):
        self.assertIn('ploneintranet_messaging', self.portal)


class UninstallTestCase(unittest.TestCase):

    layer = PLONEINTRANET_MESSAGING_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']

        with api.env.adopt_roles(['Manager']):
            self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_jsregistry_removed(self):
        resource_ids = self.portal.portal_javascripts.getResourceIds()
        for id in JS:
            self.assertNotIn(id, resource_ids, '{0} not removed'.format(id))

    def test_cssregistry_removed(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        for id in CSS:
            self.assertNotIn(id, resource_ids, '{0} not removed'.format(id))

    def test_user_actions_removed(self):
        user_actions = self.portal['portal_actions'].user
        self.assertNotIn('plone_social_menu', user_actions)

    def test_tool_removed(self):
        self.assertNotIn('ploneintranet_messaging', self.portal)

    def test_resources_removed(self):
        bundles = getUtility(IRegistry).collectionOfInterface(
            IResourceRegistry, prefix="plone.resources")
        self.assertNotIn(
            'resource-ploneintranet-messaging-messaging-css', bundles)
        self.assertNotIn(
            'resource-ploneintranet-messaging-messaging-js', bundles)
