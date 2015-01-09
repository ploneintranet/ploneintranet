# -*- coding: utf-8 -*-
from plonesocial.network.browser.author import AuthorView
from plonesocial.network.browser.interfaces import IPlonesocialNetworkLayer
from plonesocial.network.testing import FunctionalTestCase
from plonesocial.network.testing import IntegrationTestCase
from zope.interface import directlyProvides
import unittest2 as unittest


class TestViews(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        directlyProvides(self.request, IPlonesocialNetworkLayer)

    def test_author(self):
        ''' We have to be sure that we get our custom author zope view and
        not the FSControllerPageTemplate
        This is going to fail in Plone4
        '''
        author_view = self.portal.restrictedTraverse('author')
        self.assertIsInstance(author_view, AuthorView)
