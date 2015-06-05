# coding=utf-8
"""
Tests for ploneintranet.workspace forms
"""
#import re

# from Products.MailHost.interfaces import IMailHost
# from collective.workspace.interfaces import IWorkspace
# from email import message_from_string
# from zope.event import notify
# from zope.interface import Interface
# from zope.publisher.interfaces.browser import IBrowserRequest
# from zope.component import provideAdapter
from plone import api
# from plone.testing.z2 import Browser
# from ploneintranet.invitations.events import TokenAccepted
from ploneintranet.workspace.tests.base import BaseTestCase
# from ploneintranet.workspace.browser.forms import InviteForm
# from ploneintranet.workspace.browser.forms import TransferMembershipForm
# from z3c.form.interfaces import IFormLayer
from zope.publisher.browser import TestRequest
# from zope.interface import alsoProvides
# from zope.annotation.interfaces import IAttributeAnnotatable
#from ploneintranet.workspace.testing import \
#    PLONEINTRANET_WORKSPACE_FUNCTIONAL_TESTING
from ploneintranet.workspace.browser.tiles.workspaces import my_workspaces

class TestWorkspaceSort(BaseTestCase):

    def test_workspace_sort(self):
        self.login_as_portal_owner()
        request = self.layer['request']
        
        for sort_by in ('alphabet', 'newest', 'activity'):
            request.sort = sort_by
            ws_container = api.content.get_view(
                name='workspaces.html',
                context=self.portal.workspaces,
                request = request)
            self.assertEqual(len(ws_container.sort_options()),3)
            self.assertEqual(ws_container.sort_options()[0]['value'], sort_by)

    def test_my_workspaces(self):
        api.content.create(
            self.portal.workspaces,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
        ws = my_workspaces(self.portal.workspaces)
        self.assertEqual(len(ws) > 0, True)
