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
        self.sa = StatusUpdate('test', tags=['a'])
        self.sa.userid = 'arnold'
        self.container.add(self.sa)
        self.sb = StatusUpdate('test', tags=['b'])
        self.sb.userid = 'bernard'
        self.container.add(self.sb)
        self.sc = StatusUpdate('test', tags=['c'])
        self.sc.userid = 'cary'
        self.container.add(self.sc)

    def test_keys(self):
        keys = [x for x in self.container.keys(tag='b')]
        self.assertEqual([self.sb.id], keys)

    def test_values(self):
        values = [x for x in self.container.values(tag='b')]
        self.assertEqual([self.sb], values)

    def test_items(self):
        values = [x[1] for x in self.container.items(tag='b')]
        self.assertEqual([self.sb], values)

    def test_user_keys_match(self):
        keys = [x for x in self.container.user_keys(
            ['arnold', 'bernard', 'cary'],
            tag='b')]
        self.assertEqual([self.sb.id], keys)

    def test_user_keys_nomatch(self):
        keys = [x for x in self.container.user_keys(
            ['arnold', 'bernard'],
            tag='c')]
        self.assertEqual([], keys)

    def test_user_values(self):
        values = [x for x in self.container.user_values(
            ['arnold', 'bernard', 'cary'],
            tag='b')]
        self.assertEqual([self.sb], values)

    def test_user_items(self):
        values = [x[1] for x in self.container.user_items(
                  ['arnold', 'bernard', 'cary'],
                  tag='b')]
        self.assertEqual([self.sb], values)

    def test_keys_nosuchtag(self):
        keys = [x for x in self.container.keys(tag='foo')]
        self.assertEqual([], keys)

    def test_user_keys_nosuchtag(self):
        keys = [x for x in self.container.user_keys(
                ['arnold', 'bernard', 'cary'],
                tag='foobar')]
        self.assertEqual([], keys)
