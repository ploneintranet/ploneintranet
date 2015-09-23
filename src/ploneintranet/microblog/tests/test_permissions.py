import unittest2 as unittest
import time

from zope.component import queryUtility
from zope.interface import implements
from zope.interface import alsoProvides

from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View

from plone import api

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import login, logout

from ploneintranet.microblog.testing import\
    PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

import ploneintranet.microblog.statuscontainer
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.microblog.interfaces import IMicroblogContext
from ploneintranet.microblog.interfaces import IStatusUpdate
from ploneintranet.microblog.statusupdate import StatusUpdate


class MockStatusUpdate(StatusUpdate):
    """Override actual implementation with unittest features"""

    implements(IStatusUpdate)

    def __init__(self, text, userid, creator=None):
        StatusUpdate.__init__(self, text)
        self.userid = userid
        if creator:
            self.creator = creator
        else:
            self.creator = userid

    def _init_userid(self):
        pass

    def _init_creator(self):
        pass


class TestPermissions(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.mb_tool = queryUtility(IMicroblogTool)
        ploneintranet.microblog.statuscontainer.MAX_QUEUE_AGE = 0

    def tearDown(self):
        ploneintranet.microblog.statuscontainer.MAX_QUEUE_AGE = 1000

    def test_add_read_member(self):
        setRoles(self.portal, TEST_USER_ID, ('Member',))
        sa = MockStatusUpdate('test a', 'arnold')
        container = self.mb_tool
        container.add(sa)
        values = [x for x in container.values()]
        self.assertEqual([sa], values)

    def test_add_anon(self):
        setRoles(self.portal, TEST_USER_ID, ())
        sa = MockStatusUpdate('test a', 'arnold')
        container = self.mb_tool
        self.assertRaises(Unauthorized, container.add, sa)

    def test_read_anon(self):
        setRoles(self.portal, TEST_USER_ID, ())
        container = self.mb_tool
        self.assertRaises(Unauthorized, container.get, 0)
        self.assertEqual([x for x in container.values()], [])
        self.assertEqual([x for x in container.items()], [])
        self.assertEqual([x for x in container.keys()], [])


class TestMicroblogContextBlacklisting(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        workflowTool = getToolByName(self.portal, 'portal_workflow')
        workflowTool.setDefaultChain('simple_publication_workflow')
        workflowTool.updateRoleMappings()
        f1 = api.content.create(self.portal, 'Folder', 'f1', title=u'Folder 1')
        alsoProvides(f1, IMicroblogContext)
        f1.reindexObject()
        f2 = api.content.create(self.portal, 'Folder', 'f2', title=u'Folder 2')
        alsoProvides(f2, IMicroblogContext)
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

# more security testing in ploneintranet/suite/tests/test_microblog_security.py
