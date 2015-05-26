import time
from plone import api
import unittest2 as unittest
from zope.interface import implements
from ploneintranet.microblog.testing import \
    PLONEINTRANET_MICROBLOG_PORTAL_SUBSCRIBER_INTEGRATION_TESTING

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

    def __init__(self, text, userid, creator=None, mention_ids=None):
        statusupdate.StatusUpdate.__init__(self, text, mention_ids=mention_ids)
        self.userid = userid
        if creator:
            self.creator = creator
        else:
            self.creator = userid

    def _init_userid(self):
        pass

    def _init_creator(self):
        pass


class TestStatusContainer_Mentions(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_PORTAL_SUBSCRIBER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.user_a = api.user.create(
            email='a@example.com',
            username='arnold',
            properties={
                'fullname': 'Arnold A'
            }
        )
        self.user_b = api.user.create(
            email='b@example.com',
            username='bernard',
            properties={
                'fullname': 'Bernard B'
            }
        )
        self.user_c = api.user.create(
            email='c@example.com',
            username='cary',
            properties={
                'fullname': 'Cary C'
            }
        )

    def test_mention_items_all(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['bernard'])
        container.add(sa)
        sb = StatusUpdate('test @arnold', 'bernard',
                          mention_ids=['arnold', 'cary'])
        container.add(sb)
        sc = StatusUpdate('test @arnold @bernard', 'cary',
                          mention_ids=['arnold', 'bernard'])
        container.add(sc)
        values = [x[1] for x in
                  container.mention_items(['arnold', 'bernard'])]
        self.assertIn(sa, values)
        self.assertIn(sb, values)
        self.assertIn(sc, values)

    def test_mention_items_limit(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['bernard'])
        container.add(sa)
        sb = StatusUpdate('test @arnold', 'bernard',
                          mention_ids=['arnold', 'cary'])
        container.add(sb)
        sc = StatusUpdate('test @arnold @bernard', 'cary',
                          mention_ids=['arnold', 'bernard'])
        container.add(sc)
        values = [x[1] for x in
                  container.mention_items(['arnold', 'bernard', 'cary'],
                                          limit=2)]
        self.assertEqual(len(values), 2)

    def test_mention_items_some(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['bernard'])
        container.add(sa)
        sb = StatusUpdate('test @arnold', 'bernard', mention_ids=['cary'])
        container.add(sb)
        sc = StatusUpdate('test @arnold @bernard', 'cary',
                          mention_ids=['arnold', 'bernard'])
        container.add(sc)
        values = [x[1] for x in
                  container.mention_items(['arnold', 'cary'])]
        self.assertNotIn(sa, values)
        self.assertIn(sb, values)
        self.assertIn(sc, values)

    def test_mention_items_one(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['bernard'])
        container.add(sa)
        sb = StatusUpdate('test @arnold', 'bernard', mention_ids=['cary'])
        container.add(sb)
        sc = StatusUpdate('test @arnold @bernard', 'cary',
                          mention_ids=['arnold', 'bernard'])
        container.add(sc)
        values = [x[1] for x in
                  container.mention_items(['cary'])]
        self.assertEqual([sb], values)

    def test_mention_items_none(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['bernard'])
        container.add(sa)
        sb = StatusUpdate('test @arnold', 'bernard', mention_ids=['arnold'])
        container.add(sb)
        sc = StatusUpdate('test @arnold @bernard', 'cary',
                          mention_ids=['arnold', 'bernard'])
        container.add(sc)
        values = [x for x in
                  container.mention_items(['cary'])]
        self.assertEqual([], values)

    def test_mention_items_min_max_all(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['bernard'])
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test @arnold', 'bernard', mention_ids=['cary'])
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test @arnold @bernard', 'cary',
                          mention_ids=['arnold', 'bernard'])
        container.add(sc)
        tc = sc.id

        mentions = ['arnold', 'bernard', 'cary']

        values = [x[1] for x in container.mention_items(mentions, max=ta)]
        self.assertEqual([sa], values)
        values = [x[1] for x in container.mention_items(mentions, min=tb)]
        self.assertEqual([sc, sb], values)
        values = [x[1] for x in container.mention_items(mentions,
                                                        min=ta, max=ta)]
        self.assertEqual([sa], values)
        values = [x[1] for x in container.mention_items(mentions,
                                                        min=ta, max=tb)]
        self.assertEqual([sb, sa], values)
        values = [x[1] for x in container.mention_items(mentions,
                                                        min=tc, max=tc)]
        self.assertEqual([sc], values)

    def test_mention_items_min_max_some(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['cary'])
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test @arnold', 'bernard', mention_ids=['arnold'])
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test @arnold @bernard', 'cary',
                          mention_ids=['arnold', 'bernard'])
        container.add(sc)
        tc = sc.id

        mentions = ['arnold', 'bernard', 'denis']  # excludes sa

        values = [x[1] for x in container.mention_items(mentions, max=ta)]
        self.assertEqual([], values)
        values = [x[1] for x in container.mention_items(mentions, min=tb)]
        self.assertEqual([sc, sb], values)
        values = [x[1] for x in container.mention_items(mentions,
                                                        min=ta, max=ta)]
        self.assertEqual([], values)
        values = [x[1] for x in container.mention_items(mentions,
                                                        min=ta, max=tb)]
        self.assertEqual([sb], values)
        values = [x[1] for x in container.mention_items(mentions,
                                                        min=tc, max=tc)]
        self.assertEqual([sc], values)

    def test_mention_keys_min_max_some(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['cary'])
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test @arnold', 'bernard', mention_ids=['arnold'])
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test @arnold @bernard', 'cary',
                          mention_ids=['arnold', 'bernard'])
        container.add(sc)
        tc = sc.id

        mentions = ['arnold', 'bernard', 'denis']  # excludes sa

        values = [x for x in container.mention_keys(mentions, max=ta)]
        self.assertEqual([], values)
        values = [x for x in container.mention_keys(mentions, min=tb)]
        self.assertEqual([sc.id, sb.id], values)
        values = [x for x in container.mention_keys(mentions, min=ta, max=ta)]
        self.assertEqual([], values)
        values = [x for x in container.mention_keys(mentions, min=ta, max=tb)]
        self.assertEqual([sb.id], values)
        values = [x for x in container.mention_keys(mentions, min=tc, max=tc)]
        self.assertEqual([sc.id], values)

    def test_mention_values_min_max_some(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['cary'])
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test @arnold', 'bernard', mention_ids=['arnold'])
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test @arnold @bernard', 'cary',
                          mention_ids=['arnold', 'bernard'])
        container.add(sc)
        tc = sc.id

        mentions = ['arnold', 'bernard', 'denis']  # excludes sa

        values = [x for x in container.mention_values(mentions, max=ta)]
        self.assertEqual([], values)
        values = [x for x in container.mention_values(mentions, min=tb)]
        self.assertEqual([sc, sb], values)
        values = [x for x in container.mention_values(mentions,
                                                      min=ta, max=ta)]
        self.assertEqual([], values)
        values = [x for x in container.mention_values(mentions,
                                                      min=ta, max=tb)]
        self.assertEqual([sb], values)
        values = [x for x in container.mention_values(mentions,
                                                      min=tc, max=tc)]
        self.assertEqual([sc], values)

    def test_mention_keys_generator_empty(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['cary'])
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test @arnold', 'bernard', mention_ids=['arnold'])
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test @arnold @bernard', 'cary',
                          mention_ids=['arnold', 'bernard'])
        container.add(sc)
        # tc = sc.id

        mentions = (x for x in [])

        values = [x for x in container.mention_values(mentions,
                                                      min=ta, max=tb)]
        self.assertEqual([], values)

    def test_mention_keys_string(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['bernard'])
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test @arnold', 'bernard', mention_ids=['cary'])
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test @arnold @bernard', 'cary',
                          mention_ids=['arnold', 'bernard'])
        container.add(sc)
        # tc = sc.id

        mentions = 'cary'
        values = [x for x in container.mention_values(mentions,
                                                      min=ta, max=tb)]
        self.assertEqual([sb], values)

        mentions = 'zacharias'
        values = [x for x in container.mention_values(mentions,
                                                      min=ta, max=tb)]
        self.assertEqual([], values)

    def test_mention_keys_None(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['cary'])
        container.add(sa)
        ta = sa.id  # reset by container

        time.sleep(0.1)
        sb = StatusUpdate('test @arnold', 'bernard', mention_ids=['arnold'])
        container.add(sb)
        tb = sb.id

        time.sleep(0.1)
        sc = StatusUpdate('test @arnold @bernard', 'cary',
                          mention_ids=['arnold', 'bernard'])
        container.add(sc)
        # tc = sc.id

        mentions = None
        values = [x for x in container.mention_values(mentions,
                                                      min=ta, max=tb)]
        self.assertEqual([], values)
