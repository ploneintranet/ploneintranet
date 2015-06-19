from plone import api
from ploneintranet.invitations.testing import \
    PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING
import unittest


class TestInstall(unittest.TestCase):

    layer = PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ploneintranet.invitations is installed."""
        self.assertTrue(
            self.installer.isProductInstalled('ploneintranet.invitations'))

    def test_browserlayer(self):
        """Test that IKboWebappLayer is registered."""
        from ploneintranet.invitations.interfaces import \
            IPloneintranetInvitationsLayer
        from plone.browserlayer import utils
        self.assertIn(
            IPloneintranetInvitationsLayer, utils.registered_layers())

    def test_controlpanel(self):
        portal_controlpanel = api.portal.get_tool('portal_controlpanel')
        self.assertIn(
            'ploneintranet.invitations',
            [i.id for i in portal_controlpanel.listActions()])


class TestUninstall(unittest.TestCase):

    layer = PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['ploneintranet.invitations'])

    def test_is_uninstalled(self):
        """Test if ploneintranet.invitations is cleanly uninstalled."""
        self.assertFalse(
            self.installer.isProductInstalled('ploneintranet.invitations'))

    def test_browserlayer(self):
        """Test that the layer is removed."""
        from ploneintranet.invitations.interfaces import \
            IPloneintranetInvitationsLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IPloneintranetInvitationsLayer, utils.registered_layers())

    def test_controlpanel_is_removed(self):
        portal_controlpanel = api.portal.get_tool('portal_controlpanel')
        self.assertNotIn(
            'ploneintranet.invitations',
            [i.id for i in portal_controlpanel.listActions()])
