import time
import unittest2 as unittest
from zope.interface import implements
from zope.interface.verify import verifyClass

from plonesocial.microblog.interfaces import IStatusContainer
from plonesocial.microblog.interfaces import IStatusUpdate
from plonesocial.microblog.statuscontainer import BaseStatusContainer
from plonesocial.microblog import statusupdate


class StatusUpdate(statusupdate.StatusUpdate):
    """Override actual implementation with unittest features"""

    implements(IStatusUpdate)

    def __init__(self, text, userid='dude', creator=None):
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


class TestBaseStatusContainer(unittest.TestCase):

    def test_verify_interface(self):
        self.assertTrue(verifyClass(IStatusContainer, BaseStatusContainer))

    def test_empty(self):
        container = BaseStatusContainer()
        self.assertEqual(0, len(container.items()))

    def test_check_status(self):
        container = BaseStatusContainer()

        class Dummy():
            pass

        su = Dummy()
        self.assertRaises(ValueError, container.add, su)
        self.assertEqual(0, len(container.items()))

    def test_add_items(self):
        container = BaseStatusContainer()
        su = StatusUpdate('test')
        container.add(su)
        self.assertEqual(1, len(container.items()))

    def test_key_corresponds_to_id(self):
        container = BaseStatusContainer()
        su = StatusUpdate('test')
        container.add(su)
        (key, value) = container.items()[0]
        self.assertEqual(key, value.id)
        self.assertEqual(su, value)

    def test_clear_items(self):
        container = BaseStatusContainer()
        su = StatusUpdate('test')
        container.add(su)
        self.assertEqual(1, len(container.items()))
        container.clear()
        self.assertEqual(0, len(container.items()))

    ## primary accessors

    def test_get(self):
        container = BaseStatusContainer()
        su = StatusUpdate('test')
        container.add(su)
        self.assertEqual(su, container.get(su.id))

    def test_items_min_max(self):
        container = BaseStatusContainer()
        sa = StatusUpdate('test a')
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test b')
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test c')
        container.add(sc)
        tc = sc.id

        values = [x[1] for x in container.items(max=ta)]
        self.assertEqual([sa], values)
        values = [x[1] for x in container.items(min=tb)]
        self.assertEqual([sb, sc], values)
        values = [x[1] for x in container.items(min=ta, max=ta)]
        self.assertEqual([sa], values)
        values = [x[1] for x in container.items(min=ta, max=tb)]
        self.assertEqual([sa, sb], values)
        values = [x[1] for x in container.items(min=tc, max=tc)]
        self.assertEqual([sc], values)

    def test_iteritems_min_max(self):
        container = BaseStatusContainer()
        sa = StatusUpdate('test a')
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test b')
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test c')
        container.add(sc)
        tc = sc.id

        values = [x[1] for x in container.iteritems(max=ta)]
        self.assertEqual([sa], values)
        values = [x[1] for x in container.iteritems(min=tb)]
        self.assertEqual([sb, sc], values)
        values = [x[1] for x in container.iteritems(min=ta, max=ta)]
        self.assertEqual([sa], values)
        values = [x[1] for x in container.iteritems(min=ta, max=tb)]
        self.assertEqual([sa, sb], values)
        values = [x[1] for x in container.iteritems(min=tc, max=tc)]
        self.assertEqual([sc], values)

    def test_iterkeys_min_max(self):
        container = BaseStatusContainer()
        sa = StatusUpdate('test a')
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test b')
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test c')
        container.add(sc)
        tc = sc.id

        keys = [x for x in container.iterkeys(max=ta)]
        self.assertEqual([sa.id], keys)
        keys = [x for x in container.iterkeys(min=tb)]
        self.assertEqual([sb.id, sc.id], keys)
        keys = [x for x in container.iterkeys(min=ta, max=ta)]
        self.assertEqual([sa.id], keys)
        keys = [x for x in container.iterkeys(min=ta, max=tb)]
        self.assertEqual([sa.id, sb.id], keys)
        keys = [x for x in container.iterkeys(min=tc, max=tc)]
        self.assertEqual([sc.id], keys)

    def test_itervalues_min_max(self):
        container = BaseStatusContainer()
        sa = StatusUpdate('test a')
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test b')
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test c')
        container.add(sc)
        tc = sc.id

        values = [x for x in container.itervalues(max=ta)]
        self.assertEqual([sa], values)
        values = [x for x in container.itervalues(min=tb)]
        self.assertEqual([sb, sc], values)
        values = [x for x in container.itervalues(min=ta, max=ta)]
        self.assertEqual([sa], values)
        values = [x for x in container.itervalues(min=ta, max=tb)]
        self.assertEqual([sa, sb], values)
        values = [x for x in container.itervalues(min=tc, max=tc)]
        self.assertEqual([sc], values)

    def test_keys_min_max(self):
        container = BaseStatusContainer()
        sa = StatusUpdate('test a')
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test b')
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test c')
        container.add(sc)
        tc = sc.id

        keys = [x for x in container.keys(max=ta)]
        self.assertEqual([sa.id], keys)
        keys = [x for x in container.keys(min=tb)]
        self.assertEqual([sb.id, sc.id], keys)
        keys = [x for x in container.keys(min=ta, max=ta)]
        self.assertEqual([sa.id], keys)
        keys = [x for x in container.keys(min=ta, max=tb)]
        self.assertEqual([sa.id, sb.id], keys)
        keys = [x for x in container.keys(min=tc, max=tc)]
        self.assertEqual([sc.id], keys)

    def test_values_min_max(self):
        container = BaseStatusContainer()
        sa = StatusUpdate('test a')
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test b')
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test c')
        container.add(sc)
        tc = sc.id

        values = [x for x in container.values(max=ta)]
        self.assertEqual([sa], values)
        values = [x for x in container.values(min=tb)]
        self.assertEqual([sb, sc], values)
        values = [x for x in container.values(min=ta, max=ta)]
        self.assertEqual([sa], values)
        values = [x for x in container.values(min=ta, max=tb)]
        self.assertEqual([sa, sb], values)
        values = [x for x in container.values(min=tc, max=tc)]
        self.assertEqual([sc], values)
