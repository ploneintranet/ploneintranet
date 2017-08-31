# -*- coding: utf-8 -*-
'''Setup/installation tests for this package.'''
from plone import api
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.testing import z2
from ploneintranet.admintool.browser.interfaces import IGeneratePWResetToken
from ploneintranet.admintool.browser.interfaces import IPloneintranetAdmintoolLayer  # noqa
from ploneintranet.admintool.testing import FunctionalTestCase
from ploneintranet.layout.app import apps_container_id
from zope.interface import alsoProvides


class TestViews(FunctionalTestCase):
    '''Test installation of this  product into Plone.'''

    def setUp(self):
        '''Custom shared utility setup for tests.'''
        self.portal = self.layer['portal']
        self.app = self.portal.restrictedTraverse(
            '%s/administrator-tool' % apps_container_id
        )
        self.request = self.layer['request']
        self.login_as_portal_owner()

        api.content.create(
            type='ploneintranet.userprofile.userprofile',
            container=self.portal.profiles,
            title='John Doe',
            first_name='John',
            last_name='Doe',
            username='john-doe',
        )
        api.content.create(
            type='ploneintranet.userprofile.userprofile',
            container=self.portal.profiles,
            title='John Smith',
            first_name='John',
            last_name='Smith',
            username='john-smith',
        )
        api.content.create(
            type='ploneintranet.userprofile.userprofile',
            container=self.portal.profiles,
            title='Maria Rossi',
            first_name='Maria',
            last_name='Rossi',
            username='maria-rossi',
        )

        # pre date user creation date and change the state
        # for testing the sort methods
        for idx, (userid, to_state) in enumerate(
            zip(
                ('john-doe', 'maria-rossi'),
                ('enabled', 'disabled')
            )
        ):
            obj = self.portal.profiles[userid]
            obj.creation_date = obj.creation_date - idx - 1
            api.content.transition(obj, to_state=to_state)
            obj.reindexObject(idxs=['created', 'review_state'])

    def login_as_portal_owner(self):
        """
        helper method to login as site admin
        """
        z2.login(self.layer['app']['acl_users'], SITE_OWNER_NAME)

    def get_request(self, params={}):
        ''' Prepare a fresh request
        '''
        request = self.request.clone()
        request.form.update(params)
        alsoProvides(request, IPloneintranetAdmintoolLayer)
        return request

    def get_app_admintool(self, params={}):
        ''' Get the app view called with params
        '''
        return api.content.get_view(
            'app-administrator-tool',
            self.app,
            self.get_request(params),
        )

    def test_app_available(self):
        view = api.content.get_view(
            'apps.html',
            self.portal,
            self.get_request(),
        )
        self.assertIn(self.app, view.apps())
        view = api.content.get_view(
            'app-tile',
            self.app,
            self.get_request(),
        )
        with api.env.adopt_roles([
            'Member',
            'Authenticated',
            'Site Administrator',
        ]):
            self.assertEqual(view.disabled, 'disabled')

        # clear memoized values
        view.request = self.get_request()
        with api.env.adopt_roles([
            'Member',
            'Authenticated',
            'Contributor',
            'Editor',
            'Reader',
        ]
        ):
            self.assertEqual(view.disabled, 'disabled')

    def test_user_management(self):
        existing_profiles = self.portal.profiles.listFolderContents()

        # Test sorting by title
        view = api.content.get_view(
            'user-management',
            self.app,
            self.get_request(),
        )
        found_profiles = [
            x.title for x in view.users
        ]
        self.assertListEqual(
            found_profiles,
            [
                user.title for user in sorted(
                    existing_profiles, key=lambda obj: obj.last_name)]
        )

        # Test sorting by reversed creation date
        existing_profiles = sorted(
            existing_profiles,
            key=lambda obj: obj.creation_date,
            reverse=True,
        )
        view = api.content.get_view(
            'user-management',
            self.app,
            self.get_request({'sorting': '-created'}),
        )
        found_profiles = [
            x.title for x in view.users
        ]
        self.assertListEqual(
            found_profiles,
            [obj.title for obj in existing_profiles],
        )

        # Test sorting by review_state
        existing_profiles = sorted(
            existing_profiles,
            key=lambda obj: api.content.get_state(obj),
        )
        view = api.content.get_view(
            'user-management',
            self.app,
            self.get_request({'sorting': 'review_state'}),
        )
        found_profiles = [
            x.title for x in view.users
        ]
        self.assertListEqual(
            found_profiles,
            [obj.title for obj in existing_profiles],
        )

        # Test searchable text
        view.request = self.get_request({'SearchableText': 'Doe'})
        self.assertListEqual(
            [x.title for x in view.users],
            [u'John Doe']
        )

    def test_create_user_panel(self):
        view = api.content.get_view(
            'panel-create-user-account',
            self.portal.profiles,
            self.get_request(),
        )
        self.assertRaises(ValueError, view.create_user)
        self.assertEqual(view.error, u'missing_parameter_key')
        view.request = self.get_request({
            'username': 'john-doe',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'jd@example.com',
        })
        self.assertRaises(Exception, view.create_user)
        self.assertEqual(
            view.error,
            'The id "john-doe" is invalid - it is already in use.'
        )
        view.request = self.get_request({
            'username': 'jane-doe',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jd@example.com',
        })
        user = view.create_user()
        self.assertEqual(user.fullname, u'Jane Doe')
        self.assertEqual(
            api.content.get_state(user),
            'enabled',
        )

    def test_mail_user_created(self):
        view = api.content.get_view(
            'mail-user-created',
            self.portal.profiles['john-doe'],
            self.get_request(),
        )
        self.assertIn(
            'http://nohost/plone/passwordreset/exampletoken',
            view(),
        )
        request = self.get_request()
        alsoProvides(request, IGeneratePWResetToken)
        view.request = request
        # The example token is replaced by a proper token
        self.assertNotIn(
            'http://nohost/plone/passwordreset/exampletoken',
            view(),
        )
