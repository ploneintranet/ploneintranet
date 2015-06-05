# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from email import message_from_string
from plone import api
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from ploneintranet.invitations.testing import \
    PLONEINTRANET_INVITATIONS_FUNCTIONAL_TESTING
from zope.component import getMultiAdapter
from zope.component import getUtility
import unittest


class TestInviteUser(unittest.TestCase):

    layer = PLONEINTRANET_INVITATIONS_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # Mock the mail host so we can test sending the email
        # NEVER EVER IMPORT MOCKMAILHOST OUTSIDE OF SETUP!
        # IT WILL BREAK YOUR TEST_ISOLATION AND KILL YOUR FIRSTBORN
        from Products.CMFPlone.tests.utils import MockMailHost
        from Products.MailHost.interfaces import IMailHost
        mockmailhost = MockMailHost('MailHost')

        if not hasattr(mockmailhost, 'smtp_host'):
            mockmailhost.smtp_host = 'localhost'

        self.portal.MailHost = mockmailhost
        sm = self.portal.getSiteManager()
        sm.registerUtility(component=mockmailhost, provided=IMailHost)

        self.mailhost = api.portal.get_tool('MailHost')
        registry = getUtility(IRegistry)
        self.mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        self.mail_settings.email_from_name = u'Portal Owner'
        self.mail_settings.email_from_address = 'sender@example.org'

        self.browser = Browser(self.app)
        self.browser.handleErrors = False

        # Commit so that the test browser sees these changes
        import transaction
        transaction.commit()

    def test_invite_user(self):
        email = 'test@test.com'
        view = getMultiAdapter(
            (self.portal, self.request),
            name=u'ploneintranet-invitations-invite-user',
        )
        token_id, token_url = view.invite_user(email)

        self.assertEqual(len(self.mailhost.messages), 1)
        msg = message_from_string(self.mailhost.messages[0])
        self.assertEqual(msg['To'], email)
        self.assertIn(token_url, msg.get_payload())
        self.mailhost.reset()

        # Commit so that the test browser sees these changes
        import transaction
        transaction.commit()

        self.browser.open(token_url)

        # We should now be authenticated
        self.assertIn('userrole-authenticated', self.browser.contents,
                      'User was not authenticated after accepting token')
        self.assertIn(
            email, self.browser.contents,
            'Incorrect user authenticated after accepting token',
        )

        # Logout
        self.browser.open('%s/logout' % (
            self.portal.absolute_url(),
        ))

        # A token is valid only one time.
        self.browser.open(token_url)

        # We should NOT be authenticated
        self.assertIn('userrole-anonymous', self.browser.contents,
                      'User was authenticated')

        # Try an invalid token
        self.browser.open('%s/@@accept-token/thisisnotatoken' % (
            self.portal.absolute_url(),
        ))
        self.assertNotIn('userrole-authenticated', self.browser.contents,
                         'Invalid token should not allow access')

        # No token
        with self.assertRaises(KeyError):
            self.browser.open('%s/@@accept-token' % (
                self.portal.absolute_url(),
            ))

    def test_invite_user_form(self):
        email = 'test@test.com'

        self.browser.open(self.portal.absolute_url() + '/login_form')
        self.browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
        self.browser.getControl(name='__ac_password').value = \
            SITE_OWNER_PASSWORD
        self.browser.getControl(name='submit').click()

        self.browser.open('%s/@@ploneintranet-invitations-invite-user' %
                          self.portal.absolute_url())
        self.browser.getControl(name='email').value = email
        self.browser.getControl(name='send').click()

        self.assertEqual(len(self.mailhost.messages), 1)
        msg = message_from_string(self.mailhost.messages[0])
        self.assertEqual(msg['To'], email)
