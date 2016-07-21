# coding=utf-8
from plone import api
from ploneintranet.layout.testing import FunctionalTestCase
from ploneintranet.layout.testing import IntegrationTestCase
from ploneintranet.layout.viewlets.resources import PIScriptsView
from ploneintranet.layout.viewlets.resources import PIStylesView
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


class TestResources(FunctionalTestCase):

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_scripts_viewlet(self):
        ''' Test the viewlet that returns the styles
        '''
        viewlet = PIScriptsView(
            self.portal,
            self.request.clone(),
            None,
            None,
        )
        viewlet.update()
        # normally we have all the bundles
        self.assertSetEqual(
            {x.get('bundle') for x in viewlet.scripts()},
            {'production'},
        )
        # but we can disable some of theme, in the theme...
        viewlet.themeObj.disabled_bundles.append('production')
        self.assertSetEqual(
            {x.get('bundle') for x in viewlet.scripts()},
            set([]),
        )
        # or through the request
        viewlet.themeObj.disabled_bundles.pop(0)
        viewlet.request.disabled_bundles = ['production']
        self.assertSetEqual(
            {x.get('bundle') for x in viewlet.scripts()},
            set([])
        )
        # if we fake a theme switch
        # we get what the resource registry thinks is good
        oldname = viewlet.themeObj.__name__
        viewlet.themeObj.__name__ = u'something'
        self.assertSetEqual(
            {x.get('bundle') for x in viewlet.scripts()},
            {'production'},
        )
        viewlet.themeObj.__name__ = oldname

    def test_styles_viewlet(self):
        ''' Test the viewlet that returns the styles
        '''
        viewlet = PIStylesView(
            self.portal,
            self.request.clone(),
            None,
            None,
        )
        viewlet.update()
        # normally we have all the bundles
        self.assertSetEqual(
            {x.get('bundle') for x in viewlet.styles()},
            {'diazo', 'production'},
        )
        # but we can disable some of theme, in the theme...
        viewlet.themeObj.disabled_bundles.append('diazo')
        self.assertSetEqual(
            {x.get('bundle') for x in viewlet.styles()},
            {'production'},
        )
        # and through the request
        viewlet.request.disabled_bundles = ['production']
        self.assertSetEqual(
            {x.get('bundle') for x in viewlet.styles()},
            set([])
        )
        # if we fake a theme switch
        # we get what the resource registry thinks is good
        oldname = viewlet.themeObj.__name__
        viewlet.themeObj.__name__ = u'something'
        self.assertSetEqual(
            {x.get('bundle') for x in viewlet.styles()},
            {'diazo', 'production'},
        )
        viewlet.themeObj.__name__ = oldname
