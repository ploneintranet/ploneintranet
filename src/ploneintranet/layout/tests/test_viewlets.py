from plone import api
from ploneintranet.layout.testing import IntegrationTestCase
from ploneintranet.theme.interfaces import IThemeSpecific
from zope.component import getMultiAdapter
from zope.interface import alsoProvides


class TestBreadcrumbs(IntegrationTestCase):

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.folder = api.content.create(
            container=self.portal,
            type='Folder',
            title='Main folder')
        api.content.transition(self.folder, 'publish')
        self.subfolder = api.content.create(
            container=self.folder,
            type='Folder',
            title='Sub folder')
        api.content.transition(self.subfolder, 'publish')

    def _add_browser_layer(self, layer):
        alsoProvides(self.request, layer)

    def _get_breadcrumbs(self, context):
        view = getMultiAdapter(
            (context, self.request), name='breadcrumbs_view')
        return view.breadcrumbs()

    def test_breadcrumbs_cms(self):
        self.assertEqual(self._get_breadcrumbs(self.portal), ())
        self.assertEqual(self._get_breadcrumbs(self.folder),
                         ({'absolute_url': self.folder.absolute_url(),
                           'Title': 'Main folder'},))
        self.assertEqual(self._get_breadcrumbs(self.subfolder),
                         ({'absolute_url': self.folder.absolute_url(),
                           'Title': 'Main folder'},
                          {'absolute_url': self.subfolder.absolute_url(),
                           'Title': 'Sub folder'}))

    def test_breadcrumbs_theme(self):
        self._add_browser_layer(IThemeSpecific)
        self.assertEqual(self._get_breadcrumbs(self.portal), ())
        self.assertEqual(self._get_breadcrumbs(self.folder),
                         ({'absolute_url': self.folder.absolute_url(),
                           'Title': 'Main folder'},))
        self.assertEqual(self._get_breadcrumbs(self.subfolder),
                         ({'absolute_url': self.folder.absolute_url(),
                           'Title': 'Main folder'},))
