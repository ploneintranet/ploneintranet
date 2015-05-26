import unittest2 as unittest
from AccessControl import Unauthorized
from plone.app.testing import login, logout
from zope.component import queryUtility


from ploneintranet.suite.testing import\
    PLONEINTRANET_SUITE_FUNCTIONAL

from ploneintranet.microblog.interfaces import IMicroblogTool
# from ploneintranet.microblog.interfaces import IMicroblogContext
from ploneintranet.microblog.statusupdate import StatusUpdate


class TestMicroblogSecurity(unittest.TestCase):
    """
    This test expans on microblog/tests/test_tool.py
    It needs complex test fixures which are not available in microblog.
    Instead we use the existing suite test fixture.
    """

    layer = PLONEINTRANET_SUITE_FUNCTIONAL

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.tool = queryUtility(IMicroblogTool)
        self.workspace = self.portal.workspaces['open-market-committee']

    def test_member_allowed_write(self):
        login(self.portal, 'allan_neece')
        su1 = StatusUpdate('test #foo')
        su2 = StatusUpdate('test #foo', self.workspace)
        self.tool.add(su1)
        # should NOT raise Unauthorized
        self.tool.add(su2)

    def test_nonmember_unauthorized_write(self):
        login(self.portal, 'alice_lindstrom')
        su1 = StatusUpdate('test #foo')
        su2 = StatusUpdate('test #foo', self.workspace)
        self.tool.add(su1)
        # should raise, since Alice is not a member of the workspace
        self.assertRaises(Unauthorized, self.tool.add, su2)

    def test_nonmember_unauthorized_get(self):
        login(self.portal, 'allan_neece')
        su = StatusUpdate('test #foo', self.workspace)
        self.tool.add(su)
        logout()
        login(self.portal, 'alice_lindstrom')
        # should raise, since Alice is not a member of the workspace
        self.assertRaises(Unauthorized, self.tool.get, su.id)

    def test_nonmember_secured_read(self):
        login(self.portal, 'allan_neece')
        su = StatusUpdate('test #foo', self.workspace)
        self.tool.add(su)
        logout()
        login(self.portal, 'alice_lindstrom')
        # silently filters all you're not allowed to see
        self.assertFalse(su.id in self.tool.keys())
