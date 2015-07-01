"""Tests for the example search API"""
from plone.app.testing import IntegrationTesting, PloneSandboxLayer

from . import base as base_tests
from .. import testing
from ..base import FEATURE_NOT_IMPLEMENTED
import ploneintranet.search


class ZCatalogLayer(PloneSandboxLayer):
    """Loads the registrations for the zcatalog implementation."""

    defaultBases = (testing.FIXTURE,)

    def setUpZope(self, app, configuration_context):
        super(ZCatalogLayer, self).setUpZope(app, configuration_context)
        self.loadZCML(name='zcatalog.zcml', package=ploneintranet.search)


INTEGRATION_TESTING = IntegrationTesting(
    bases=(ZCatalogLayer(),),
    name='ZCatalogLayer:IntegrationTesting'
)


class IntegrationTestsMixin(object):

    layer = INTEGRATION_TESTING

    def _make_utility(self):
        from ..zcatalog import SiteSearch
        return SiteSearch()


class TestSiteSearch(IntegrationTestsMixin,
                     base_tests.SiteSearchTestsMixin,
                     testing.IntegrationTestCase):
    """Test the example zcatalog search API implementation"""

    def test_spell_corrected_search(self):
        util = self._make_utility()
        response = util.query('spelling beans')
        self.assertIs(response.spell_corrected_search, FEATURE_NOT_IMPLEMENTED)


class TestSiteSearchPermissions(IntegrationTestsMixin,
                                base_tests.SiteSearchPermissionTestsMixin,
                                testing.IntegrationTestCase):
    """Test the example zcatalog search API w/permissions."""
