"""Tests for the example search API"""
import unittest
from plone.app.testing import FunctionalTesting, PloneSandboxLayer

from ploneintranet.search.tests import test_base
from ploneintranet.search import testing
from ploneintranet.search.base import FEATURE_NOT_IMPLEMENTED
import ploneintranet.search


class ZCatalogLayer(PloneSandboxLayer):
    """Loads the registrations for the zcatalog implementation."""

    defaultBases = (testing.FIXTURE,)

    def setUpZope(self, app, configuration_context):
        super(ZCatalogLayer, self).setUpZope(app, configuration_context)
        self.loadZCML(name='zcatalog.zcml', package=ploneintranet.search)


ZCATALOG_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(ZCatalogLayer(),),
    name='ZCatalogLayer:FunctionalTesting'
)


class TestCatalogSearch(test_base.SearchTestsBase,
                        testing.FunctionalTestCase):
    """Test the example zcatalog search API implementation

    The actual tests are in ploneintranet.search.tests.base.
    """

    layer = ZCATALOG_FUNCTIONAL_TESTING

    def _make_utility(self):
        from ploneintranet.search.zcatalog import SiteSearch
        return SiteSearch()

    def test_spell_corrected_search(self):
        util = self._make_utility()
        response = util.query('spelling beans')
        self.assertIs(response.spell_corrected_search, FEATURE_NOT_IMPLEMENTED)

    @unittest.skip('File content searching not implemented in zcatalog')
    def test_file_content_matches(self):
        self.fail()


class TestCatalogPermissions(test_base.PermissionTestsBase,
                             testing.FunctionalTestCase):
    """Test the example zcatalog search API w/permissions.

    The actual tests are defined in test_base.
    """

    layer = ZCATALOG_FUNCTIONAL_TESTING

    def _make_utility(self):
        from ploneintranet.search.zcatalog import SiteSearch
        return SiteSearch()
