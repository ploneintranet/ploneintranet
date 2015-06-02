import unittest
from plone import api
from plone.testing.z2 import Browser
from plone.app.theming.utils import theming_policy
from zope.interface import directlyProvidedBy

from ploneintranet.themeswitcher.interfaces import IThemeASpecific
from ploneintranet.themeswitcher.policy import SwitchableRecordsProxy

from ploneintranet.themeswitcher.testing import IntegrationTestCase
from ploneintranet.themeswitcher.testing import FunctionalTestCase


class TestSwitchableRecordsProxy(unittest.TestCase):

    def test_getattr(self):
        overrides = dict(foo='bar')
        proxy = SwitchableRecordsProxy(None, **overrides)
        self.assertEqual(proxy.foo, 'bar')

    def test_setattr(self):
        overrides = dict(foo='bar')
        proxy = SwitchableRecordsProxy(None, **overrides)
        with self.assertRaises(AttributeError):
            proxy.baz = 'xyz'


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

    def test_registry(self):
        """Verify that registry.xml was loaded
        instead of the interfaces.py default values
        """
        policy = theming_policy()
        switch_settings = policy.getSwitcherSettings()
        self.assertTrue(switch_settings.enabled)
        self.assertEqual(switch_settings.fallback_theme, u'barceloneta')
        self.assertEqual(switch_settings.hostname_switchlist,
                         [u'cms.localhost'])
        self.assertEqual(
            switch_settings.browserlayer_filterlist,
            [u'ploneintranet.themeswitcher.interfaces.IThemeASpecific'])


class TestFunctional(FunctionalTestCase):

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # avoid CSRF error on homepage redirect
        self.testurl = "%s/sitemap" % self.portal.absolute_url()

    def test_verifysetup(self):
        """Verify that testthemeA is loaded"""
        browser = Browser(self.app)
        browser.open(self.testurl)
        self.assertTrue('testthemeA title' in browser.contents)

    def test_default_theme(self):
        """Verify normal theme loading"""
        policy = theming_policy(self.request)
        themename = policy.getCurrentTheme()
        self.assertEqual(themename, u'ploneintranet.themeswitcher.testthemeA')

    def test_hostname_switching(self):
        """Switch theme based on hostname"""
        request = self.request
        request['HTTP_HOST'] = 'cms.localhost:8080'
        policy = theming_policy(request)
        themename = policy.getCurrentTheme()
        self.assertEqual(themename, u'barceloneta')

    def test_settings(self):
        """Switch theme based on hostname"""
        request = self.request
        request['HTTP_HOST'] = 'cms.localhost:8080'
        policy = theming_policy(request)
        settings = policy.getSettings()
        self.assertTrue('SwitchableRecordsProxy' in repr(settings))
        self.assertEqual(settings.currentTheme, u'barceloneta')
        self.assertEqual(settings.rules, u'/++theme++barceloneta/rules.xml')

    def test_hostname_layer_marking(self):
        request = self.request
        request['HTTP_HOST'] = 'cms.localhost:8080'
        policy = theming_policy(request)
        policy.filter_layers()
        active = [x for x in directlyProvidedBy(self.request)]
        self.assertFalse(IThemeASpecific in active)

    def test_hostname_switching_registry(self):
        request = self.request
        policy = theming_policy(request)
        themename = policy.getCurrentTheme()
        self.assertEqual(themename, u'ploneintranet.themeswitcher.testthemeA')
        switchersettings = policy.getSwitcherSettings()
        switchersettings.hostname_switchlist.append(u"nohost")
        themename = policy.getCurrentTheme()
        self.assertEqual(themename, u'barceloneta')

    @unittest.skip("registry settings not picked up")
    def test_hostname_switching_view(self):
        policy = theming_policy(self.request)
        switchersettings = policy.getSwitcherSettings()
        switchersettings.hostname_switchlist.append(u"nohost")
        view = api.content.get_view(
            context=self.portal,
            request=self.request,
            name='sitemap')
        html = view()
        active = [x for x in directlyProvidedBy(self.request)]
        self.assertFalse(IThemeASpecific in active)
        self.assertFalse('testthemeA title' in html)

    @unittest.skip("registry settings not picked up")
    def test_hostname_switching_browser(self):
        policy = theming_policy(self.request)
        switchersettings = policy.getSwitcherSettings()
        switchersettings.hostname_switchlist.append(u"nohost")
        import transaction
        transaction.commit()
        browser = Browser(self.app)
        browser.open(self.testurl)
        self.assertFalse('testthemeA title' in browser.contents)
