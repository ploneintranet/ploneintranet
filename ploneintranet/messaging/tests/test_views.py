# -*- coding: utf-8 -*-
from datetime import datetime
from plone.app.testing.helpers import login
from plone.testing.z2 import Browser
from ploneintranet.messaging.testing import \
    PLONEINTRANET_MESSAGING_FUNCTIONAL_TESTING

import json
import plone.api as api
import transaction
import unittest

now = datetime.now()


class TestJsonView(unittest.TestCase):

    layer = PLONEINTRANET_MESSAGING_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_set_contenttype(self):
        from ploneintranet.messaging.browser.messaging import JsonView
        view = JsonView(None, self.request)
        self.assertEqual(
            view.request.response.headers['content-type'], 'application/json')

    def test_json_error(self):
        from ploneintranet.messaging.browser.messaging import JsonView
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

    layer = PLONEINTRANET_MESSAGING_FUNCTIONAL_TESTING

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
        inboxes = self.portal.ploneintranet_messaging
        inboxes.send_message(from_, to, text, created=created)
        transaction.commit()

    def _conversations(self, username):
        inboxes = self.portal.ploneintranet_messaging
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
        self._create_message(
            'testuser1', 'testuser2', 'Message Text', created=now)
        self._login('testuser1', 'testuser1')
        self.browser.open(
            self.portal_url + '/@@messaging-messages?user=testuser2')
        content = json.loads(self.browser.contents)
        self.assertEqual(len(content['messages']), 1)
        message = content['messages'][0]
        self.assertEqual(message['text'], 'Message Text')
        self.assertEqual(message['sender'], 'testuser1')
        self.assertEqual(message['recipient'], 'testuser2')
        self.assertEqual(message['text'], 'Message Text')
        self.assertEqual(message['created'], now.isoformat())
        self.assertTrue(isinstance(message['uid'], (int, long)))

    def test_delete_message_no_testbrowser(self):
        self._create_message(
            'testuser1', 'testuser2', 'Message Text', created=now)
        inbox = self.portal.ploneintranet_messaging['testuser1']
        message_id = inbox['testuser2'].keys()[0]
        self.request.form = {
            'user': 'testuser2',
            'message': str(message_id),
        }
        login(self.portal, 'testuser1')
        view = api.content.get_view(
            context=self.portal,
            request=self.request,
            name='delete-message')
        content = json.loads(view())
        self.assertEqual(content['result'], True)
        self.assertIn(str(message_id), content['message'])
        self.assertNotIn(message_id, inbox['testuser2'])
        self.request.form = {}

    @unittest.skip('After the mechanize call the item seems to get'
                   'resurrected. Persistence issue?')
    def test_delete_message(self):
        self._create_message(
            'testuser1', 'testuser2', 'Message Text', created=now)
        inbox = self.portal.ploneintranet_messaging['testuser1']
        message_id = inbox['testuser2'].keys()[0]
        self._login('testuser1', 'testuser1')
        self.browser.open(self.portal_url +
                          '/@@delete-message?user=testuser2&message=' +
                          str(message_id))
        content = json.loads(self.browser.contents)
        self.assertEqual(content['result'], True)
        self.assertIn(str(message_id), content['message'])
        self.assertNotIn(message_id, inbox['testuser2'])

    def test_list_conversations(self):
        self._create_message('testuser1', 'testuser2', 'Message Text',
                             created=now)
        self._login('testuser1', 'testuser1')
        self.browser.open(self.portal_url + '/@@messaging-conversations')
        content = json.loads(self.browser.contents)
        self.assertEqual(len(content['conversations']), 1)
        self.assertEqual(content['conversations'][0]['username'], 'testuser2')
        self.assertEqual(
            content['conversations'][0]['fullname'], 'Test User 2')

    def test_delete_conversation_no_testbrowser(self):
        self._create_message(
            'testuser1', 'testuser2', 'Message Text', created=now)
        self.assertEqual(len(self._conversations('testuser1')), 1)
        self.request.form = {
            'user': 'testuser2',
        }
        login(self.portal, 'testuser1')
        view = api.content.get_view(
            context=self.portal,
            request=self.request,
            name='delete-conversation')
        content = json.loads(view())
        self.assertEqual(content, {u'result': True})
        self.assertEqual(len(self._conversations('testuser1')), 0)
        self.request.form = {}

    @unittest.skip('After the mechanize call the item seems to get'
                   'resurrected. Persistence issue?')
    def test_delete_conversation(self):
        self._create_message(
            'testuser1', 'testuser2', 'Message Text', created=now)
        self.assertEqual(len(self._conversations('testuser1')), 1)
        self._login('testuser1', 'testuser1')
        self.browser.open(
            self.portal_url + '/@@delete-conversation?user=testuser2')
        content = json.loads(self.browser.contents)
        self.assertEqual(content, {u'result': True})
        self.assertEqual(len(self._conversations('testuser1')), 0)


class TestYourMessagesView(unittest.TestCase):

    layer = PLONEINTRANET_MESSAGING_FUNCTIONAL_TESTING

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
        inboxes = self.portal.ploneintranet_messaging
        inboxes.send_message(from_, to, text, created=created)
        transaction.commit()

    def _login(self, username, password):
        # Go admin
        self.browser.open(self.portal_url + '/login_form')
        self.browser.getControl(name='__ac_name').value = username
        self.browser.getControl(name='__ac_password').value = password
        self.browser.getControl(name='submit').click()

    def _logout(self):
        self.browser.open(self.portal_url + '/logout')

    def test_inbox_in_actions(self):
        # we've added an inbox link to the actions.xml,
        # It should appear once logged in.
        self.browser.open(self.portal_url)
        self.assertNotIn(
            'personaltools-plone_social_menu', self.browser.contents)
        self._login('testuser1', 'testuser1')
        self.browser.open(self.portal_url)
        self.assertIn(
            'personaltools-plone_social_menu', self.browser.contents)

    @unittest.expectedFailure
    def test_unread_messages(self):
        # lets return a count to see if there are any unread messages
        self.browser.open(self.portal_url + '/@@your-messages')
        # lets checked when not logged in
        self.assertNotIn('id="your-messages"', self.browser.contents)
        # lets login and create a message
        self._login('testuser1', 'testuser1')
        self._create_message(
            'testuser2', 'testuser1', 'Message Text', created=now)
        self.browser.open(self.portal_url + '/@@your-messages')
        self.assertIn('id="your-messages"', self.browser.contents)
        self.assertIn('1', self.browser.contents)
        self._logout()
        self._login('testuser2', 'testuser2')
        self.browser.open(self.portal_url + '/@@your-messages')
        self.assertNotIn('id="your-messages"', self.browser.contents)
        self.assertNotIn('1', self.browser.contents)
