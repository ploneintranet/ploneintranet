from collective.workspace.interfaces import IWorkspace
import unittest2 as unittest
from plone.testing import z2
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.app.testing import login
from Products.CMFCore.utils import getToolByName
from ploneintranet.workspace.testing import \
    PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING
from zope.annotation.interfaces import IAnnotations


class BaseTestCase(unittest.TestCase):

    layer = PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        self.request = self.portal.REQUEST

    def login(self, username):
        """
        helper method to login as specific user

        :param username: the username of the user to add to the group
        :type username: str
        :rtype: None

        """
        login(self.portal, username)

    def login_as_portal_owner(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)

    def add_user_to_workspace(self, username, workspace, groups=None):
        """
        helper method which adds a user to team and then clears the cache

        :param username: the username of the user to add to the group
        :type username: str
        :param workspace: the workspace to add this user
        :type workspace: ploneintranet.workspace.workspacefolder
        :param groups: the groups to which this user should be added
        :type groups: set
        :rtype: None

        """
        if groups is None:
            groups = []

        IWorkspace(workspace).add_to_team(
            user=username,
            groups=groups,
        )
        IAnnotations(self.request)[('workspaces', username)] = None
