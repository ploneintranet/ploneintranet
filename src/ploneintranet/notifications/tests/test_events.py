# -*- coding: utf-8 -*-
from ..testing import PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING
from plone import api
from plone.app.testing.interfaces import TEST_USER_PASSWORD
from plone.app.testing.interfaces import TEST_USER_ROLES
from plonesocial.microblog.statusupdate import StatusUpdate
from unittest import TestCase


class TestEvents(TestCase):

    layer = PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        # add another user
        self.pas = self.layer['portal']['acl_users']
        # We need another user
        self.pas.source_users.addUser(
            'test_user_2_',
            'test_user_2_',
            TEST_USER_PASSWORD
        )
        for role in TEST_USER_ROLES:
            self.pas.portal_role_manager.doAssignRoleToPrincipal('test_user_2_', role)  # noqa
        with api.env.adopt_user('test_user_2_'):
            api.user.get('test_user_2_').setProperties({
                'email': 'marielle@sjogren.se',
                'fullname': 'Marielle Sjögren',
            })  # randomly generated

    def test_on_status_update(self):
        ''' A user makes a status update and we get a notification message
        '''
        # When we add a status update
        with api.env.adopt_user('test_user_2_'):
            su = StatusUpdate(u'Test à')
            pm = api.portal.get_tool('plonesocial_microblog')
            pm.add(su)
        # an events creates a notification for that user
        pin = api.portal.get_tool('ploneintranet_notifications')
        for user in api.user.get_users():
            queue = pin.get_user_queue(user)
            self.assertTrue(len(queue), 1)
            message = queue[0]
            self.assertEqual(message.predicate, 'StatusUpdate')
            self.assertEqual(message.obj['creator'], 'test_user_2_')
            self.assertDictEqual(
                message.actors,
                {
                    'email': 'marielle@sjogren.se',
                    'fullname': 'Marielle Sjögren',
                    'userid': 'test_user_2_',
                }
            )
