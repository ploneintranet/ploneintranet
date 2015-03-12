import time
import unittest2 as unittest
from zope.interface import directlyProvides
from zope.component import queryUtility

from AccessControl import getSecurityManager
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName

from plone import api
from plone.app.testing import TEST_USER_ID, setRoles
from plone.app.testing import login, logout

from ploneintranet.microblog.testing import \
    PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

from ploneintranet.microblog.interfaces import IStatusContainer
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.microblog.interfaces import IMicroblogContext
from ploneintranet.microblog.statusupdate import StatusUpdate


class TestMicroblogTool(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_tool_available(self):
        tool = queryUtility(IMicroblogTool)
        self.assertTrue(IStatusContainer.providedBy(tool))

    def test_tool_uninstalled(self):
        qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=['ploneintranet.microblog'])
        self.assertNotIn('ploneintranet_microblog', self.portal)
        tool = queryUtility(IMicroblogTool, None)
        self.assertIsNone(tool)


class TestMicroblogToolContextBlacklisting(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        workflowTool = getToolByName(self.portal, 'portal_workflow')
        workflowTool.setDefaultChain('simple_publication_workflow')
        workflowTool.updateRoleMappings()
        f1 = api.content.create(self.portal, 'Folder', 'f1', title=u'Folder 1')
        directlyProvides(f1, IMicroblogContext)
        f1.reindexObject()
        f2 = api.content.create(self.portal, 'Folder', 'f2', title=u'Folder 2')
        directlyProvides(f2, IMicroblogContext)
        f2.reindexObject()

        api.content.transition(f2, 'publish')
        self.assertEqual(api.content.get_state(f1), 'private')
        self.assertEqual(api.content.get_state(f2), 'published')

        tool = queryUtility(IMicroblogTool)
        self.su1 = su1 = StatusUpdate('test #foo', f1)
        tool.add(su1)
        self.su2 = su2 = StatusUpdate('test #foo', f2)
        tool.add(su2)
        # the tool is queued
        tool.flush_queue()

        # set up new user
        api.user.create('user1@foo.bar', username='user1', password='secret')

    def tearDown(self):
        time.sleep(1)  # allow for thread cleanup

    def test_allowed_status_user(self):
        """The base implementation does not test access controls.
        The tool should provide those.
        """
        # verify setup: only f2 is accessible for Member
        logout()
        login(self.portal, 'user1')
        sm = getSecurityManager()
        user = api.user.get_current()
        self.assertEqual(user.getId(), 'user1')
        self.assertFalse(sm.checkPermission(View, self.portal['f1']))
        self.assertTrue(sm.checkPermission(View, self.portal['f2']))

        # and now finally the actual test
        tool = queryUtility(IMicroblogTool)
        self.assertEqual(list(tool.values()), [self.su2])

    def test_allowed_status_manager(self):
        """The default test user owns both IMicroblogContexts
        thus has access to both."""
        tool = queryUtility(IMicroblogTool)
        self.assertEqual(list(tool.values()), [self.su2, self.su1])
