# -*- coding: utf-8 -*-
from json import loads
from plone import api
from ploneintranet import api as pi_api
from ploneintranet.workspace.tests.base import BaseTestCase
from ploneintranet.workspace.behaviors.group import IMembraneGroup
from Products.membrane.interfaces import IGroup
from AccessControl import Unauthorized
from zope.annotation import IAnnotations


class TestGroupspaceBehavior(BaseTestCase):
    """
    Test the abilities of users within a workspace
    """
    def setUp(self):
        super(TestGroupspaceBehavior, self).setUp()

        self.login_as_portal_owner()
        # set up some users
        self.profile1 = pi_api.userprofile.create(
            username='johndoe',
            email='johndoe@doe.com',
            approve=True,
        )
        self.profile2 = pi_api.userprofile.create(
            username='janeschmo',
            email='janeschmo@doe.com',
            approve=True,
        )

        self.workspace_a = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'workspace-a',
            title=u"Workspace A"
        )
        api.content.transition(self.workspace_a, 'make_private')
        self.add_user_to_workspace(
            'johndoe',
            self.workspace_a,
        )

        # Add a second and third workspace, without participants
        self.workspace_b = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'workspace-b',
            title=u"Workspace 𝔅"
        )
        api.content.transition(self.workspace_b, 'make_private')
        self.workspace_c = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'workspace-c',
            title=u"Workspace 𝒞"
        )
        self.logout()

    def logout(self):
        """
        Delete any cached localrole information from the request.
        """
        super(TestGroupspaceBehavior, self).logout()
        annotations = IAnnotations(self.request)
        keys_to_remove = []
        for key in annotations.keys():
            if (
                isinstance(key, basestring) and
                key.startswith('borg.localrole')
            ):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            annotations.pop(key)

    def traverse_to_item(self, item):
        """ helper method to travers to an item by path """
        return api.content.get(path='/'.join(item.getPhysicalPath()))

    def test_groups_behavior_present(self):
        self.assertTrue(IMembraneGroup.providedBy(self.workspace_a))

    def test_group_interface_provided(self):
        self.assertTrue(IGroup(self.workspace_a, None) is not None)

    def test_group_title(self):
        obj = IGroup(self.workspace_a)
        self.assertEqual(obj.getGroupName(), self.workspace_a.Title())

    def test_basic_group_membership(self):
        obj = IGroup(self.workspace_a)
        self.assertEqual(
            set(obj.getGroupMembers()),
            set(['johndoe', 'admin'])
        )

    def test_group_permissions_from_workspace(self):
        """
            Johndoe is member in Workspace A,
            Workspace A is member in Workspace B
                => Johndoe can access Workspace B
        """
        self.login('johndoe')
        # johndoe cannot access workspace-b
        with self.assertRaises(Unauthorized):
            self.traverse_to_item(self.workspace_b)
        self.logout()
        self.login_as_portal_owner()
        # the group workspace-a gets added as member to workspace-b
        self.add_user_to_workspace(
            'workspace-a',
            self.workspace_b,
        )
        obj = IGroup(self.workspace_b)
        self.assertEqual(
            set(obj.getGroupMembers()),
            set(['workspace-a', 'admin'])
        )
        self.logout()
        # johndoe can now access workspace-b
        self.login('johndoe')
        self.traverse_to_item(self.workspace_b)
        self.logout()
        # but janeschmo still cannot
        self.login('janeschmo')
        with self.assertRaises(Unauthorized):
            self.traverse_to_item(self.workspace_b)

    def test_group_permissions_from_workspace_from_workspace(self):
        """
            Johndoe is member in Workspace A,
            Workspace A is member in Workspace B,
            Workspace B is member in Workspace C
                => Johndoe can access Workspace C
        """
        self.login('johndoe')
        # johndoe cannot access workspace-c
        with self.assertRaises(Unauthorized):
            self.traverse_to_item(self.workspace_c)
        self.logout()
        self.login_as_portal_owner()
        # the group workspace-a gets added as member to workspace-b
        self.add_user_to_workspace(
            'workspace-a',
            self.workspace_b,
        )
        obj = IGroup(self.workspace_b)
        self.assertEqual(
            set(obj.getGroupMembers()),
            set(['workspace-a', 'admin'])
        )
        # the group workspace-b gets added as member to workspace-c
        self.add_user_to_workspace(
            'workspace-b',
            self.workspace_c,
        )
        obj = IGroup(self.workspace_c)
        self.assertEqual(
            set(obj.getGroupMembers()),
            set(['workspace-b', 'admin'])
        )
        self.logout()
        # johndoe can now access workspace-c
        self.login('johndoe')

        self.traverse_to_item(self.workspace_c)
        self.logout()
        # but janeschmo still cannot
        self.login('janeschmo')
        with self.assertRaises(Unauthorized):
            self.traverse_to_item(self.workspace_c)

    def test_group_properties_provider(self):
        """
            Makes sure that our MembraneGroupProperties provider gets used
        """
        all_groups = api.group.get_groups()
        ws_groups = [
            group for group in all_groups if
            group.getId().startswith('workspace-')]
        workspace_titles = set([
            group.getProperty('title') for group in ws_groups
        ])
        self.assertEqual(
            workspace_titles,
            set([u'Workspace A', u'Workspace 𝔅', u'Workspace 𝒞'])
        )
        workspace_uids = set([
            group.getProperty('uid') for group in ws_groups
        ])
        self.assertEqual(
            workspace_uids,
            set([
                self.workspace_a.UID(),
                self.workspace_b.UID(),
                self.workspace_c.UID()
            ])
        )

    def test_workspace_members_listing_ignores_secret(self):
        self.login_as_portal_owner()

        json_groups = self.workspace_a.restrictedTraverse('allgroups.json')()
        available_group_ids = [x['id'] for x in loads(json_groups)]
        # The secret workspace C does not get listed
        self.assertTrue('workspace-a' in available_group_ids)
        self.assertTrue('workspace-b' in available_group_ids)
        self.assertFalse('workspace-c' in available_group_ids)

        # Add private workspace B to A
        self.add_user_to_workspace(
            'workspace-b',
            self.workspace_a,
        )
        # Add secret workpace C to A
        self.add_user_to_workspace(
            'workspace-c',
            self.workspace_a,
        )
        existing_users = self.workspace_a.existing_users()
        group_ids = [x['id'] for x in existing_users if x['typ'] == 'group']
        self.assertTrue('workspace-b' in group_ids)
        self.assertFalse('workspace-c' in group_ids)
