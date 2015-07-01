# -*- coding: utf-8 -*-
from plone import api
from plone.browserlayer.utils import registered_layers
from ploneintranet.workspace.config import DYNAMIC_GROUPS_PLUGIN_ID
from ploneintranet.workspace.config import INTRANET_USERS_GROUP_ID
from ploneintranet.workspace.interfaces import IPloneintranetWorkspaceLayer
from ploneintranet.workspace.interfaces import IWorkspaceAppContentLayer
from ploneintranet.workspace.testing import \
    PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING
import unittest2 as unittest

PROJECTNAME = 'ploneintranet.workspace'


class TestInstall(unittest.TestCase):

    layer = PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST

    def test_product_installed(self):
        """Test if ploneintranet.workspace is installed."""
        installer = api.portal.get_tool('portal_quickinstaller')
        self.assertTrue(installer.isProductInstalled(PROJECTNAME))

    def test_browserlayer(self):
        """Test that the browserlayer is registered."""
        self.assertIn(IPloneintranetWorkspaceLayer, registered_layers())

    def test_browserlayer_app(self):
        """Test that the app browserlayer is registered."""
        self.assertIn(IWorkspaceAppContentLayer, registered_layers())

    def test_workspaces_created(self):
        workspaces = self.portal.get('workspaces', None)
        if workspaces:
            self.assertEqual(
                workspaces.portal_type,
                'ploneintranet.workspace.workspacecontainer')

    def test_group_created(self):
        self.assertIsNotNone(api.group.get(INTRANET_USERS_GROUP_ID))

    def test_plugin_created(self):
        pas = api.portal.get_tool('acl_users')
        self.assertIn(DYNAMIC_GROUPS_PLUGIN_ID, pas.objectIds())

    def test_actions_installed(self):
        actions = api.portal.get_tool('portal_actions')
        object_actions = actions.get('object')
        self.assertIn('ws_policies', object_actions)


class TestUninstall(unittest.TestCase):
    """Test that ploneintranet.workspace is properly uninstalled."""

    layer = PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts([PROJECTNAME])

    def test_uninstall(self):
        """Test if ploneintranet.workspace is cleanly uninstalled."""
        self.assertFalse(
            self.installer.isProductInstalled(PROJECTNAME))

    def test_indexes_removed(self):
        catalog = api.portal.get_tool('portal_catalog')
        self.assertNotIn('mimetype', catalog.indexes())
        self.assertNotIn('mimetype', catalog.schema())

    def test_types_removed(self):
        portal_types = api.portal.get_tool('portal_types')
        self.assertNotIn(
            'ploneintranet.workspace.workspacefolder', portal_types)
        self.assertNotIn(
            'ploneintranet.workspace.workspacecontainer', portal_types)

    def test_browserlayer_removed(self):
        """Test that IPloneintranetWorkspaceLayer is registered."""
        self.assertNotIn(IPloneintranetWorkspaceLayer, registered_layers())

    def test_browserlayer_app_removed(self):
        """Test that the app browserlayer is unregistered."""
        self.assertNotIn(IWorkspaceAppContentLayer, registered_layers())

    def test_workspaces_not_removed(self):
        """Test that the workspaces folder is kept."""
        self.assertEqual(
            self.portal['workspaces'].portal_type,
            'ploneintranet.workspace.workspacecontainer')

    def test_group_removed(self):
        self.assertIsNone(api.group.get(INTRANET_USERS_GROUP_ID))

    def test_plugin_removed(self):
        pas = api.portal.get_tool('acl_users')
        self.assertNotIn(DYNAMIC_GROUPS_PLUGIN_ID, pas.objectIds())

    def test_roles_removed(self):
        valid_roles = self.portal.valid_roles()
        pas = api.portal.get_tool('acl_users')
        roles = pas.portal_role_manager.listRoleIds()
        for role in ['TeamMember', 'TeamManager', 'SelfPublisher']:
            self.assertNotIn(role, valid_roles)
            self.assertNotIn(role, roles)

    def test_actions_reset(self):
        actions = api.portal.get_tool('portal_actions')
        object_actions = actions.get('object')
        self.assertNotIn('ws_policies', object_actions)
        self.assertEqual(object_actions.local_roles.available_expr, '')
