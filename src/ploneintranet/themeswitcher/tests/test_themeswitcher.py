from plone.testing.z2 import Browser
from ploneintranet.themeswitcher.testing import FunctionalTestCase


class TestThemeswitcher(FunctionalTestCase):

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_verifysetup(self):
        """Verify that testthemeA is loaded"""
        browser = Browser(self.app)
        browser.open(self.portal.absolute_url())
        self.assertTrue('testthemeA title' in browser.contents)
