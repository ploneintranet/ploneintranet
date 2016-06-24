# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.messaging.testing import IntegrationTestCase

PROJECTNAME = 'ploneintranet.messaging'


class InstallTestCase(IntegrationTestCase):

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_installed(self):
        qi = self.portal['portal_quickinstaller']
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_user_actions(self):
        user_actions = self.portal['portal_actions'].user
        self.assertIn('plone_social_menu', user_actions)

    def test_tool_installed(self):
        self.assertIn('ploneintranet_messaging', self.portal)


class UninstallTestCase(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']

        with api.env.adopt_roles(['Manager']):
            self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_user_actions_removed(self):
        user_actions = self.portal['portal_actions'].user
        self.assertNotIn('plone_social_menu', user_actions)

    def test_tool_removed(self):
        self.assertNotIn('ploneintranet_messaging', self.portal)
