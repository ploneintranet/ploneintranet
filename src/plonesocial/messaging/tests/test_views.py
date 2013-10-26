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
        api.user.create(username='testuser1', email='what@ev.er',
                        password='testuser1')
        api.user.create(username='testuser2', email='what@ev.er',
                        password='testuser2')
        transaction.commit()

    def _create_message(self, from_, to, text, created=now):
        inboxes = self.portal.plonesocial_messaging
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

    def test_list_send_messages(self):
        self._create_message('testuser1', 'testuser2', 'Message Text',
                             created=now)
        self._login('testuser1', 'testuser1')
        self.browser.open(self.portal_url +
                          '/@@messaging-messages?user=testuser2')
        content = json.loads(self.browser.contents)
        self.assertEqual(len(content['messages']),
                         1)
        self.assertEqual(content['messages'][0]['text'],
                         'Message Text')
