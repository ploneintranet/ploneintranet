from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from plone.api.exc import InvalidParameterError
from AccessControl import Unauthorized


class TestPermissions(BaseTestCase):
    """
    Test the abilities of users within a workspace
    """
    def setUp(self):
        super(TestPermissions, self).setUp()
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

    def traverse_to_item(self, item):
        """ helper method to travers to an item by path """
        return api.content.get(path='/'.join(item.getPhysicalPath()))

    def test_consumers_can_view(self):
        """ Consumers can only view published content in the workspace """
        self.login_as_portal_owner()
        self.workspace.participant_policy = 'consumers'
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

    def test_consumers_cannot_add(self):
        """Consumers cannot add content to the workspace"""
        self.login_as_portal_owner()
        self.workspace.participant_policy = 'consumers'
        self.login('user1')
        with self.assertRaises(Unauthorized):
            api.content.create(
                self.workspace,
                'Document',
                'my-test-page',
            )

    def test_consumers_cannot_add_after_change(self):
        """Consumers cannot add content to the workspace"""
        self.login_as_portal_owner()
        self.workspace.participant_policy = 'producers'
        self.workspace.participant_policy = 'consumers'
        self.login('user1')
        with self.assertRaises(Unauthorized):
            api.content.create(
                self.workspace,
                'Document',
                'my-test-page',
            )

    def test_producers_can_add(self):
        """
        Producers can add content to the workspace, and
        submit it for review
        """
        self.login_as_portal_owner()
        self.workspace.participant_policy = 'Producers'

        self.login('user1')
        doc = api.content.create(
            self.workspace,
            'Document',
            'my-test-page',
        )
        api.content.transition(doc, transition='submit')
        # We cannot publish our own content
        with self.assertRaises(InvalidParameterError):
            api.content.transition(doc, transition='publish')

        # But an admin can
        self.login('wsadmin')
        api.content.transition(doc, transition='publish')

    def test_publishers_can_publish(self):
        """
        Publishers can add and publish their own content
        """
        self.login_as_portal_owner()
        admin_doc = api.content.create(
            self.workspace,
            'Document',
            'my-admin-page',
        )
        self.workspace.participant_policy = 'Publishers'

        self.login('user1')
        doc = api.content.create(
            self.workspace,
            'Document',
            'my-test-page',
        )
        # Can publish my own content
        api.content.transition(doc, transition='submit')
        api.content.transition(doc, transition='publish')

        # We cannot view or publish someone else's content
        with self.assertRaises(Unauthorized):
            self.traverse_to_item(admin_doc)
        with self.assertRaises(InvalidParameterError):
            api.content.transition(admin_doc, transition='submit')

    def test_moderators_can_publish_all(self):
        """
        Moderators can add and publish any content
        """
        self.login_as_portal_owner()
        admin_doc = api.content.create(
            self.workspace,
            'Document',
            'my-admin-page',
        )
        self.workspace.participant_policy = 'Moderators'

        self.login('user1')
        doc = api.content.create(
            self.workspace,
            'Document',
            'my-test-page',
        )
        # Can publish my own content
        api.content.transition(doc, transition='submit')
        api.content.transition(doc, transition='publish')

        # We can also view and publish someone else's document
        self.traverse_to_item(admin_doc)
        api.content.transition(admin_doc, transition='submit')
        api.content.transition(admin_doc, transition='publish')
