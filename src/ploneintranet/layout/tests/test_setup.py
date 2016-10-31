from plone import api
from plone.browserlayer.utils import registered_layers
from ploneintranet.layout.testing import IntegrationTestCase
from ploneintranet.layout.interfaces import IPloneintranetLayoutLayer
from ploneintranet.layout.interfaces import IPloneintranetContentLayer
from ploneintranet.layout.interfaces import IPloneintranetFormLayer
from ploneintranet.layout.setuphandlers import create_apps_container


class TestSetup(IntegrationTestCase):

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ploneintranet.layout is installed."""
        self.assertTrue(
            self.installer.isProductInstalled('ploneintranet.layout'))

    def test_layout_browserlayer(self):
        """Test that IPloneintranetLayoutLayer is registered."""
        self.assertIn(IPloneintranetLayoutLayer, registered_layers())

    def test_content_browserlayer(self):
        """Test that IPloneintranetContentLayer is registered."""
        self.assertIn(IPloneintranetContentLayer, registered_layers())

    def test_form_browserlayer(self):
        """Test that IPloneintranetFormLayer is registered."""
        self.assertIn(IPloneintranetFormLayer, registered_layers())

    def test_layout(self):
        self.assertEqual('dashboard.html', self.portal.getLayout())

    def test_actions(self):
        actions = api.portal.get_tool('portal_actions')
        self.assertIn('index_html', actions.portal_tabs)
        self.assertIn('dashboard', actions.portal_tabs)
        self.assertEqual('Dashboard', actions.portal_tabs['dashboard'].title)
        self.assertEqual(False, actions.portal_tabs['index_html'].visible)

    def test_apps_created(self):
        ''' The setuphandlers creates and publishes some apps
        '''
        self.assertListEqual(
            self.portal.apps.keys(),
            [
                'contacts',
                'messages',
                'todo',
                'calendar',
                'slide-bank',
                'image-bank',
                # 'news',
                'case-manager',
                'app-market',
            ]
        )
        for app in self.portal.apps.listFolderContents():
            self.assertEqual(
                api.content.get_state(app),
                'published',
            )

    def test_create_apps_container(self):
        ''' Test the create_apps_container function
        '''
        # we remove the apps created by the setuphandler
        api.content.delete(self.portal.apps)

        # We can call the function to just create the apps
        create_apps_container(with_apps=False)
        self.assertTrue(len(self.portal.apps) == 0)

        # or to create everything (the default)
        create_apps_container()
        self.assertTrue(len(self.portal.apps) != 0)


class TestUninstall(IntegrationTestCase):

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['ploneintranet.layout'])

    def test_uninstall(self):
        """Test if ploneintranet.layout is cleanly uninstalled."""
        self.assertFalse(
            self.installer.isProductInstalled('ploneintranet.layout'))

    def test_layout_browserlayer_removed(self):
        """Test that IPloneintranetLayoutLayer is unregistered."""
        self.assertNotIn(IPloneintranetLayoutLayer, registered_layers())

    def test_content_browserlayer_removed(self):
        """Test that IPloneintranetContentLayer is unregistered."""
        self.assertNotIn(IPloneintranetContentLayer, registered_layers())

    def test_form_browserlayer_removed(self):
        """Test that IPloneintranetFormLayer is unregistered."""
        self.assertNotIn(IPloneintranetFormLayer, registered_layers())

    def test_layout(self):
        self.assertEqual('listing_view', self.portal.getLayout())
