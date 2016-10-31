# coding=utf-8
from plone import api
from ploneintranet.search.solr import testing
from ploneintranet.search.solr.indexers import only_if_installed


class DummyClass(object):

    @only_if_installed
    def dummy_method(self):
        return 1


class TestDecorators(testing.IntegrationTestCase):

    layer = testing.INTEGRATION_TESTING

    def test_only_if_installed(self):
        # When the product is installed dummy_method returns 1
        dummy = DummyClass()
        self.assertEqual(dummy.dummy_method(), 1)

        # Removing the product makes dummy_method return None
        qi = api.portal.get_tool('portal_quickinstaller')
        qi.uninstallProducts(['ploneintranet.search'])
        self.assertEqual(dummy.dummy_method(), None)
