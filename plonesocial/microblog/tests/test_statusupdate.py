import unittest2 as unittest

#from zope.component import createObject
#from Acquisition import aq_base, aq_parent
#from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_ID, setRoles

from plonesocial.microblog.testing import\
    PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

from plonesocial.microblog.interfaces import IStatusUpdate
from plonesocial.microblog.statusupdate import StatusUpdate


class TestStatusUpdate(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_implements(self):
        self.assertTrue(IStatusUpdate.implementedBy(StatusUpdate))

    def test_text(self):
        su = StatusUpdate('foo bar')
        self.assertEquals(su.text, 'foo bar')

    def test_tags(self):
        su = StatusUpdate('#foo bar #fuzzy #beer')
        tags = list(su.tags)
        tags.sort()
        self.assertEquals(tags, ['beer', 'foo', 'fuzzy'])

    def no_test_userid(self):
        """Doesn't work in test context"""
        su = StatusUpdate('foo bar')
        self.assertEquals(su.id, TEST_USER_ID)

    def test_creator(self):
        su = StatusUpdate('foo bar')
        self.assertEquals(su.creator, 'test-user')

    def test_tag_comma(self):
        sa = StatusUpdate('test #foo,')
        self.assertEquals(sa.tags, ['foo'])

    def test_tag_interpunction(self):
        sa = StatusUpdate('test #foo,:.;!$')
        self.assertEquals(sa.tags, ['foo'])
