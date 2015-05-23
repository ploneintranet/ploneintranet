import time
import unittest2 as unittest
from zope.interface import implements
from zope.interface.verify import verifyClass

from ploneintranet.microblog.interfaces import IStatusContainer
from ploneintranet.microblog.interfaces import IStatusUpdate
from ploneintranet.microblog import statuscontainer
from ploneintranet.microblog import statusupdate

from ploneintranet.microblog.statuscontainer import STATUSQUEUE
import ploneintranet.microblog.statuscontainer
from ploneintranet.microblog.testing import tearDownContainer


class StatusContainer(statuscontainer.QueuedStatusContainer):
    """Override actual implementation with unittest features"""

    implements(IStatusContainer)

    def _check_add_permission(self, statusupdate):
        pass

    def _blacklist_microblogcontext_uuids(self):
        return []


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


class TestQueueStatusContainer(unittest.TestCase):

    def setUp(self):
        # needed for thread teardown
        self.container = StatusContainer()
        # make sure also first item will be queued
        self.container._mtime = int(time.time() * 1000)
        ploneintranet.microblog.statuscontainer.MAX_QUEUE_AGE = 50

    def tearDown(self):
        tearDownContainer(self.container)
        ploneintranet.microblog.statuscontainer.MAX_QUEUE_AGE = 1000

    def test_verify_interface(self):
        self.assertTrue(verifyClass(IStatusContainer, StatusContainer))

    def test_add_queued(self):
        """Test the queueing"""
        container = self.container
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        values = [x for x in container.values()]
        # stuff is in queue, not stored
        self.assertEqual([], values)
        self.assertFalse(STATUSQUEUE.empty())

    def test_add_scheduled(self):
        """Test the thread scheduler"""
        container = self.container
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        values = [x for x in container.values()]
        # stuff is in queue, not stored
        self.assertEqual([], values)
        time.sleep(2)  # second resolution only on timer
        values = [x for x in container.values()]
        self.assertEqual([sa], values)

    def test_add_scheduled_disabled(self):
        """Test disabling of thread scheduler"""
        container = self.container
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)

        # same test as above, but cancel scheduler
        self.container._v_timer.cancel()

        values = [x for x in container.values()]
        # stuff is in queue, not stored
        self.assertEqual([], values)
        time.sleep(1)  # second resolution only on timer
        values = [x for x in container.values()]
        self.assertEqual([], values)

    def test_add_multi(self):
        container = self.container
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        self.container._v_timer.cancel()  # cancel scheduler
        sb = StatusUpdate('test b', 'bernard')
        # more than autoflush, less than scheduled flush
        time.sleep(.2)
        container.add(sb)
        values = [x for x in container.values()]
        self.assertEqual([sb, sa], values)  # added by autoflush
