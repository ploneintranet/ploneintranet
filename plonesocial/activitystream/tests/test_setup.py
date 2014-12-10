# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IResourceRegistry
from plonesocial.activitystream.testing import (
    PLONESOCIAL_ACTIVITYSTREAM_INTEGRATION_TESTING
)
from plone import api
from plone.browserlayer.utils import registered_layers
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import unittest2 as unittest

PROJECTNAME = 'plonesocial.activitystream'
CSS = (
    '++resource++plonesocial.activitystream.stylesheets/activitystream.css',
)


class InstallTestCase(unittest.TestCase):

    layer = PLONESOCIAL_ACTIVITYSTREAM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_product_is_installed(self):
        qi = self.portal['portal_quickinstaller']
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertIn('IPlonesocialActivitystreamLayer', layers)

    def test_cssregistry(self):
        bundles = getUtility(IRegistry).collectionOfInterface(
            IResourceRegistry, prefix="plone.resources")
        bundle = bundles['resource-plonesocial-activitystream-stylesheets']

        for id in CSS:
            self.assertIn(id, bundle.css, '{0} not installed'.format(id))

    def test_activitystream_portal_view_registered(self):
        types = self.portal['portal_types']
        site_views = types['Plone Site'].view_methods
        folder_views = types['Folder'].view_methods
        self.assertIn('activitystream_portal', site_views)
        self.assertIn('activitystream_portal', folder_views)


class UninstallTestCase(unittest.TestCase):

    layer = PLONESOCIAL_ACTIVITYSTREAM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer_removed(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertNotIn('IPlonesocialActivitystreamLayer', layers)

    def _XXXtest_cssregistry_removed(self): # Bug in Plone 5
        bundles = getUtility(IRegistry).collectionOfInterface(
            IResourceRegistry, prefix="plone.resources")
        bundle = bundles['resource-plonesocial-activitystream-stylesheets']
        for id in CSS:
            self.assertNotIn(id, bundle.css, '{0} not removed'.format(id))

    def test_activitystream_portal_view_removed(self):
        types = self.portal['portal_types']
        site_views = types['Plone Site'].view_methods
        folder_views = types['Folder'].view_methods
        self.assertNotIn('activitystream_portal', site_views)
        self.assertNotIn('activitystream_portal', folder_views)
