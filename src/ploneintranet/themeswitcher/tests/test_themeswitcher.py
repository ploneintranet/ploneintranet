from plone.testing.z2 import Browser
from plone.app.theming.utils import theming_policy
from ploneintranet.themeswitcher.testing import IntegrationTestCase
from ploneintranet.themeswitcher.testing import FunctionalTestCase


class TestIntegration(IntegrationTestCase):

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_custom_policy(self):
        """Verify that our custom adapter is loaded"""
        from ploneintranet.themeswitcher.policy import SwitchableThemingPolicy
        policy = theming_policy()
        self.assertEqual(policy.__class__, SwitchableThemingPolicy)


class TestFunctional(FunctionalTestCase):

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_verifysetup(self):
        """Verify that testthemeA is loaded"""
        browser = Browser(self.app)
        browser.open(self.portal.absolute_url())
        self.assertTrue('testthemeA title' in browser.contents)

    def test_default_theme(self):
        """Verify normal theme loading"""
        policy = theming_policy(self.request)
        themename = policy.getCurrentTheme()
        self.assertEqual(themename, u'ploneintranet.themeswitcher.testthemeA')

    def test_hostname_switching_direct(self):
        """Switch theme based on hostname"""
        request = self.request
        request['SERVER_NAME'] = 'cms.localhost'
        policy = theming_policy(request)
        themename = policy.getCurrentTheme()
        self.assertEqual(themename, u'barceloneta')

    def test_hostname_switching_registry(self):
        request = self.request
        policy = theming_policy(request)
        themename = policy.getCurrentTheme()
        self.assertEqual(themename, u'ploneintranet.themeswitcher.testthemeA')
        switchersettings = policy.getSwitcherSettings()
        switchersettings.hostname_switchlist.append(u"nohost")
        themename = policy.getCurrentTheme()
        self.assertEqual(themename, u'barceloneta')
