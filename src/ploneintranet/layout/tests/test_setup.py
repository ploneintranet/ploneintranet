from plone import api
from plone.browserlayer.utils import registered_layers
from ploneintranet.layout.testing import IntegrationTestCase
from ploneintranet.layout.interfaces import IPloneintranetLayoutLayer
from ploneintranet.layout.interfaces import IPloneintranetContentLayer
from ploneintranet.layout.interfaces import IPloneintranetFormLayer


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
