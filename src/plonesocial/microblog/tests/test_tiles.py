# -*- coding: utf-8 -*-
from plone import api
from plonesocial.microblog.browser.interfaces import IPlonesocialMicroblogLayer
from plonesocial.microblog.testing import (
    PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING
)
from zope.interface import alsoProvides
import unittest2 as unittest


class TestSetup(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, IPlonesocialMicroblogLayer)

    def test_newpostbox_tile(self):
        ''' This will test the existence of the newpostbox.tile
        and its functionality
        '''
        tile = api.content.get_view(
            'newpostbox.tile',
            self.portal,
            self.request
        )
        tile()
