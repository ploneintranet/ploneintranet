# -*- coding: utf-8 -*-
from ..testing import PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING
from plone import api
from plonesocial.microblog.statusupdate import StatusUpdate
from unittest import TestCase


class TestEvents(TestCase):

    layer = PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_on_status_update(self):
        self.assertTrue(True)
        # When we add a status update
        pm = api.portal.get_tool('plonesocial_microblog')
        su = StatusUpdate(u'Test à')
        pm.add(su)
        # an events creates a notification for that user
        pin = api.portal.get_tool('ploneintranet_notifications')
        user = api.user.get_current()
        queue = pin.get_user_queue(user)
        self.assertTrue(len(queue), 1)
        message = queue[0]
        self.assertEqual(message.predicate, 'StatusUpdate')
        self.assertEqual(message.obj['creator'], 'test-user')
        self.assertDictEqual(
            message.actors,
            {'email': '', 'fullname': '', 'userid': 'test_user_1_'}
        )
