from email import message_from_string
import unittest
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from plone import api
from zope.component import getMultiAdapter
from ploneintranet.invitations.testing import \
    PLONEINTRANET_INVITATIONS_FUNCTIONAL_TESTING
from plone.testing.z2 import Browser


class TestInviteUser(unittest.TestCase):

    layer = PLONEINTRANET_INVITATIONS_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # Mock the mail host so we can test sending the email
        mockmailhost = MockMailHost('MailHost')

        if not hasattr(mockmailhost, 'smtp_host'):
            mockmailhost.smtp_host = 'localhost'

        self.portal.MailHost = mockmailhost
        sm = self.portal.getSiteManager()
        sm.registerUtility(component=mockmailhost, provided=IMailHost)

        self.mailhost = api.portal.get_tool('MailHost')

        self.portal._updateProperty('email_from_name', 'Portal Owner')
        self.portal._updateProperty('email_from_address', 'sender@example.org')

    def test_invite_user(self):
        email = 'test@test.com'
        view = getMultiAdapter((self.portal, self.request),
                               name=u'invite-user')
        token_id, token_url = view.invite_user(email)

        self.assertEqual(len(self.mailhost.messages), 1)
        msg = message_from_string(self.mailhost.messages[0])
        self.assertEqual(msg['To'], email)
        self.assertIn(token_url, msg.get_payload())
        self.mailhost.reset()

        # Commit so that the test browser sees these changes
        import transaction
        transaction.commit()

        browser = Browser(self.app)
        browser.open(token_url)

        # We should now be authenticated
        self.assertIn('userrole-authenticated', browser.contents,
                      'User was not authenticated after accepting token')
        self.assertIn(
            email, browser.contents,
            'Incorrect user authenticated after accepting token',
        )

        browser.open('%s/logout' % (
            self.portal.absolute_url(),
        ))
        browser.open('%s/@@accept-token/thisisnotatoken' % (
            self.portal.absolute_url(),
        ))
        self.assertNotIn('userrole-authenticated', browser.contents,
                         'Invalid token should not allow access')
