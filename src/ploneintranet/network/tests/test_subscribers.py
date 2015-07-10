from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser
from plone.uuid.interfaces import IUUID
import transaction


from ploneintranet.network.setuphandlers import restore_all_behaviors
from ploneintranet.network.testing import FunctionalTestCase


class TestSubscribers(FunctionalTestCase):

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        self.graph = api.portal.get_tool('ploneintranet_network')
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def add_testdocument(self):
        """Helper method"""
        self.browser.open(self.portal_url + '/++add++Document')
        self.browser.getControl(
            name="form.widgets.IDublinCore.title"
        ).value = 'TestDocument'
        self.browser.getControl(
            name="form.widgets.IDublinCore.subjects"
        ).value = "foo;bar;foobar"
        self.browser.getControl('Save').click()
        self.assertTrue("foobar" in self.browser.contents)
        self.assertFalse("foo;bar" in self.browser.contents)

    def test_add_document_adds_tags(self):
        self.add_testdocument()
        doc = self.portal.testdocument
        uuid = IUUID(doc)
        tags = self.graph.unpack(
            self.graph.get_tags('content', uuid, SITE_OWNER_NAME))
        self.assertEqual(sorted(tags), [u'bar', u'foo', u'foobar'])

    def test_add_document_standard_dublincore_does_not_add_tags(self):
        restore_all_behaviors()
        transaction.commit()
        self.add_testdocument()
        doc = self.portal.testdocument
        uuid = IUUID(doc)
        with self.assertRaises(KeyError):
            self.graph.get_tags('content', uuid, SITE_OWNER_NAME)
