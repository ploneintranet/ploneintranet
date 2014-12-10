# -*- coding: utf-8 -*-
from ..testing import PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING
from datetime import datetime
from plone import api
from plone.app.testing.interfaces import TEST_USER_PASSWORD
from plone.app.testing.interfaces import TEST_USER_ROLES
from plonesocial.microblog.statusupdate import StatusUpdate
import unittest


class TestAdapters(unittest.TestCase):

    layer = PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        # add another user
        self.pas = self.layer['portal']['acl_users']
        # We need another user
        self.pas.source_users.addUser(
            'test_user_adapters_',
            'test_user_adapters_',
            TEST_USER_PASSWORD
        )
        for role in TEST_USER_ROLES:
            self.pas.portal_role_manager.doAssignRoleToPrincipal('test_user_adapters_', role)  # noqa
            self.pas.portal_role_manager.doAssignRoleToPrincipal('test_user_adapters_', 'Contributor')  # noqa
        with api.env.adopt_user('test_user_adapters_'):
            api.user.get('test_user_adapters_').setProperties({
                'email': 'kelly@sjogren.se',
                'fullname': 'Kelly Sjögren',
            })  # randomly generated

    def test_page(self):
        ''' Let's try to create a page and inspect the created adapter
        '''
        with api.env.adopt_user('test_user_adapters_'):
            api.content.create(self.portal, 'Document', 'page1')

        pin = api.portal.get_tool('ploneintranet_notifications')
        message = pin.get_user_queue(api.user.get('test_user_adapters_'))[-1]

        self.assertEqual(message.predicate, 'GLOBAL_NOTICE')

        self.assertDictEqual(
            message.actors[0], {
                'fullname': 'Kelly Sj\xc3\xb6gren',
                'userid': 'test_user_adapters_',
                'email': 'kelly@sjogren.se'
            }
        )

        self.assertEqual(message.obj['id'], 'page1')
        self.assertEqual(message.obj['title'], 'page1')
        self.assertEqual(message.obj['url'], 'plone/page1')
        self.assertEqual(message.obj['read'], False)
        self.assertIsInstance(message.obj['message_last_modification_date'], datetime)  # noqa

    def test_status_update(self):
        ''' Let's try to create a status_update and inspect the created adapter
        '''
        with api.env.adopt_user('test_user_adapters_'):
            su = StatusUpdate(u'Test à')
            pm = api.portal.get_tool('plonesocial_microblog')
            pm.add(su)

        pin = api.portal.get_tool('ploneintranet_notifications')
        message = pin.get_user_queue(api.user.get('test_user_adapters_'))[-1]

        self.assertEqual(message.predicate, 'STATUS_UPDATE')

        self.assertDictEqual(
            message.actors[0], {
                'fullname': 'Kelly Sj\xc3\xb6gren',
                'userid': 'test_user_adapters_',
                'email': 'kelly@sjogren.se'
            }
        )

        self.assertIsInstance(message.obj['id'], long)
        self.assertEqual(message.obj['title'], u'Test \xe0')
        self.assertEqual(message.obj['url'], 'plone/@@stream/network')
        self.assertEqual(message.obj['read'], False)
        self.assertIsInstance(message.obj['message_last_modification_date'], datetime)  # noqa
