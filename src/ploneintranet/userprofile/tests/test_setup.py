# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from plone import api
from ploneintranet.userprofile.tests.base import BaseTestCase

PROJECTNAME = 'ploneintranet.userprofile'


class TestInstall(BaseTestCase):
    """Test installation of ploneintranet.userprofile into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ploneintranet.userprofile is installed with portal_quickinstaller.
        """
        self.assertTrue(self.installer.isProductInstalled(
            PROJECTNAME))

    def test_types_installed(self):
        portal_types = api.portal.get_tool('portal_types')
        fti = portal_types.get(
            'ploneintranet.userprofile.userprofile', None)
        self.assertEqual(fti.id, 'ploneintranet.userprofile.userprofile')
        fti = portal_types.get(
            'ploneintranet.userprofile.userprofilecontainer', None)
        self.assertEqual(
            fti.id, 'ploneintranet.userprofile.userprofilecontainer')

    def test_allowed_types_installed(self):
        portal_types = api.portal.get_tool('portal_types')
        fti = portal_types.get('Plone Site', None)
        self.assertIn(
            'ploneintranet.userprofile.userprofilecontainer',
            fti.allowed_content_types)


class TestUninstall(BaseTestCase):
    """Test that ploneintranet.userprofile is properly uninstalled."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['ploneintranet.userprofile'])

    def test_uninstall(self):
        """Test if ploneintranet.userprofile is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            PROJECTNAME))

    def test_types_removed(self):
        portal_types = api.portal.get_tool('portal_types')
        fti = portal_types.get(
            'ploneintranet.userprofile.userprofile', None)
        self.assertIsNone(fti)
        fti = portal_types.get(
            'ploneintranet.userprofile.userprofilecontainer', None)
        self.assertIsNone(fti)

    def test_allowed_types_removed(self):
        portal_types = api.portal.get_tool('portal_types')
        fti = portal_types.get('Plone Site', None)
        self.assertNotIn(
            'ploneintranet.userprofile.userprofilecontainer',
            fti.allowed_content_types)
