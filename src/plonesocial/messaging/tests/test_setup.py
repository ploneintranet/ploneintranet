# -*- coding: utf-8 -*-
from plone import api
from plonesocial.messaging.testing import \
    PLONESOCIAL_MESSAGING_INTEGRATION_TESTING

import unittest

PROJECTNAME = 'plonesocial.messaging'

JS = [
    '++resource++plonesocial.messaging.messaging.js',
]

CSS = [
    '++resource++plonesocial.messaging.messaging.css',
]


class InstallTestCase(unittest.TestCase):

    layer = PLONESOCIAL_MESSAGING_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_installed(self):
        qi = self.portal['portal_quickinstaller']
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_jsregistry(self):
        resource_ids = self.portal.portal_javascripts.getResourceIds()
        for id in JS:
            self.assertIn(id, resource_ids, '{0} not installed'.format(id))

    def test_cssregistry(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        for id in CSS:
            self.assertIn(id, resource_ids, '{0} not installed'.format(id))

    def test_user_actions(self):
        user_actions = self.portal['portal_actions'].user
        self.assertIn('plone_social_menu', user_actions)


class UninstallTestCase(unittest.TestCase):

    layer = PLONESOCIAL_MESSAGING_INTEGRATION_TESTING

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
