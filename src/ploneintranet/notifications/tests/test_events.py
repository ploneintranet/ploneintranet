# -*- coding: utf-8 -*-
from ..testing import PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING
from plonesocial.microblog.statusupdate import StatusUpdate
import unittest


class TestEvents(unittest.TestCase):

    layer = PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_fired(self):
        self.assertTrue(True)
        su = StatusUpdate(u'Test à')
        self.portal['plonesocial_microblog'].add(su)
