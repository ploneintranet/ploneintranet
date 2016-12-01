# coding=utf-8
from collective.workspace.interfaces import IWorkspace
from plone import api
from ploneintranet import api as pi_api
from ploneintranet.workspace.testing import PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING  # noqa
from Products.membrane.interfaces import IGroup
from unittest import TestCase


class TestWorkspaceWorkgroups(TestCase):

    layer = PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.workspace = api.content.create(
            container=self.portal.workspaces,
            id='testws',
            type='ploneintranet.workspace.workspacefolder',
        )
        self.workgroup = api.content.create(
            container=self.portal.workspaces,
            type='ploneintranet.userprofile.workgroup',
            canonical='Test workgroup',
            title='Test workgroup',
            description='',
            members=['johndoe@doe.com'],
            mail='testworkgroup@example.com',
        )
        self.userprofile = pi_api.userprofile.create(
            username='johndoe@doe.com',
            email='johndoe@doe.com',
        )
        IWorkspace(self.workspace).add_to_team(self.workgroup.canonical)

    def test_workgroup_security(self):
        ''' Check if that a workgroup assigned to a workspace allows his
        members to see the workspace
        '''
        group = IGroup(self.workspace)
        self.assertSetEqual(
            set(group.getGroupMembers()),
            {'test_user_1_', 'Test workgroup'},
        )
        self.assertTrue(
            api.user.has_permission(
                'View',
                user=self.userprofile,
                obj=self.workspace
            )
        )
