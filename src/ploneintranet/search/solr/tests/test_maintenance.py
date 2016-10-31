from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter

from ploneintranet.search.solr import testing


class TestMaintenanceView(testing.FunctionalTestCase):

    def setUp(self):
        super(TestMaintenanceView, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        view = getMultiAdapter((self.portal, self.request),
                               name="solr-maintenance")
        self.view = view.__of__(self.portal)

        def monkey_mklog(*args, **kwargs):
            def log(msg, timestamp=True):
                pass
            return log
        self.view.mklog = monkey_mklog

    def assertOK(self, *ignore):
        self.assertEqual(200, self.request.response.status)

    def test_optimize(self):
        self.assertOK(self.view.optimize())

    def test_clear(self):
        self.assertOK(self.view.clear())

    def test_reindex(self):
        self.assertOK(self.view.reindex())

    def test_sync(self):
        self.assertOK(self.view.sync())

    def test_cleanup(self):
        with self.assertRaises(NotImplementedError):
            self.view.cleanup()
