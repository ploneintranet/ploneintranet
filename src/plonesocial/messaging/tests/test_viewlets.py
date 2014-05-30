# -*- coding: utf-8 -*-
from ..testing import PLONESOCIAL_MESSAGING_INTEGRATION_TESTING
from datetime import datetime
from plone import api
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME
from plonesocial.messaging.browser.viewlets import NotificationsViewlet
from plonesocial.messaging.interfaces import IMessagingLocator
from zope.component import getUtility

import unittest


class TestViewlet(unittest.TestCase):

    layer = PLONESOCIAL_MESSAGING_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_available(self):
        ALICE = 'alice'
        api.user.create(email='alice@plone.org', username=ALICE)

        # no message exchange yet; viewlet is not available
        viewlet = NotificationsViewlet(self.portal, self.request, None)
        self.assertFalse(viewlet.available())

        locator = getUtility(IMessagingLocator)
        inboxes = locator.get_inboxes()
        # test user sends a message to Alice
        inboxes.send_message(
            TEST_USER_NAME, ALICE, 'Oi!', created=datetime.now())

        # Alice has a new message; viewlet is available when she logs in
        login(self.portal, ALICE)
        self.assertTrue(viewlet.available())
        inbox = inboxes[ALICE]
        conversation = inbox[TEST_USER_NAME]
        conversation.mark_read()
        # she reads the message; viewlet is not available
        self.assertFalse(viewlet.available())

        # she reply the message; viewlet should not be available for her
        inboxes.send_message(
            ALICE, TEST_USER_NAME, 'Tudo bom?', created=datetime.now())
        # FIXME: https://github.com/cosent/plonesocial.messaging/issues/4
        self.assertFalse(viewlet.available())

        # test user has a new message; viewlet is available when he logs in
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(viewlet.available())
        inbox = inboxes[TEST_USER_NAME]
        conversation = inbox[ALICE]
        conversation.mark_read()
        # he reads the message; viewlet is not available
        self.assertFalse(viewlet.available())
