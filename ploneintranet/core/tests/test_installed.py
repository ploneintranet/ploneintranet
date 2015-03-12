# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.core.testing import PLONEINTRANET_CORE_INTEGRATION_TESTING
import unittest2 as unittest


class TestSetup(unittest.TestCase):

    layer = PLONEINTRANET_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_installed(self):
        ''' Check if the package is installed '''
        qi = api.portal.get_tool('portal_quickinstaller')
        self.assertTrue(qi.isProductInstalled('ploneintranet.core'))
