from plone import api
from ploneintranet import api as pi_api
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

        # activate the group behaviour on workspacefolder
        fti = queryUtility(
            IDexterityFTI,
            name='ploneintranet.workspace.workspacefolder')
        behaviors = set(fti.behaviors)
        behaviors.add("{0}.{1}".format(
            IMembraneGroup.__module__, IMembraneGroup.__name__))
        fti.behaviors = tuple(behaviors)
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
            'workspace-a'
        )
        self.add_user_to_workspace(
            'johndoe',
            self.workspace_a,
        )

        # Add a second and third workspace, without participants
        self.workspace_b = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'workspace-b'
        )
        self.workspace_c = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'workspace-c'
        )
        self.logout()

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
