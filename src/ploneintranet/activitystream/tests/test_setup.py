# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IResourceRegistry
from ploneintranet.activitystream.testing import (
    PLONEINTRANET_ACTIVITYSTREAM_INTEGRATION_TESTING
)
from plone import api
from plone.browserlayer.utils import registered_layers
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import unittest2 as unittest

PROJECTNAME = 'ploneintranet.activitystream'
CSS = (
    '++resource++ploneintranet.activitystream.stylesheets/activitystream.css',
)


class InstallTestCase(unittest.TestCase):

    layer = PLONEINTRANET_ACTIVITYSTREAM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_product_is_installed(self):
        qi = self.portal['portal_quickinstaller']
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertIn('IPloneIntranetActivitystreamLayer', layers)

    def test_cssregistry(self):
        bundles = getUtility(IRegistry).collectionOfInterface(
            IResourceRegistry, prefix="plone.resources")
        bundle = bundles['resource-ploneintranet-activitystream-stylesheets']

        for id in CSS:
            self.assertIn(id, bundle.css, '{0} not installed'.format(id))


class UninstallTestCase(unittest.TestCase):

    layer = PLONEINTRANET_ACTIVITYSTREAM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer_removed(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertNotIn('IPloneIntranetActivitystreamLayer', layers)

    def test_cssregistry_removed(self):
        bundles = getUtility(IRegistry).collectionOfInterface(
            IResourceRegistry, prefix="plone.resources")
        self.assertNotIn(
            'resource-ploneintranet-activitystream-stylesheets', bundles)

    def test_view_method_removed(self):
        portal_types = api.portal.get_tool('portal_types')
        fti = portal_types['Folder']
        self.assertNotIn('activitystream_portal', fti.view_methods)
