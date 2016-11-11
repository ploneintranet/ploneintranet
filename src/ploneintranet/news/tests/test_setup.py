# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.news.testing import IntegrationTestCase

PROJECTNAME = 'ploneintranet.news'


class InstallTestCase(IntegrationTestCase):

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_installed(self):
        qi = self.portal['portal_quickinstaller']
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_app_installed(self):
        self.assertIn('news', self.portal)

    def test_section_installed(self):
        self.assertTrue(len(self.portal.news.sections()) > 0)


class UninstallTestCase(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']

        with api.env.adopt_roles(['Manager']):
            self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_app_removed(self):
        self.assertNotIn('news', self.portal)
