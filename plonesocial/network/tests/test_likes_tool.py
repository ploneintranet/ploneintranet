# -*- coding: utf-8 -*-
from plone import api
from plonesocial.network.interfaces import ILikesContainer
from plonesocial.network.interfaces import ILikesTool
from plonesocial.network.testing import FunctionalTestCase
from plonesocial.network.testing import IntegrationTestCase
from zope.component import queryUtility
import unittest2 as unittest


class TestLikesTool(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_likes_tool_available(self):
        tool = queryUtility(ILikesTool)
        self.assertTrue(ILikesContainer.providedBy(tool))

    def test_likes_tool_uninstalled(self):
        qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=['plonesocial.network'])
        self.assertNotIn('plonesocial_likes', self.portal)
        tool = queryUtility(ILikesTool, None)
        self.assertIsNone(tool)
