import time
import Queue
import unittest2 as unittest
from zope.interface import implements

from plonesocial.microblog.interfaces import IStatusContainer
from plonesocial.microblog.interfaces import IStatusUpdate
from plonesocial.microblog import statuscontainer
from plonesocial.microblog import statusupdate

from plonesocial.microblog.statuscontainer import STATUSQUEUE
import plonesocial.microblog.statuscontainer
plonesocial.microblog.statuscontainer.MAX_QUEUE_AGE = 50


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


class StatusContainer(statuscontainer.StatusContainer):
    """Override implementation for unittest isolation"""

    implements(IStatusContainer)

    def __init__(self, context=None):
        """A contextless statuscontainer for fast unittesting"""
        statuscontainer.StatusContainer.__init__(self, context)

    def _notify(self, status):
        """This was the only actual context dependency."""
        pass


class TestStatusContainer_Queue(unittest.TestCase):

    def setUp(self):
        # needed for thread teardown
        self.container = StatusContainer()
        # make sure also first item will be queued
        self.container._mtime = int(time.time() * 1000)

    def tearDown(self):
        # stop the thread timer
        try:
            self.container._v_timer.cancel()
            time.sleep(1)  # allow for thread cleanup
        except AttributeError:
            pass

        # we have an in-memory queue, purge it
        while True:
            try:
                STATUSQUEUE.get(block=False)
            except Queue.Empty:
                break

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
        time.sleep(1)  # second resolution only on timer
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
        self.assertEqual([sa, sb], values)  # added by autoflush
