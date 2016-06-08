import unittest2 as unittest
from AccessControl import Unauthorized
from plone import api
from plone.app.testing import login, logout
from zope.component import queryUtility


from ploneintranet.suite.testing import\
    PLONEINTRANET_SUITE_FUNCTIONAL

from ploneintranet.microblog.interfaces import IMicroblogTool
# from ploneintranet.microblog.interfaces import IMicroblogContext
from ploneintranet.microblog import migration
from ploneintranet.microblog.statusupdate import StatusUpdate
from ploneintranet.microblog.utils import longkeysortreverse


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


class TestMicroblogAdminAccess(unittest.TestCase):
    """
    This test expans on microblog/tests/test_tool.py
    It uses the dynamic character of the suite-generated statusupdates,
    which have different ids on every test run, to extra rigourously
    check the statuscontainer accessors and filtering logic.
    """

    layer = PLONEINTRANET_SUITE_FUNCTIONAL

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.tool = queryUtility(IMicroblogTool)
        self.allkeys = [x for x in self.tool._status_mapping.keys()]

    def test_blacklist(self):
        """Admin should have full access"""
        self.assertIn('Manager', api.user.get_roles())
        self.assertEquals([], self.tool._blacklist_microblogcontext_uuids())

    def test_allowed(self):
        """Admin should have full access"""
        got = [x for x in self.tool.allowed_status_keys()]
        self.assertEquals(len(got), len(self.allkeys))
        self.assertEquals(got, self.allkeys)

    def test_via_keys_tag(self):
        """Admin should have full access"""
        got = [x for x in self.tool._keys_tag(
            None, self.tool.allowed_status_keys())]
        self.assertEquals(len(got), len(self.allkeys))
        self.assertEquals(got, self.allkeys)

    def test_keys_direct(self):
        """Admin should have full access"""
        got = sorted([x for x in self.tool.keys(limit=None)])
        self.assertEquals(len(got), len(self.allkeys))
        self.assertEquals(got, self.allkeys)

    def test_longkeysortreverse(self):
        """Admin access should not be impacted by longkeysortreverse"""
        self.assertIn('Manager', api.user.get_roles())
        got = sorted([x for x in longkeysortreverse(
            self.tool._status_mapping.keys(), None, None, None)])
        self.assertEquals(len(got), len(self.allkeys))
        self.assertEquals(got, self.allkeys)


class TestMicroblogMigration(unittest.TestCase):
    """
    Security filters resulted in missing statusupdates when using
    the old normal microblog accessors.

    This test uses the dynamic character of the suite-generated statusupdates,
    which have different ids on every test run, to extra rigourously
    verify the microblog migration logic.
    """

    layer = PLONEINTRANET_SUITE_FUNCTIONAL

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.tool = queryUtility(IMicroblogTool)
        self.workspace = self.portal.workspaces['open-market-committee']

    @unittest.skip("No reproducable problems in this migration")
    def test_enforce_parent_context(self):
        # setup
        for status in self.tool._status_mapping.values():
            if status.thread_id:
                del(status._microblog_context_uuid)
        # migrate - accessor not changed because no problem detected
        migration.enforce_parent_context(None)
        # verify
        for status in self.tool._status_mapping.values():
            if status.thread_id:
                parent = self.tool._get(status.thread_id)
                self.assertEquals(status._microblog_context_uuid,
                                  parent._microblog_context_uuid)

    def test_document_discussion_fields(self):
        """Verify migration hits raw accessors.
        """
        # setup
        for status in self.tool._status_mapping.values():
            del(status._content_context_uuid)
        # migrate
        migration.document_discussion_fields(None)
        # verify
        for status in self.tool._status_mapping.values():
            try:
                status._content_context_uuid
            # turn error into a test failure
            except AttributeError, exc:
                self.fail(exc)
