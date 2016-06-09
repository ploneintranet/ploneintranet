import unittest2 as unittest
from zope.interface import implements

from ploneintranet.microblog.interfaces import IStatusContainer
from ploneintranet.microblog import statuscontainer
from ploneintranet.microblog import statusupdate


class StatusContainer(statuscontainer.BaseStatusContainer):
    """Override actual implementation with unittest features"""

    implements(IStatusContainer)

    def _check_add_permission(self, statusupdate):
        pass

    def _blacklist_microblogcontext_uuids(self):
        return []


class StatusUpdate(statusupdate.StatusUpdate):
    """Override actual implementation with unittest features"""

    def _init_userid(self):
        pass

    def _init_creator(self):
        pass


class TestStatusContainer_Tags(unittest.TestCase):

    def setUp(self):
        self.container = StatusContainer()
        self.sa = StatusUpdate('test', tags=['a', 'd'])
        self.sa.userid = 'arnold'
        self.container.add(self.sa)
        self.sb = StatusUpdate('test', tags=['b', 'e'])
        self.sb.userid = 'bernard'
        self.container.add(self.sb)
        self.sc = StatusUpdate('test', tags=['c', 'f'])
        self.sc.userid = 'cary'
        self.container.add(self.sc)

    def sortAndAssertEqual(self, a, b):
        """Compare lists while ignoring sort"""
        self.assertEqual(sorted(a), sorted(b))

    def test_keys_str(self):
        keys = [x for x in self.container.keys(tags='b')]
        self.sortAndAssertEqual([self.sb.id], keys)

    def test_keys_list(self):
        keys = [x for x in self.container.keys(tags=['b', 'x'])]
        self.sortAndAssertEqual([self.sb.id], keys)

    def test_values(self):
        values = [x for x in self.container.values(tags=['b', 'c'])]
        self.sortAndAssertEqual([self.sb, self.sc], values)

    def test_items(self):
        values = [x[1] for x in self.container.items(tags=['b', 'x'])]
        self.sortAndAssertEqual([self.sb], values)

    def test_user_keys_match(self):
        keys = [x for x in self.container.user_keys(
            ['arnold'],
            tags=['b'])]
        self.sortAndAssertEqual([self.sa.id, self.sb.id], keys)

    def test_user_keys_nomatch(self):
        keys = [x for x in self.container.user_keys(
            ['foo', ],
            tags=['c'])]
        self.sortAndAssertEqual([self.sc.id], keys)

    def test_user_values(self):
        values = [x for x in self.container.user_values(
            ['arnold', ],
            tags=['b'])]
        self.sortAndAssertEqual([self.sa, self.sb], values)

    def test_user_items(self):
        values = [x[1] for x in self.container.user_items(
                  ['cary'],
                  tags=['c'])]
        self.sortAndAssertEqual([self.sc], values)

    def test_keys_nosuchtag(self):
        keys = [x for x in self.container.keys(
            tags=['foo'])]
        self.sortAndAssertEqual([], keys)

    def test_user_keys_nosuchtag(self):
        keys = [x for x in self.container.user_keys(
                ['john', 'mary'],
                tags=['foo', 'bar'])]
        self.sortAndAssertEqual([], keys)
