import transaction

from plone import api
from zope.interface import alsoProvides
from ZPublisher import BeforeTraverse

from plone.testing.z2 import Browser

from ploneintranet.layout.interfaces import IAppContainer
from ploneintranet.layout.layers import enable_app_layer
from ploneintranet.layout.testing import FunctionalTestCase
from .utils import IMockLayer, IMockFolder


class IMockContainer(IAppContainer):
    pass


class TestLayers(FunctionalTestCase):

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_all_layers_disabled(self):
        view = api.content.get_view(
            context=self.portal,
            request=self.request,
            name='sitemap')
        view()
        self.assertFalse(IMockLayer.providedBy(self.request))

    def test_all_layers_disabled_via_browser(self):
        browser = Browser(self.app)
        browser.open("%s/@@browser_layers" % self.portal.absolute_url())
        self.assertFalse('ploneintranet.layout.tests.utils.IMockLayer'
                         in browser.contents)

    def test_app_layer_enabled_directly(self):
        folder = api.content.create(container=self.portal,
                                    type='Folder',
                                    title='testfolder')
        api.content.transition(folder, 'publish')
        alsoProvides(folder, IMockFolder)
        folder.app_layers = (IMockLayer,)
        BeforeTraverse.registerBeforeTraverse(folder,
                                              enable_app_layer(),
                                              'enable_app_layer')
        transaction.commit()

        browser = Browser(self.app)
        browser.open("%s/@@browser_layers" % folder.absolute_url())
        self.assertTrue('ploneintranet.layout.tests.utils.IMockLayer'
                        in browser.contents)

    def test_app_layer_enabled_subclass(self):
        mockfolder = api.content.create(
            container=self.portal,
            type='ploneintranet.layout.mockfolder',
            title='mockfolder')
        api.content.transition(mockfolder, 'publish')
        transaction.commit()

        browser = Browser(self.app)
        browser.open("%s/@@browser_layers" % mockfolder.absolute_url())
        self.assertTrue('ploneintranet.layout.tests.utils.IMockLayer'
                        in browser.contents)
