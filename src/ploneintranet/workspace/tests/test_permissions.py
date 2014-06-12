from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from AccessControl import Unauthorized


class TestPermissions(BaseTestCase):
    """
    Test the abilities of users within a workspace
    """
    def setUp(self):
        super(TestPermissions, self).setUp()
        self.login_as_portal_owner()
        # set up some users
        api.user.create(username='wsadmin', email="admin@test.com")
        api.user.create(username='user1', email="test@test.com")
        api.user.create(username='user2', email="test2@test.com")
        self.workspace = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
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

    def traverse_to_item(self, item):
        """ helper method to travers to an item by path """
        return api.content.get(path='/'.join(item.getPhysicalPath()))

    def test_consumers_can_view(self):
        """ Consumers can only view published content in the workspace """
        self.login_as_portal_owner()
        self.workspace.participant_policy = "Consumers"
        doc_private = api.content.create(
            self.workspace,
            'Document',
            'test-page',
        )
        doc_published = api.content.create(
            self.workspace,
            'Document',
            'test-page-2',
        )
        api.content.transition(doc_published, to_state='published')

        # Should not be able to view this doc
        self.login('user1')
        with self.assertRaises(Unauthorized):
            self.traverse_to_item(doc_private)
        # Published doc is OK
        self.traverse_to_item(doc_published)
