from z3c.form.interfaces import IFormLayer
from zope.annotation import IAttributeAnnotatable
from zope.component import provideAdapter
from zope.interface import alsoProvides, Interface
from zope.publisher.browser import TestRequest
from plone import api
from zope.publisher.interfaces.browser import IBrowserRequest
from ploneintranet.simplesharing.forms import SimpleSharing
from ploneintranet.simplesharing.tests.base import BaseTestCase


class TestBehaviors(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        provideAdapter(adapts=(Interface, IBrowserRequest),
                       provides=Interface,
                       factory=SimpleSharing,
                       name="simple-sharing")

    def setUp(self):
        super(TestBehaviors, self).setUp()
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

        request = TestRequest()
        request.form.update(form)
        alsoProvides(request, IFormLayer)
        alsoProvides(request, IAttributeAnnotatable)
        return request

    def test_visibility(self):
        request = self.make_request(
            visibility='published',
            share_with=[]
        )

        shareform = api.content.get_view('simple-sharing',
                                         context=self.doc,
                                         request=request)
        shareform.update()

        data, errors = shareform.extractData()
        self.assertEqual(len(errors), 0)
        self.assertEqual(api.content.get_state(self.doc), 'published')
        self.assertEqual(self.doc.users_with_local_role('Reader'), [])

    def test_share_with(self):
        user1 = api.user.create(
            email='test@user.co',
            username='user1',
            password='12345'
        )

        request = self.make_request(
            visibility='private',
            share_with='user1'
        )

        shareform = api.content.get_view('simple-sharing',
                                         context=self.doc,
                                         request=request)
        shareform.update()
        data, errors = shareform.extractData()
        self.assertEqual(len(errors), 0)
        self.assertEqual(api.content.get_state(self.doc), 'private')
        self.assertEqual(self.doc.users_with_local_role('Reader'),
                         ['user1'],
                         'User1 has not been given the Reader role')
