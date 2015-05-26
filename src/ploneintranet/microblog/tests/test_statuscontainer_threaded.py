import unittest2 as unittest
from zope.interface import implements

from ploneintranet.microblog.interfaces import IStatusContainer
from ploneintranet.microblog.interfaces import IStatusUpdate
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

    implements(IStatusUpdate)

    def __init__(self, text, userid, creator=None, thread_id=None):
        statusupdate.StatusUpdate.__init__(self, text)
        self.userid = userid
        self.thread_id = thread_id
        if creator:
            self.creator = creator
        else:
            self.creator = userid

    def _init_userid(self):
        pass

    def _init_creator(self):
        pass


class TestStatusContainer_Tags(unittest.TestCase):

    # user/tag accessors

    def test_keys_self(self):
        container = StatusContainer()
        # add normal status update
        status = StatusUpdate('test', 'arnold')
        container.add(status)
        (key, value) = list(container.items())[0]
        self.assertEqual(key, value.id)
        self.assertEqual(status, value)
        keys = [x for x in container.thread_keys(thread_id=status.id)]
        self.assertEqual([status.id], keys)

    def test_keys(self):
        container = StatusContainer()
        # add normal status update
        status = StatusUpdate('test', 'arnold')
        container.add(status)
        (key, value) = list(container.items())[0]
        self.assertEqual(key, value.id)
        self.assertEqual(status, value)
        # add reply to status.id
        sa = StatusUpdate('test reply a', 'arnold', thread_id=status.id)
        container.add(sa)
        sb = StatusUpdate('test reply b', 'bernard', thread_id=status.id)
        container.add(sb)
        sc = StatusUpdate('test reply c', 'cary', thread_id=status.id)
        container.add(sc)
        # get all thread items from parent status.id
        keys = [x for x in container.thread_keys(thread_id=status.id)]
        self.assertEqual([status.id, sa.id, sb.id, sc.id], keys)

    def test_values(self):
        container = StatusContainer()
        # add normal status update
        status = StatusUpdate('test', 'arnold')
        container.add(status)
        (key, value) = list(container.items())[0]
        self.assertEqual(key, value.id)
        self.assertEqual(status, value)
        # add reply to status.id
        sa = StatusUpdate('test reply a', 'arnold', thread_id=status.id)
        container.add(sa)
        sb = StatusUpdate('test reply b', 'bernard', thread_id=status.id)
        container.add(sb)
        sc = StatusUpdate('test reply c', 'cary', thread_id=status.id)
        container.add(sc)
        # get all thread items from parent status.id
        values = [x for x in container.thread_values(thread_id=status.id)]
        self.assertEqual([status, sa, sb, sc], values)

    def test_items(self):
        container = StatusContainer()
        # add normal status update
        status = StatusUpdate('test', 'arnold')
        container.add(status)
        (key, value) = list(container.items())[0]
        self.assertEqual(key, value.id)
        self.assertEqual(status, value)
        # add reply to status.id
        sa = StatusUpdate('test reply a', 'arnold', thread_id=status.id)
        container.add(sa)
        sb = StatusUpdate('test reply b', 'bernard', thread_id=status.id)
        container.add(sb)
        sc = StatusUpdate('test reply c', 'cary', thread_id=status.id)
        container.add(sc)
        # get all thread items from parent status.id
        values = [x[1] for x in container.thread_items(thread_id=status.id)]
        self.assertEqual([status, sa, sb, sc], values)

    def test_get_thread_by_thread_item(self):
        container = StatusContainer()
        # add normal status update
        status = StatusUpdate('test', 'arnold')
        container.add(status)
        (key, value) = list(container.items())[0]
        self.assertEqual(key, value.id)
        self.assertEqual(status, value)
        # add reply to status.id
        sa = StatusUpdate('test reply a', 'arnold', thread_id=status.id)
        container.add(sa)
        sb = StatusUpdate('test reply b', 'bernard', thread_id=status.id)
        container.add(sb)
        sc = StatusUpdate('test reply c', 'cary', thread_id=status.id)
        container.add(sc)
        # get all thread items from thread item sa.id
        si = container.get(sa.id)
        if getattr(si, 'thread_id'):
            values = [x[1] for x in
                      container.thread_items(thread_id=si.thread_id)]
            self.assertEqual([status, sa, sb, sc], values)

    def test_get_nothing_by_none_thread_item(self):
        container = StatusContainer()
        # add normal status update
        status = StatusUpdate('test', 'arnold')
        container.add(status)
        (key, value) = list(container.items())[0]
        self.assertEqual(key, value.id)
        self.assertEqual(status, value)
        # add reply to status.id
        sa = StatusUpdate('test reply a', 'arnold', thread_id=status.id)
        container.add(sa)
        sb = StatusUpdate('test reply b', 'bernard', thread_id=status.id)
        container.add(sb)
        sc = StatusUpdate('test reply c', 'cary', thread_id=status.id)
        container.add(sc)
        # test by giving none
        values = [x[1] for x in container.thread_items(thread_id=None)]
        self.assertEqual([], values)
