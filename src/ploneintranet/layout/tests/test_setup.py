
from plone import api
from ploneintranet.layout.testing import IntegrationTestCase


class TestSetup(IntegrationTestCase):

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ploneintranet.layout is installed."""
        self.assertTrue(
            self.installer.isProductInstalled('ploneintranet.layout'))

    def test_layout(self):
        self.assertEqual('dashboard.html', self.portal.getLayout())

    def test_actions(self):
        actions = api.portal.get_tool('portal_actions')
        self.assertIn('index_html', actions.portal_tabs)
        self.assertEqual('Dashboard', actions.portal_tabs['index_html'].title)


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

    def test_layout(self):
        self.assertEqual('listing_view', self.portal.getLayout())
