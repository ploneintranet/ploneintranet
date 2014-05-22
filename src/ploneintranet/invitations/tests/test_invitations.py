import unittest
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

    def test_invite_user(self):
        view = getMultiAdapter((self.portal, self.request),
                               name=u'invite-user')
        token_id, token_url = view.invite_user('bob@test.com')
        # Commit so that the test browser sees these changes
        import transaction
        transaction.commit()

        browser = Browser(self.app)
        browser.open(token_url)

        # We should now be authenticated
        self.assertIn('userrole-authenticated', browser.contents)
        self.assertIn('bob@test.com', browser.contents)

        browser.open('%s/logout' % (
            self.portal.absolute_url(),
        ))
        browser.open('%s/@@accept-token/thisisnotatoken' % (
            self.portal.absolute_url(),
        ))
        self.assertNotIn('userrole-authenticated', browser.contents)
