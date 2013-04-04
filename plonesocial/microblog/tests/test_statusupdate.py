import unittest2 as unittest
from zope.interface.verify import verifyClass

#from zope.component import createObject
#from Acquisition import aq_base, aq_parent
#from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_ID, setRoles

from plonesocial.microblog.testing import\
    PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

from plonesocial.microblog.interfaces import IStatusUpdate
import plonesocial.microblog.statusupdate


class StatusUpdate(plonesocial.microblog.statusupdate.StatusUpdate):

    def _context2uuid(self, context):
        return repr(context)


class TestStatusUpdate(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_implements(self):
        self.assertTrue(IStatusUpdate.implementedBy(StatusUpdate))
        self.assertTrue(verifyClass(IStatusUpdate, StatusUpdate))

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

    def test_context_UUID(self):
        mockcontext = object()
        uuid = repr(mockcontext)
        sa = StatusUpdate('foo', context=mockcontext)
        self.assertEquals(uuid, sa.context_uuid)

    def test_context_UUID_legacy(self):
        class OldStatusUpdate(StatusUpdate):
            def _init_context(self, context):
                pass
        sa = OldStatusUpdate('foo')
        # old data has new code accessors
        self.assertEquals(None, sa.context_uuid)
