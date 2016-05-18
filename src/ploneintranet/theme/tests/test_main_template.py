# coding=utf-8
from plone import api
from ploneintranet.theme.interfaces import IThemeSpecific
from ploneintranet.theme.testing import PLONEINTRANET_THEME_INTEGRATION_TESTING  # noqa
import unittest2 as unittest
from zope.interface import alsoProvides


class TestSetup(unittest.TestCase):
    """Test that ploneintranet.theme is properly installed."""

    layer = PLONEINTRANET_THEME_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request'].clone()
        alsoProvides(self.request, IThemeSpecific)

    def test_main_template_macros(self):
        """Test if main_template works good."""
        view = api.content.get_view(
            'main_template',
            self.portal,
            self.request,
        )
        self.assertListEqual(
            sorted(view.macros.names),
            ['content', 'master', 'statusmessage', 'webstats_js']
        )

    def test_main_template_call(self):
        """Test if main_template works good."""
        view = api.content.get_view(
            'main_template',
            self.portal,
            self.request,
        )
        view()
