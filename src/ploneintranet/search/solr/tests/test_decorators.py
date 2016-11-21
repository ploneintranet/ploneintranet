# coding=utf-8
from plone import api
from ploneintranet.search.solr import testing
from ploneintranet.search.solr.indexers import is_solr_enabled


class DummyClass(object):

    @is_solr_enabled
    def dummy_method(self):
        return 'solr enabled'


class TestDecorators(testing.IntegrationTestCase):

    layer = testing.INTEGRATION_TESTING

    def test_is_solr_enabled(self):
        # When the product is installed dummy_method returns 1
        dummy = DummyClass()
        self.assertEqual(dummy.dummy_method(), 'solr enabled')

        # We can disabled it by setting a proper registry
        api.portal.set_registry_record(
            'ploneintranet.search.solr.disabled', True
        )
        self.assertEqual(dummy.dummy_method(), None)
        api.portal.set_registry_record(
            'ploneintranet.search.solr.disabled', False
        )
        self.assertEqual(dummy.dummy_method(), 'solr enabled')

        # Of course if the product is uninstalled solr will be disabled
        qi = api.portal.get_tool('portal_quickinstaller')
        qi.uninstallProducts(['ploneintranet.search'])
        self.assertEqual(dummy.dummy_method(), None)
