# -*- coding: utf-8 -*-
from datetime import datetime
import json
import unittest2 as unittest

import plone.api as api
from plone.testing.z2 import Browser

from plonesocial.messaging.testing import \
    PLONESOCIAL_MESSAGING_FUNCTIONAL_TESTING

import transaction

now = datetime.now()


class TestJsonView(unittest.TestCase):

    layer = PLONESOCIAL_MESSAGING_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_set_contenttype(self):
        from plonesocial.messaging.browser.messaging import JsonView
        view = JsonView(None, self.request)
        self.assertEqual(view.request.response.headers['content-type'],
                         'application/json')

    def test_json_error(self):
        from plonesocial.messaging.browser.messaging import JsonView
        view = JsonView(None, self.request)
        content_string = view.error(500, 'Error Message')

        # check the body with the json response
        content = json.loads(content_string)
        self.assertEqual(content['error']['code'], 500)
        self.assertEqual(content['error']['reason'], 'Error Message')

        # check the http response
        self.assertEqual(self.request.response.status, 500)
        self.assertEqual(self.request.response.errmsg, 'Error Message')


class TestAjaxViews(unittest.TestCase):

    layer = PLONESOCIAL_MESSAGING_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.request = self.layer['request']
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        api.user.create(username='testuser1', email='what@ev.er',
                        password='testuser1',
                        properties={'fullname': 'Test User 1'})
        api.user.create(username='testuser2', email='what@ev.er',
                        password='testuser2',
                        properties={'fullname': 'Test User 2'})
        transaction.commit()

    def _create_message(self, from_, to, text, created=now):
        inboxes = self.portal.plonesocial_messaging
        inboxes.send_message(from_, to, text, created=created)
        transaction.commit()

    def _conversations(self, username):
        inboxes = self.portal.plonesocial_messaging
        return [c for c in inboxes[username].get_conversations()]

    def _login(self, username, password):
         # Go admin
        self.browser.open(self.portal_url + '/login_form')
        self.browser.getControl(name='__ac_name').value = username
        self.browser.getControl(name='__ac_password').value = password
        self.browser.getControl(name='submit').click()

    def _logout(self):
        self.browser.open(self.portal_url + '/logout')

    def test_list_send_messages(self):
        self._create_message('testuser1', 'testuser2', 'Message Text',
                             created=now)
        self._login('testuser1', 'testuser1')
        self.browser.open(self.portal_url +
                          '/@@messaging-messages?user=testuser2')
        content = json.loads(self.browser.contents)
        self.assertEqual(len(content['messages']),
                         1)
        message = content['messages'][0]
        self.assertEqual(message['text'], 'Message Text')
        self.assertEqual(message['sender'], 'testuser1')
        self.assertEqual(message['recipient'], 'testuser2')
        self.assertEqual(message['text'], 'Message Text')
        self.assertEqual(message['created'], now.isoformat())
        self.assertTrue(isinstance(message['uid'], int))

    def test_delete_message(self):
        self._create_message('testuser1', 'testuser2', 'Message Text',
                             created=now)
        inbox = self.portal.plonesocial_messaging['testuser1']
        message_id = inbox['testuser2'].keys()[0]
        self._login('testuser1', 'testuser1')
        self.browser.open(self.portal_url +
                          '/@@delete-message?user=testuser2&message=' +
                          str(message_id))
        content = json.loads(self.browser.contents)
        self.assertEqual(content['result'], True)
        self.assertTrue(str(message_id) in content['message'])
        self.assertTrue(message_id not in inbox['testuser2'])

    def test_list_conversations(self):
        self._create_message('testuser1', 'testuser2', 'Message Text',
                             created=now)
        self._login('testuser1', 'testuser1')
        self.browser.open(self.portal_url +
                          '/@@messaging-conversations')
        content = json.loads(self.browser.contents)
        self.assertEqual(len(content['conversations']),
                         1)
        self.assertEqual(content['conversations'][0]['username'],
                         'testuser2')
        self.assertEqual(content['conversations'][0]['fullname'],
                         'Test User 2')

    def test_delete_conversation(self):
        self._create_message('testuser1', 'testuser2', 'Message Text',
                             created=now)
        self.assertEqual(len(self._conversations('testuser1')), 1)
        self._login('testuser1', 'testuser1')
        self.browser.open(self.portal_url +
                          '/@@delete-conversation?user=testuser2')
        content = json.loads(self.browser.contents)
        self.assertEqual(content, {u'result': True})
        self.assertEqual(len(self._conversations('testuser1')), 0)
