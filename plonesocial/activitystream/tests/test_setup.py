# -*- coding: utf-8 -*-

from ..browser.interfaces import IPlonesocialActivitystreamLayer
from ..testing import PLONESOCIAL_ACTIVITYSTREAM_INTEGRATION_TESTING
from plone.browserlayer.utils import registered_layers

import unittest2 as unittest

PROJECTNAME = 'plonesocial.activitystream'
CSS_ID = '++resource++plonesocial.activitystream.stylesheets/activitystream.css'  # noqa


class InstallTestCase(unittest.TestCase):

    layer = PLONESOCIAL_ACTIVITYSTREAM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']
        self.types = self.portal['portal_types']

    def test_product_is_installed(self):
        installed = [p['id'] for p in self.qi.listInstalledProducts()]
        self.assertTrue(PROJECTNAME in installed,
                        'package appears not to have been installed')

    def test_browser_layer_installed(self):
        self.assertIn(IPlonesocialActivitystreamLayer, registered_layers())

    def test_cssregistry(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        self.assertIn(CSS_ID, resource_ids)

    def test_activitystream_portal_view_registered(self):
        folder_views = self.types['Folder'].view_methods
        self.assertIn('activitystream_portal', folder_views)


class UninstallTestCase(unittest.TestCase):

    layer = PLONESOCIAL_ACTIVITYSTREAM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']
        self.types = self.portal['portal_types']
        self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_browser_layer_removed_uninstalled(self):
        self.assertNotIn(IPlonesocialActivitystreamLayer, registered_layers())

    def test_cssregistry_removed(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        self.assertNotIn(CSS_ID, resource_ids)

    def test_activitystream_portal_view_removed(self):
        folder_views = self.types['Folder'].view_methods
        self.assertNotIn('activitystream_portal', folder_views)
