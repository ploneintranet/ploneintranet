# -*- coding: utf-8 -*-
from pkg_resources import resource_string
from plone import api
from plone.app.testing import login
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.namedfile.file import NamedBlobFile
from plone.protect.authenticator import createToken
from ploneintranet import api as pi_api
from ploneintranet.docconv.client.decorators import force_synchronous_previews
from ploneintranet.docconv.client.interfaces import IPloneintranetDocconvClientLayer  # noqa
from ploneintranet.docconv.client.testing import FunctionalTestCase
from StringIO import StringIO
from zope.annotation import IAnnotations


class TestDocconvViews(FunctionalTestCase):
    '''Test views for ploneintranet.docconv.client
    '''

    def setUp(self):
        '''Custom shared utility setup for tests.'''
        self.portal = self.layer['portal']
        login(self.portal.aq_parent, SITE_OWNER_NAME)

    def get_blob(self):
        ''' Returns a blob with a previewable pdf
        '''
        return NamedBlobFile(
            data=resource_string(
                'ploneintranet.attachments.tests',
                'plone.pdf'
            ).decode(
                'latin1',
                'utf8'
            ),
            filename=u'plone.pdf'
        )

    def get_request(self, params={}):
        ''' Return a fresh request
        '''
        request = self.layer['request'].clone()
        request.form.update(params)
        # Keep standard output clean
        request.response.stdout = StringIO()
        return request

    def get_preview_ids_for(self, obj):
        ''' Get's the preview blob ids

        This is used to verify if the previews have been regenerated
        '''
        annotations = IAnnotations(obj)
        blobs = annotations['collective.documentviewer']['blob_files'].values()
        return map(id, blobs)

    def test_regenerate_views_csrf(self):
        ''' Check if the view correctly requires the CSRF _authenticator
        '''
        view = api.content.get_view(
            'generate-previews-for-contents',
            self.portal,
            self.get_request()
        )
        self.assertIn('requires confirmation', view())

        view = api.content.get_view(
            'generate-previews-for-contents-async',
            self.portal,
            self.get_request()
        )
        self.assertIn('requires confirmation', view())

    def test_regenerate_sync_view(self):
        '''
        Test the views that regenerate the previews synchronously
        '''
        file1 = api.content.create(
            self.portal,
            id='file1',
            type='File',
        )
        # We have no file => no previews
        self.assertFalse(pi_api.previews.has_previews(file1))

        # We add a file => we want previews!
        file1.file = self.get_blob()
        view = api.content.get_view(
            'generate-previews-for-contents',
            self.portal,
            self.get_request({'_authenticator': createToken()})
        )
        view()
        self.assertTrue(pi_api.previews.has_previews(file1))

    @force_synchronous_previews
    def test_regenerate_async_view(self):
        '''
        Test the views that regenerate the previews asynchronously

        We need the force_synchronous_previews decorator
        for testing purposes
        '''
        file1 = api.content.create(
            self.portal,
            id='file1',
            type='File',
        )
        # We have no file => no previews
        self.assertFalse(pi_api.previews.has_previews(file1))

        # We add a file => we want previews!
        file1.file = self.get_blob()
        view = api.content.get_view(
            'generate-previews-for-contents',
            self.portal,
            self.get_request({'_authenticator': createToken()})
        )
        view()
        self.assertTrue(pi_api.previews.has_previews(file1))

    def test_force_regenerate_sync_view(self):
        '''
        Test we can regenerate existing previews
        '''
        file1 = api.content.create(
            self.portal,
            id='file1',
            type='File',
            file=self.get_blob()
        )
        # the time of the original preview generation
        original_ids = self.get_preview_ids_for(file1)

        # Calling the view without the generate parameter will not force
        # The preview regeneration
        view = api.content.get_view(
            'generate-previews-for-contents',
            self.portal,
            self.get_request({'_authenticator': createToken()})
        )
        self.assertEqual(
            self.get_preview_ids_for(file1),
            original_ids,
        )

        # Adding a truish regenerate value to the request will
        view = api.content.get_view(
            'generate-previews-for-contents',
            self.portal,
            self.get_request({
                '_authenticator': createToken(),
                'regenerate': True,
            })
        )
        view()
        self.assertNotEqual(
            self.get_preview_ids_for(file1),
            original_ids,
        )
