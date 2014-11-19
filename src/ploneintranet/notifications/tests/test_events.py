# -*- coding: utf-8 -*-
from ploneintranet.notifications.testing import PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING  # noqa
import unittest


class TestEvents(unittest.TestCase):

    layer = PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_dummy(self):
        self.assertTrue(True)
