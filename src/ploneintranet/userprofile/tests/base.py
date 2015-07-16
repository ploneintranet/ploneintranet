import unittest2 as unittest

from plone import api as plone_api
from plone.testing import z2
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.app.testing import login
from plone.app.testing import logout

from ploneintranet.userprofile.testing import \
    PLONEINTRANET_USERPROFILE_INTEGRATION_TESTING


class BaseTestCase(unittest.TestCase):

    layer = PLONEINTRANET_USERPROFILE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST
        self.membrane_tool = plone_api.portal.get_tool('membrane_tool')
        self.profiles = self.portal.profiles

    def login(self, username):
        """
        helper method to login as specific user

        :param username: the username of the user to add to the group
        :type username: str
        :rtype: None

        """
        login(self.portal, username)

    def logout(self):
        """
        helper method to avoid importing the p.a.testing logout method
        """
        logout()

    def login_as_portal_owner(self):
        """
        helper method to login as site admin
        """
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)
