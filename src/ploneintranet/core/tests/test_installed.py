# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.core.testing import PLONEINTRANET_CORE_INTEGRATION_TESTING
from plone.browserlayer.utils import registered_layers
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from Products.CMFPlone.interfaces import IResourceRegistry

import unittest2 as unittest

PROJECTNAME = 'ploneintranet.core'


class TestSetup(unittest.TestCase):

    layer = PLONEINTRANET_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_installed(self):
        ''' Check if the package is installed '''
        qi = api.portal.get_tool('portal_quickinstaller')
        self.assertTrue(qi.isProductInstalled('ploneintranet.core'))

    def test_browserlayer_installed(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertIn('IPloneIntranetCoreLayer', layers)

    def test_resources_installed(self):
        bundles = getUtility(IRegistry).collectionOfInterface(
            IResourceRegistry, prefix="plone.resources")
        self.assertIn(
            'resource-ploneintranet-core-stylesheets-minimal', bundles)


class UninstallTestCase(unittest.TestCase):

    layer = PLONEINTRANET_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer_removed(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertNotIn('IPloneIntranetCoreLayer', layers)

    def test_resources_removed(self):
        bundles = getUtility(IRegistry).collectionOfInterface(
            IResourceRegistry, prefix="plone.resources")
        self.assertNotIn(
            'resource-ploneintranet-core-stylesheets-minimal', bundles)
