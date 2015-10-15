# coding=utf-8
from plone import api
from ploneintranet.layout.interfaces import IPloneintranetLayoutLayer
from ploneintranet.layout.testing import IntegrationTestCase
from zope.interface import alsoProvides


class TestViews(IntegrationTestCase):

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.folder = api.content.create(
            container=self.portal,
            type='Folder',
            title='Test contextless folder'
        )
        self.request = self.layer['request']
        alsoProvides(self.request, IPloneintranetLayoutLayer)

    def test_webstats_js(self):
        ''' Check if the view works and if it is correctly cached
        '''
        NEW_JS = u'<div>webstats_js</div>'
        OLD_JS = api.portal.get_registry_record('plone.webstats_js')

        request1 = self.request.clone()
        request2 = self.request.clone()
        view1_portal = api.content.get_view(
            'webstats_js',
            self.portal,
            request1
        )
        view1_folder = api.content.get_view(
            'webstats_js',
            self.folder,
            request1
        )
        view2_portal = api.content.get_view(
            'webstats_js',
            self.portal,
            request2
        )

        # Test empty registry record
        self.assertEqual(view1_portal(), OLD_JS)

        # Test modified registry record
        api.portal.set_registry_record('plone.webstats_js', NEW_JS)

        # This comes from cache
        self.assertEqual(view1_portal(), OLD_JS)
        self.assertEqual(view1_folder(), OLD_JS)
        # this does not
        self.assertEqual(view2_portal(), NEW_JS)

        # reset the registry record
        api.portal.set_registry_record('plone.webstats_js', OLD_JS)
