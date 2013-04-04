import unittest2 as unittest
from zope.component import queryUtility
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName

from plone.app.testing import TEST_USER_ID, setRoles
from plone.app.testing import login, logout

from plonesocial.microblog.testing import \
    PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

from plonesocial.microblog.interfaces import IStatusContainer
from plonesocial.microblog.interfaces import IMicroblogTool
from plonesocial.microblog.statusupdate import StatusUpdate


class TestMicroblogTool(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_tool_available(self):
        tool = queryUtility(IMicroblogTool)
        self.assertTrue(IStatusContainer.providedBy(tool))


class TestMicroblogToolContextBlacklisting(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        workflowTool = getToolByName(self.portal, 'portal_workflow')
        workflowTool.setDefaultChain('simple_publication_workflow')
        workflowTool.updateRoleMappings()
        self.portal.invokeFactory('Folder', 'f1', title=u"Folder 1")
        f1 = self.portal['f1']
        self.portal.invokeFactory('Folder', 'f2', title=u"Folder 2")
        f2 = self.portal['f2']

        workflowTool.doActionFor(f2, 'publish')
        self.assertEqual(workflowTool.getInfoFor(f1, 'review_state'),
                         'private')
        self.assertEqual(workflowTool.getInfoFor(f2, 'review_state'),
                         'published')

        tool = queryUtility(IMicroblogTool)
        su1 = StatusUpdate('test #foo', f1)
        tool.add(su1)
        self.su2 = su2 = StatusUpdate('test #foo', f2)
        tool.add(su2)
        # the tool is queued
        tool.flush_queue()

        # set up new user and switch to that user
        acl_users = getToolByName(self.portal, 'acl_users')
        acl_users.userFolderAddUser('user1', 'secret', ['Member'], [])
        logout()

    def test_allowed_status(self):
        """The base implementation does not test access controls.
        The tool should provide those.
        """
        # verify setup: only f2 is accessible for Member
        login(self.portal, 'user1')
        sm = getSecurityManager()
        user = getSecurityManager().getUser()
        self.assertEqual(user.getId(), 'user1')
        self.assertFalse(sm.checkPermission(View, self.portal['f1']))
        self.assertTrue(sm.checkPermission(View, self.portal['f2']))

        # and now finally the actual test
        tool = queryUtility(IMicroblogTool)
        self.assertEqual(list(tool.values()), [self.su2])
