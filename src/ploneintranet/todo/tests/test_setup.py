# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from ploneintranet.todo.testing import IntegrationTestCase
from plone import api

PROJECTNAME = 'ploneintranet.todo'


class TestInstall(IntegrationTestCase):
    """Test installation of ploneintranet.todo into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ploneintranet.todo is installed with portal_quickinstaller.
        """
        self.assertTrue(self.installer.isProductInstalled(
            PROJECTNAME))

    def test_type_installed(self):
        portal_types = api.portal.get_tool('portal_types')
        fti = portal_types.get('todo', None)
        self.assertEqual(fti.id, 'todo')


class TestUninstall(IntegrationTestCase):
    """Test that ploneintranet.todo is properly uninstalled."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['ploneintranet.todo'])

    def test_uninstall(self):
        """Test if ploneintranet.todo is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'ploneintranet.todo'))

    def test_type_removed(self):
        portal_types = api.portal.get_tool('portal_types')
        fti = portal_types.get('todo', None)
        self.assertIsNone(fti)

    def test_behavior_removed(self):
        portal_types = api.portal.get_tool('portal_types')
        fti = portal_types.get('News Item', None)
        self.assertNotIn(
            'ploneintranet.todo.behaviors.IMustRead', fti.behaviors)

    def test_roles_removed(self):
        valid_roles = self.portal.valid_roles()
        pas = api.portal.get_tool('acl_users')
        roles = pas.portal_role_manager.listRoleIds()
        for role in ['Assignee']:
            self.assertNotIn(role, valid_roles)
            self.assertNotIn(role, roles)
