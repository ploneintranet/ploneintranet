import unittest2 as unittest
import time

from zope.component import queryUtility
from zope.interface import implements
from AccessControl import Unauthorized

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plonesocial.microblog.testing import\
    PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

from plonesocial.microblog.interfaces import IMicroblogTool
from plonesocial.microblog.interfaces import IStatusUpdate
from plonesocial.microblog import statusupdate


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


class TestPermissions(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.mb_tool = queryUtility(IMicroblogTool)

    def test_add_read_member(self):
        setRoles(self.portal, TEST_USER_ID, ('Member',))
        sa = StatusUpdate('test a', 'arnold')
        container = self.mb_tool
        container.add(sa)
        container.flush_queue()
        values = [x for x in container.values()]
        self.assertEqual([sa], values)
        # dangling queue thread
        time.sleep(.1)

    def test_add_anon(self):
        setRoles(self.portal, TEST_USER_ID, ())
        sa = StatusUpdate('test a', 'arnold')
        container = self.mb_tool
        self.assertRaises(Unauthorized, container.add, sa)

    def test_read_anon(self):
        setRoles(self.portal, TEST_USER_ID, ())
        container = self.mb_tool
        self.assertRaises(Unauthorized, container.values)
        self.assertRaises(Unauthorized, container.items)
        self.assertRaises(Unauthorized, container.keys)
        self.assertRaises(Unauthorized, container.get, 0)
