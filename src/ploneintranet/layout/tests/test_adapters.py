from plone import api
from zope.interface import alsoProvides
from zope.interface.verify import verifyObject

from ploneintranet.layout.interfaces import IAppContainer, IAppContent
from ploneintranet.layout.testing import IntegrationTestCase


class TestAppContent(IntegrationTestCase):

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.f1 = api.content.create(container=self.portal,
                                     type='Folder',
                                     title='testfolder 1')
        self.f1.app_name = 'app-foo'
        self.f1.app_layers = ()
        alsoProvides(self.f1, IAppContainer)
        self.d1 = api.content.create(container=self.f1,
                                     type='Document',
                                     title='testdocument 1')
        self.f2 = api.content.create(container=self.portal,
                                     type='Folder',
                                     title='testfolder 2')

    def test_lookup(self):
        adapted = IAppContent(self.d1)
        self.assertTrue(IAppContent.providedBy(adapted))

    def test_verify(self):
        adapted = IAppContent(self.d1)
        self.assertTrue(verifyObject(IAppContent, adapted))

    def test_app_name_noapp(self):
        self.assertEquals('', IAppContent(self.f2).app_name)

    def test_app_name_app(self):
        self.assertEquals(self.f1.app_name, IAppContent(self.f1).app_name)

    def test_app_name_doc(self):
        self.assertEquals(self.d1.app_name, IAppContent(self.f1).app_name)

    def test_in_app_noapp(self):
        self.assertFalse(IAppContent(self.f2).in_app)

    def test_in_app_app(self):
        self.assertTrue(IAppContent(self.f1).in_app)

    def test_in_app_doc(self):
        self.assertTrue(IAppContent(self.d1).in_app)

    def test_get_app_noapp(self):
        self.assertEquals(None, IAppContent(self.f2).get_app())

    def test_get_app_app(self):
        self.assertEquals(self.f1, IAppContent(self.f1).get_app())

    def test_get_app_doc(self):
        self.assertEquals(self.f1, IAppContent(self.d1).get_app())
