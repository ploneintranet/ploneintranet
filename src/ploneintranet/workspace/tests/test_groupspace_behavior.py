from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from plone.dexterity.interfaces import IDexterityFTI
from ploneintranet.workspace.behaviors.group import IMembraneGroup
from Products.membrane.interfaces import IGroup
from zope.component import queryUtility
from AccessControl import Unauthorized


class TestGroupspaceBehavior(BaseTestCase):
    """
    Test the abilities of users within a workspace
    """
    def setUp(self):
        super(TestGroupspaceBehavior, self).setUp()
        fti = queryUtility(
            IDexterityFTI,
            name='ploneintranet.workspace.workspacefolder')
        behaviors = set(fti.behaviors)
        behaviors.add("{0}.{1}".format(
            IMembraneGroup.__module__, IMembraneGroup.__name__))
        fti.behaviors = tuple(behaviors)
        self.login_as_portal_owner()
        # set up some users
        api.user.create(username='wsadmin', email='admin@test.com')
        api.user.create(username='user1', email='test@test.com')
        api.user.create(username='user2', email='test2@test.com')
        self.workspace = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        # add participants to workspace
        self.add_user_to_workspace(
            'wsadmin',
            self.workspace,
            {'Admins'},
        )
        self.add_user_to_workspace(
            'user1',
            self.workspace,
        )

        # Add a second workspace, without participants
        self.workspace_b = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'workspace-b'
        )

        self.logout()

    def traverse_to_item(self, item):
        """ helper method to travers to an item by path """
        return api.content.get(path='/'.join(item.getPhysicalPath()))

    def test_groups_behavior_present(self):
        self.assertTrue(IMembraneGroup.providedBy(self.workspace))

    def test_group_interface_provided(self):
        self.assertTrue(IGroup(self.workspace, None) is not None)

    def test_group_title(self):
        obj = IGroup(self.workspace)
        self.assertEqual(obj.getGroupName(), self.workspace.Title())

    def test_basic_group_membership(self):
        obj = IGroup(self.workspace)
        self.assertEqual(
            set(obj.getGroupMembers()),
            set(['wsadmin', 'user1', 'admin'])
        )

    def test_group_permissions_from_workspace(self):
        self.login('user1')
        # user1 cannot access workspace-b
        with self.assertRaises(Unauthorized):
            self.traverse_to_item(self.workspace_b)
        self.logout()
        self.login_as_portal_owner()
        # the group example-workspace gets added as member to workspace-b
        self.add_user_to_workspace(
            'example-workspace',
            self.workspace_b,
        )
        obj = IGroup(self.workspace_b)
        self.assertEqual(
            set(obj.getGroupMembers()),
            set(['example-workspace', 'admin'])
        )
        self.logout()
        self.login('user1')
        # user1 can now access workspace-b
        self.traverse_to_item(self.workspace_b)
