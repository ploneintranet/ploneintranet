import unittest2 as unittest
from zope.interface import implements

from plonesocial.microblog.interfaces import IStatusContainer
from plonesocial.microblog.interfaces import IStatusUpdate
from plonesocial.microblog import statuscontainer
from plonesocial.microblog import statusupdate


class StatusContainer(statuscontainer.BaseStatusContainer):
    """Override actual implementation with unittest features"""

    implements(IStatusContainer)

    def _check_permission(self, perm="read"):
        pass


class StatusUpdate(statusupdate.StatusUpdate):
    """Override actual implementation with unittest features"""

    implements(IStatusUpdate)

    def __init__(self, text, userid, creator=None):
        statusupdate.StatusUpdate.__init__(self, text)
        self.userid = userid
        if creator:
            self.creator = creator
        else:
            self.creator = userid

    def _init_userid(self):
        pass

    def _init_creator(self):
        pass


class TestStatusContainer_Tags(unittest.TestCase):

    ## user/tag accessors

    def test_keys(self):
        container = StatusContainer()
        sa = StatusUpdate('test #a', 'arnold')
        container.add(sa)
        sb = StatusUpdate('test #b', 'bernard')
        container.add(sb)
        sc = StatusUpdate('test #c', 'cary')
        container.add(sc)
        keys = [x for x in container.keys(tag='b')]
        self.assertEqual([sb.id], keys)

    def test_values(self):
        container = StatusContainer()
        sa = StatusUpdate('test #a', 'arnold')
        container.add(sa)
        sb = StatusUpdate('test #b', 'bernard')
        container.add(sb)
        sc = StatusUpdate('test #c', 'cary')
        container.add(sc)
        values = [x for x in container.values(tag='b')]
        self.assertEqual([sb], values)

    def test_items(self):
        container = StatusContainer()
        sa = StatusUpdate('test #a', 'arnold')
        container.add(sa)
        sb = StatusUpdate('test #b', 'bernard')
        container.add(sb)
        sc = StatusUpdate('test #b #c', 'cary')
        container.add(sc)
        values = [x[1] for x in container.items(tag='b')]
        self.assertEqual([sc, sb], values)

    def test_user_keys_match(self):
        container = StatusContainer()
        sa = StatusUpdate('test #a', 'arnold')
        container.add(sa)
        sb = StatusUpdate('test #b', 'bernard')
        container.add(sb)
        sc = StatusUpdate('test #c', 'cary')
        container.add(sc)
        keys = [x for x in container.user_keys(['arnold', 'bernard', 'cary'],
                                               tag='b')]
        self.assertEqual([sb.id], keys)

    def test_user_keys_nomatch(self):
        container = StatusContainer()
        sa = StatusUpdate('test #a', 'arnold')
        container.add(sa)
        sb = StatusUpdate('test #b', 'bernard')
        container.add(sb)
        sc = StatusUpdate('test #c', 'cary')
        container.add(sc)
        keys = [x for x in container.user_keys(['arnold', 'bernard'],
                                               tag='c')]
        self.assertEqual([], keys)

    def test_user_values(self):
        container = StatusContainer()
        sa = StatusUpdate('test #a', 'arnold')
        container.add(sa)
        sb = StatusUpdate('test #b', 'bernard')
        container.add(sb)
        sc = StatusUpdate('test #c', 'cary')
        container.add(sc)
        values = [x for x in
                  container.user_values(['arnold', 'bernard', 'cary'],
                                        tag='b')]
        self.assertEqual([sb], values)

    def test_user_items(self):
        container = StatusContainer()
        sa = StatusUpdate('test #a', 'arnold')
        container.add(sa)
        sb = StatusUpdate('test #b', 'bernard')
        container.add(sb)
        sc = StatusUpdate('test #c', 'cary')
        container.add(sc)
        values = [x[1] for x in
                  container.user_items(['arnold', 'bernard', 'cary'],
                                       tag='b')]
        self.assertEqual([sb], values)

    def test_keys_nosuchtag(self):
        container = StatusContainer()
        sa = StatusUpdate('test #a', 'arnold')
        container.add(sa)
        sb = StatusUpdate('test #b', 'bernard')
        container.add(sb)
        sc = StatusUpdate('test #c', 'cary')
        container.add(sc)
        keys = [x for x in container.keys(tag='foo')]
        self.assertEqual([], keys)

    def test_user_keys_nosuchtag(self):
        container = StatusContainer()
        sa = StatusUpdate('test #a', 'arnold')
        container.add(sa)
        sb = StatusUpdate('test #b', 'bernard')
        container.add(sb)
        sc = StatusUpdate('test #c', 'cary')
        container.add(sc)
        keys = [x for x in container.user_keys(['arnold', 'bernard', 'cary'],
                                               tag='foobar')]
        self.assertEqual([], keys)
