# -*- coding: utf-8 -*-
from collective.workspace.interfaces import IWorkspace
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.app.testing.interfaces import SITE_OWNER_PASSWORD
from plone.testing import z2
from plone.testing.z2 import Browser
from ploneintranet.workspace.testing import \
    PLONEINTRANET_WORKSPACE_FUNCTIONAL_TESTING
from ploneintranet.workspace.testing import \
    PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING
from zope.annotation.interfaces import IAnnotations
import unittest2 as unittest


class BaseTestCase(unittest.TestCase):

    layer = PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.workspace_container = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacecontainer',
            'workspace-container',
            title='Workspace container'
        )
        self.request = self.portal.REQUEST

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
        IWorkspace(workspace).add_to_team(
            user=username,
            groups=groups,
        )
        # purge cache - only needed in tests since we're in same request
        IAnnotations(self.request)[('workspaces', username)] = None


class FunctionalBaseTestCase(BaseTestCase):

    layer = PLONEINTRANET_WORKSPACE_FUNCTIONAL_TESTING

    def setUp(self):
        super(FunctionalBaseTestCase, self).setUp()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False

    def browser_login_as_site_administrator(self):
        self.browser.open(self.portal.absolute_url() + '/login_form')
        self.browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
        self.browser.getControl(name='__ac_password').value = \
            SITE_OWNER_PASSWORD
        self.browser.getForm(id='login-panel').submit()
