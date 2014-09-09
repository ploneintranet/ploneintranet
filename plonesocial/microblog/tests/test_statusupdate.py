import unittest2 as unittest
from zope.interface.verify import verifyClass
from zope.interface import implements

from plone.app.testing import TEST_USER_ID, setRoles

from plonesocial.microblog.testing import\
    PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

from plonesocial.microblog.interfaces import IStatusUpdate
from plonesocial.microblog.interfaces import IMicroblogContext
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
        self.assertEqual(su.text, 'foo bar')

    def test_tags(self):
        su = StatusUpdate('#foo bar #fuzzy #beer')
        tags = list(su.tags)
        tags.sort()
        self.assertEqual(tags, ['beer', 'foo', 'fuzzy'])

    def no_test_userid(self):
        """Doesn't work in test context"""
        su = StatusUpdate('foo bar')
        self.assertEqual(su.id, TEST_USER_ID)

    def test_creator(self):
        su = StatusUpdate('foo bar')
        self.assertEqual(su.creator, 'test-user')

    def test_tag_comma(self):
        sa = StatusUpdate('test #foo,')
        self.assertEqual(sa.tags, ['foo'])

    def test_tag_interpunction(self):
        sa = StatusUpdate('test #foo,:.;!$')
        self.assertEqual(sa.tags, ['foo'])

    def test_context_is_not_IMicroblogContext(self):
        mockcontext = object()
        sa = StatusUpdate('foo', context=mockcontext)
        self.assertIsNone(sa.context_uuid)

    def test_context_UUID(self):
        import Acquisition

        class MockContext(Acquisition.Implicit):
            implements(IMicroblogContext)

        mockcontext = MockContext()
        uuid = repr(mockcontext)
        sa = StatusUpdate('foo', context=mockcontext)
        self.assertEqual(uuid, sa.context_uuid)

    def test_context_acquisition_UUID(self):
        import Acquisition
        import ExtensionClass

        class MockContext(Acquisition.Implicit):
            pass

        class MockMicroblogContext(ExtensionClass.Base):
            implements(IMicroblogContext)

        a = MockContext()
        b = MockMicroblogContext()
        wrapped = a.__of__(b)
        uuid = repr(b)
        sa = StatusUpdate('foo', context=wrapped)
        self.assertEqual(uuid, sa.context_uuid)

    def test_context_UUID_legacy(self):
        class OldStatusUpdate(StatusUpdate):
            def _init_context(self, context):
                pass
        sa = OldStatusUpdate('foo')
        # old data has new code accessors
        self.assertIsNone(sa.context_uuid)

    def test_context_object_microblog(self):
        import ExtensionClass

        class MockMicroblogContext(ExtensionClass.Base):
            implements(IMicroblogContext)

        sa = StatusUpdate('foo', context=MockMicroblogContext())
        self.assertEqual(sa, sa.getObject())

    def test_context_object_object(self):
        import Acquisition
        import ExtensionClass

        class MockContext(Acquisition.Implicit):
            pass

        class MockMicroblogContext(ExtensionClass.Base):
            implements(IMicroblogContext)

        a = MockContext()
        b = MockMicroblogContext()
        wrapped = a.__of__(b)
        sa = StatusUpdate('foo', context=wrapped)
        self.assertEquals(a, sa.getObject())

    def test_thread_id(self):
        su = StatusUpdate('foo bar', thread_id='jawel')
        self.assertEquals(su.thread_id, 'jawel')
