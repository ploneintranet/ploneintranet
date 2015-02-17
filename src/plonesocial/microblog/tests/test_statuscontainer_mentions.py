from plone import api
import unittest2 as unittest
from zope.interface import implements
from plonesocial.microblog.testing import \
    PLONESOCIAL_MICROBLOG_PORTAL_SUBSCRIBER_INTEGRATION_TESTING

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

    layer = PLONESOCIAL_MICROBLOG_PORTAL_SUBSCRIBER_INTEGRATION_TESTING

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

    def test_keys(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['bernard'])
        container.add(sa)
        sb = StatusUpdate('test @arnold', 'bernard', mention_ids=['arnold'])
        container.add(sb)
        sc = StatusUpdate('test @arnold @bernard', 'cary', mention_ids=['arnold', 'bernard'])
        container.add(sc)
        keys = [x for x in container.keys(mention='bernard')]
        self.assertIn(sa.id, keys)
        self.assertIn(sc.id, keys)

    def test_values(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['bernard'])
        container.add(sa)
        sb = StatusUpdate('test @arnold', 'bernard', mention_ids=['arnold'])
        container.add(sb)
        sc = StatusUpdate('test @arnold @bernard', 'cary', mention_ids=['arnold', 'bernard'])
        container.add(sc)
        values = [x for x in container.values(mention='bernard')]
        self.assertIn(sa, values)
        self.assertIn(sc, values)

    def test_items(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['bernard'])
        container.add(sa)
        sb = StatusUpdate('test @arnold', 'bernard', mention_ids=['arnold'])
        container.add(sb)
        sc = StatusUpdate('test @arnold @bernard', 'cary', mention_ids=['arnold', 'bernard'])
        container.add(sc)
        values = [x[1] for x in container.items(mention='bernard')]
        self.assertIn(sa, values)
        self.assertIn(sc, values)

    def test_keys_nosuchmention(self):
        container = StatusContainer()
        sa = StatusUpdate('test @bernard', 'arnold', mention_ids=['bernard'])
        container.add(sa)
        sb = StatusUpdate('test @arnold', 'bernard', mention_ids=['arnold'])
        container.add(sb)
        sc = StatusUpdate('test @arnold @bernard', 'cary', mention_ids=['arnold', 'bernard'])
        container.add(sc)
        keys = [x for x in container.keys(mention='cary')]
        self.assertEqual([], keys)
