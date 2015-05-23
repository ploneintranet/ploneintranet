import time
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


class TestStatusContainer_User(unittest.TestCase):

    # user accessors

    def test_user_items_all(self):
        container = StatusContainer()
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        sb = StatusUpdate('test b', 'bernard')
        container.add(sb)
        sc = StatusUpdate('test c', 'cary')
        container.add(sc)
        values = [x[1] for x in
                  container.user_items(['arnold', 'bernard', 'cary'])]
        self.assertEqual([sc, sb, sa], values)

    def test_user_items_limit(self):
        container = StatusContainer()
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        sb = StatusUpdate('test b', 'bernard')
        container.add(sb)
        sc = StatusUpdate('test c', 'cary')
        container.add(sc)
        values = [x[1] for x in
                  container.user_items(['arnold', 'bernard', 'cary'],
                                       limit=2)]
        self.assertEqual([sc, sb], values)

    def test_user_items_some(self):
        container = StatusContainer()
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        sb = StatusUpdate('test b', 'bernard')
        container.add(sb)
        sc = StatusUpdate('test c', 'cary')
        container.add(sc)
        values = [x[1] for x in
                  container.user_items(['arnold', 'bernard'])]
        self.assertEqual([sb, sa], values)

    def test_user_items_one(self):
        container = StatusContainer()
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        sb = StatusUpdate('test b', 'bernard')
        container.add(sb)
        sc = StatusUpdate('test c', 'cary')
        container.add(sc)
        values = [x[1] for x in
                  container.user_items(['bernard'])]
        self.assertEqual([sb], values)

    def test_user_items_none(self):
        container = StatusContainer()
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        sb = StatusUpdate('test b', 'bernard')
        container.add(sb)
        sc = StatusUpdate('test c', 'cary')
        container.add(sc)
        values = [x for x in
                  container.user_items(['zacharias'])]
        self.assertEqual([], values)

    def test_user_items_min_max_all(self):
        container = StatusContainer()
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test b', 'bernard')
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test c', 'cary')
        container.add(sc)
        tc = sc.id

        users = ['arnold', 'bernard', 'cary']

        values = [x[1] for x in container.user_items(users, max=ta)]
        self.assertEqual([sa], values)
        values = [x[1] for x in container.user_items(users, min=tb)]
        self.assertEqual([sc, sb], values)
        values = [x[1] for x in container.user_items(users, min=ta, max=ta)]
        self.assertEqual([sa], values)
        values = [x[1] for x in container.user_items(users, min=ta, max=tb)]
        self.assertEqual([sb, sa], values)
        values = [x[1] for x in container.user_items(users, min=tc, max=tc)]
        self.assertEqual([sc], values)

    def test_user_items_min_max_some(self):
        container = StatusContainer()
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test b', 'bernard')
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test c', 'cary')
        container.add(sc)
        tc = sc.id

        users = ['bernard', 'cary', 'zacharias']  # excludes sa

        values = [x[1] for x in container.user_items(users, max=ta)]
        self.assertEqual([], values)
        values = [x[1] for x in container.user_items(users, min=tb)]
        self.assertEqual([sc, sb], values)
        values = [x[1] for x in container.user_items(users, min=ta, max=ta)]
        self.assertEqual([], values)
        values = [x[1] for x in container.user_items(users, min=ta, max=tb)]
        self.assertEqual([sb], values)
        values = [x[1] for x in container.user_items(users, min=tc, max=tc)]
        self.assertEqual([sc], values)

    def test_user_keys_min_max_some(self):
        container = StatusContainer()
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test b', 'bernard')
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test c', 'cary')
        container.add(sc)
        tc = sc.id

        users = ['bernard', 'cary', 'zacharias']  # excludes sa

        values = [x for x in container.user_keys(users, max=ta)]
        self.assertEqual([], values)
        values = [x for x in container.user_keys(users, min=tb)]
        self.assertEqual([sc.id, sb.id], values)
        values = [x for x in container.user_keys(users, min=ta, max=ta)]
        self.assertEqual([], values)
        values = [x for x in container.user_keys(users, min=ta, max=tb)]
        self.assertEqual([sb.id], values)
        values = [x for x in container.user_keys(users, min=tc, max=tc)]
        self.assertEqual([sc.id], values)

    def test_user_values_min_max_some(self):
        container = StatusContainer()
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test b', 'bernard')
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test c', 'cary')
        container.add(sc)
        tc = sc.id

        users = ['bernard', 'cary', 'zacharias']  # excludes sa

        values = [x for x in container.user_values(users, max=ta)]
        self.assertEqual([], values)
        values = [x for x in container.user_values(users, min=tb)]
        self.assertEqual([sc, sb], values)
        values = [x for x in container.user_values(users, min=ta, max=ta)]
        self.assertEqual([], values)
        values = [x for x in container.user_values(users, min=ta, max=tb)]
        self.assertEqual([sb], values)
        values = [x for x in container.user_values(users, min=tc, max=tc)]
        self.assertEqual([sc], values)

    def test_user_keys_generator(self):
        container = StatusContainer()
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test b', 'bernard')
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test c', 'cary')
        container.add(sc)

        users = (x for x in
                 ['bernard', 'cary', 'zacharias'])

        values = [x for x in container.user_values(users, min=ta, max=tb)]
        self.assertEqual([sb], values)

    def test_user_keys_generator_empty(self):
        container = StatusContainer()
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test b', 'bernard')
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test c', 'cary')
        container.add(sc)

        users = (x for x in [])

        values = [x for x in container.user_values(users, min=ta, max=tb)]
        self.assertEqual([], values)

    def test_user_keys_string(self):
        container = StatusContainer()
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test b', 'bernard')
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test c', 'cary')
        container.add(sc)

        users = 'bernard'
        values = [x for x in container.user_values(users, min=ta, max=tb)]
        self.assertEqual([sb], values)

        users = 'zacharias'
        values = [x for x in container.user_values(users, min=ta, max=tb)]
        self.assertEqual([], values)

    def test_user_keys_None(self):
        container = StatusContainer()
        sa = StatusUpdate('test a', 'arnold')
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test b', 'bernard')
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test c', 'cary')
        container.add(sc)

        users = None
        values = [x for x in container.user_values(users, min=ta, max=tb)]
        self.assertEqual([], values)
