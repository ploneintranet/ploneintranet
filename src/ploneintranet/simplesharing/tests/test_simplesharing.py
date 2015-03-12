from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import NOT_CHANGED
from zope.annotation import IAttributeAnnotatable
from zope.component import provideAdapter
from zope.interface import alsoProvides, Interface
from zope.publisher.browser import TestRequest
from plone import api
from zope.publisher.interfaces.browser import IBrowserRequest
from ploneintranet.simplesharing.forms import SimpleSharing
from ploneintranet.simplesharing.tests.base import BaseTestCase


class TestSimpleSharing(BaseTestCase):

    def setUp(self):
        super(TestSimpleSharing, self).setUp()
        provideAdapter(adapts=(Interface, IBrowserRequest),
                       provides=Interface,
                       factory=SimpleSharing,
                       name="simple-sharing")
        self.login_as_portal_owner()
        self.doc = api.content.create(
            self.portal,
            "Document",
            "example-document",
            title="A document")

    def make_request(self, visibility, share_with):
        """ Creates a request
        :param visibility: The workflow state to transition to
        :type visibility: str
        :param share_with: The users to explicitly share with
        :type share_with: list
        :return: submitted request.
        """

        form = {
            'form.widgets.visibility': visibility,
            'form.widgets.share_with': share_with,
            'form.buttons.share': 'Share',
        }

        request = TestRequest(environ=self.request)
        request.form.update(form)
        alsoProvides(request, IFormLayer)
        alsoProvides(request, IAttributeAnnotatable)
        return request

    def simple_share(self, users, visibility=str(NOT_CHANGED), obj=None):
        if obj is None:
            obj = self.doc
        request = self.make_request(
            visibility=visibility,
            share_with=users
        )

        shareform = api.content.get_view(
            'simple-sharing',
            context=obj,
            request=request
        )
        shareform.update()
        return shareform

    def test_visibility(self):
        self.login_as_portal_owner()

        # Test validation error
        shareform = self.simple_share(['foobar'], 'published')
        self.assertTrue(shareform.status)
        # State and shared with should remain unchanged
        self.assertEqual(api.content.get_state(self.doc), 'private')
        self.assertEqual(self.doc.users_with_local_role('Reader'), [])

        # Test invalid workflow state
        shareform = self.simple_share(['user1'], 'foobar')
        self.assertTrue(shareform.status)
        # State and shared with should remain unchanged
        self.assertEqual(api.content.get_state(self.doc), 'private')
        self.assertEqual(self.doc.users_with_local_role('Reader'), [])

        # Test "Share with all" (publish)
        shareform = self.simple_share([], 'publish')
        self.assertFalse(shareform.status)
        self.assertEqual(api.content.get_state(self.doc), 'published')
        self.assertEqual(self.doc.users_with_local_role('Reader'), [])

    def test_share_with(self):
        api.user.create(
            email='test@user.co',
            username='user1',
            password='12345'
        )
        api.user.create(
            email='test2@user.co',
            username='user2',
            password='12345'
        )
        api.user.create(
            email='test3@user.co',
            username='user3',
            password='12345'
        )

        # Test sharing with one user
        shareform = self.simple_share(['user1'])
        self.assertFalse(shareform.status)
        self.assertEqual(api.content.get_state(self.doc), 'private')
        self.assertEqual(self.doc.users_with_local_role('Reader'),
                         ['user1'],
                         'User1 has not been given the Reader role')

        # Test sharing with 2 users
        self.simple_share(['user1', 'user2'])
        self.assertEqual(
            self.doc.users_with_local_role('Reader'),
            ['user2', 'user1'],
            'User1 and User2 have not both been given the Reader role'
        )

        # Test replacing existing shared users with a new one
        self.simple_share(['user3'])
        self.assertEqual(
            self.doc.users_with_local_role('Reader'),
            ['user3'],
            'User3 has not replaced the previously shared users'
        )

        # Test remove all shares
        self.simple_share([])
        self.assertEqual(
            len(self.doc.users_with_local_role('Reader')),
            0,
            'Users have not been removed from sharing'
        )

        # Test share with None
        self.simple_share(None)
        self.assertEqual(
            len(self.doc.users_with_local_role('Reader')),
            0,
            'Some users have magically been added'
        )
