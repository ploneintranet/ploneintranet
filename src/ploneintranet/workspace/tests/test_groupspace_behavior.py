from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from plone.dexterity.interfaces import IDexterityFTI
from ploneintranet.workspace.behaviors.group import IMembraneGroup
from Products.membrane.interfaces import IGroup
from zope.component import queryUtility


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
        self.add_user_to_workspace(
            'wsadmin',
            self.workspace,
            {'Admins'},
        )
        self.add_user_to_workspace(
            'user1',
            self.workspace,
        )
        self.logout()

    def test_groups_behavior_present(self):
        self.assertTrue(IMembraneGroup.providedBy(self.workspace))

    def test_group_interface_provided(self):
        self.assertTrue(IGroup(self.workspace, None) is not None)
