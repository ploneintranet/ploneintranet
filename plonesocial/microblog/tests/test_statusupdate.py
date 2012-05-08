import unittest2 as unittest

#from zope.component import createObject
#from Acquisition import aq_base, aq_parent
#from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_ID, setRoles

from plonesocial.microblog.testing import\
    PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

from plonesocial.microblog.statusupdate import StatusUpdate


class TestStatusUpdate(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_text(self):
        s = StatusUpdate('foo bar')
        self.assertEquals(s.text, 'foo bar')

    def test_tags(self):
        s = StatusUpdate('#foo bar #fuzzy #beer')
        tags = list(s.tags)
        tags.sort()
        self.assertEquals(tags, ['#beer', '#foo', '#fuzzy'])

    def no_test_userid(self):
        """Doesn't work in test context"""
        s = StatusUpdate('foo bar')
        self.assertEquals(s.id, TEST_USER_ID)

    def test_creator(self):
        s = StatusUpdate('foo bar')
        self.assertEquals(s.creator, 'test-user')
