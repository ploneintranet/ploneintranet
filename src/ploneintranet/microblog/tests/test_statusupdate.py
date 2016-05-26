import unittest2 as unittest
from AccessControl import Unauthorized
from Products.ATContentTypes.content.file import ATFile
from ploneintranet.attachments.attachments import IAttachmentStorage
from zope.component import queryUtility
from zope.interface.verify import verifyClass
from zope.interface import alsoProvides
from zope.interface import implements

from plone.app.testing import login
from plone.app.testing import TEST_USER_ID, setRoles
from plone import api

from ploneintranet.microblog.testing import (
    PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING,
    PLONEINTRANET_MICROBLOG_CONTENTUPDATES_TESTING)

from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.microblog.interfaces import IStatusUpdate
from ploneintranet.microblog.interfaces import IMicroblogContext
from ploneintranet.microblog.statusupdate import StatusUpdate


UUID = dict()


class MockStatusUpdate(StatusUpdate):

    def _context2uuid(self, context):
        if context is None:
            return None
        uuid = repr(context)
        UUID[uuid] = context
        return uuid

    def _uuid2object(self, uuid):
        return UUID[uuid]


class TestStatusUpdateIntegration(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])
        self.container = queryUtility(IMicroblogTool)

    def test_implements(self):
        self.assertTrue(IStatusUpdate.implementedBy(StatusUpdate))
        self.assertTrue(verifyClass(IStatusUpdate, StatusUpdate))

    def test_text(self):
        su = StatusUpdate('foo bar')
        self.assertEqual(su.text, 'foo bar')

    def test_tags(self):
        su = StatusUpdate('bar', tags=['foo', 'fuzzy', 'beer'])
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

    def test_microblog_context_is_not_IMicroblogContext(self):
        mockcontext = object()
        su = StatusUpdate('foo', microblog_context=mockcontext)
        self.assertIsNone(su._microblog_context_uuid)

    def test_microblog_context_uuid(self):
        import Acquisition

        class MockContext(Acquisition.Implicit):
            implements(IMicroblogContext)

        mockcontext = MockContext()
        uuid = repr(mockcontext)
        su = MockStatusUpdate('foo', microblog_context=mockcontext)
        self.assertEqual(uuid, su._microblog_context_uuid)

    def test_microblog_context_acquisition_UUID(self):
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
        su = MockStatusUpdate('foo', microblog_context=wrapped)
        self.assertEqual(uuid, su._microblog_context_uuid)

    def test_microblog_context(self):
        import Acquisition

        class MockContext(Acquisition.Implicit):
            implements(IMicroblogContext)

        mockcontext = MockContext()
        su = MockStatusUpdate('foo', microblog_context=mockcontext)
        self.assertEqual(mockcontext, su.microblog_context)

    def test_microblog_context_acquisition(self):
        import Acquisition
        import ExtensionClass

        class MockContext(Acquisition.Implicit):
            pass

        class MockMicroblogContext(ExtensionClass.Base):
            implements(IMicroblogContext)

        a = MockContext()
        b = MockMicroblogContext()
        wrapped = a.__of__(b)
        su = MockStatusUpdate('foo', microblog_context=wrapped)
        self.assertEqual(b, su.microblog_context)

    def test_microblog_context_UUID_legacy(self):
        class OldStatusUpdate(StatusUpdate):
            def _init_microblog_context(self, *args, **kwargs):
                pass
        su = OldStatusUpdate('foo')
        # old data has new code accessors
        with self.assertRaises(AttributeError):
            su._microblog_context_uuid

    def test_thread_id(self):
        su1 = StatusUpdate('foo bar')
        self.container.add(su1)
        su2 = StatusUpdate('boo baz', thread_id=su1.id)
        self.assertEquals(su2.thread_id, su1.id)

    def test_thread_microblog_context(self):
        self.portal.invokeFactory('Folder', 'f1', title=u"Folder 1")
        f1 = self.portal['f1']
        alsoProvides(f1, IMicroblogContext)
        su1 = StatusUpdate('foo', microblog_context=f1)
        self.container.add(su1)
        su2 = StatusUpdate('foo', thread_id=su1.id)
        self.assertEqual(f1, su2.microblog_context)

    def test_attachments(self):
        su = StatusUpdate('foo bar')
        attachments = IAttachmentStorage(su)

        f = ATFile('data.dat')
        attachments.add(f)
        self.assertEqual([k for k in attachments.keys()], [f.getId()])
        attachments.remove(f.getId())
        self.assertEqual(len(attachments.keys()), 0)

    def test_mentions(self):
        test_user = api.user.create(
            email='test@example.com',
            username='testuser',
            properties={
                'fullname': 'Test User'
            }
        )
        userid = test_user.getId()
        fullname = test_user.getProperty('fullname')
        su = StatusUpdate('foo', mention_ids=[userid])
        self.assertEqual(su.mentions, {userid: fullname})

    def test_action_verb_default(self):
        su = StatusUpdate('foo bar')
        self.assertEqual(su.action_verb, 'posted')

    def test_action_verb_custom(self):
        su = StatusUpdate('foo bar', action_verb='created')
        self.assertEqual(su.action_verb, 'created')


class TestStatusUpdateEdit(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.user_admin = api.user.create(
            email='admin@example.com',
            username='user_admin',  # prevent collision with default admin
            properties={
                'fullname': 'Site Admin'
            }
        )
        api.user.grant_roles(
            user=self.user_admin,
            roles=['Site Administrator', 'Member']
        )
        self.user_steve = api.user.create(
            email='steve@example.com',
            username='user_steve',
            properties={
                'fullname': 'Steve User'
            }
        )
        api.user.grant_roles(
            user=self.user_steve,
            roles=['Member', ]
        )
        self.user_jane = api.user.create(
            email='jane@example.com',
            username='user_jane',
            properties={
                'fullname': 'Jane User'
            }
        )
        api.user.grant_roles(
            user=self.user_jane,
            roles=['Member', ]
        )

    def test_edit_changes_text(self):
        su = StatusUpdate('foo')
        su.edit('bar')
        self.assertEqual(su.text, 'bar')

    def test_original_text_default(self):
        su = StatusUpdate('foo')
        self.assertEqual(su.original_text, None)

    def test_original_text_on_firstedit(self):
        su = StatusUpdate('foo')
        su.edit('bar')
        self.assertEqual(su.original_text, 'foo')

    def test_original_text_remains_secondedit(self):
        su = StatusUpdate('foo')
        su.edit('bar')
        su.edit('shoob')
        self.assertEqual(su.original_text, 'foo')

    def test_edited(self):
        su = StatusUpdate('foo')
        self.assertFalse(su.original_text)
        su.edit('bar')
        self.assertTrue(su.original_text)

    def test_admin_can_edit(self):
        login(self.portal, 'user_steve')
        su = StatusUpdate('foo')
        login(self.portal, 'user_admin')
        su.edit('bar')
        self.assertEqual(su.text, 'bar')

    def test_creator_can_edit(self):
        login(self.portal, 'user_steve')
        su = StatusUpdate('foo')
        su.edit('bar')
        self.assertEqual(su.text, 'bar')

    def test_other_cannot_edit(self):
        login(self.portal, 'user_steve')
        su = StatusUpdate('foo')
        login(self.portal, 'user_jane')
        with self.assertRaises(Unauthorized):
            su.edit('bar')


class TestContentStatusUpdate(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_CONTENTUPDATES_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])
        self.container = queryUtility(IMicroblogTool)

    def test_content_context_mocked(self):
        content = object()
        su = MockStatusUpdate('foo bar', content_context=content)
        self.assertEqual(
            su._content_context_uuid,
            su._context2uuid(content)
        )

    def test_content_context_subscriber(self):
        doc = api.content.create(
            container=self.portal,
            type='Document',
            title='My document',
        )
        # auto-created by event listener
        self.assertEqual(1, len([x for x in self.container.values()]))
        api.content.transition(doc, to_state='published')
        found = [x for x in self.container.values()]
        self.assertEqual(2, len(found))
        su = found[0]
        self.assertEqual(None, su.microblog_context)
        self.assertEqual(doc, su.content_context)

    def test_thread_content_context(self):
        doc = api.content.create(
            container=self.portal,
            type='Document',
            title='My document',
        )
        api.content.transition(doc, to_state='published')
        found = [x for x in self.container.values()]
        su1 = found[0]
        su2 = StatusUpdate('foo', thread_id=su1.id)
        self.assertEqual(None, su2.microblog_context)
        self.assertEqual(doc, su2.content_context)

    def test_content_context_init_sets_microblog_context(self):
        self.portal.invokeFactory('Folder', 'f1', title=u"Folder 1")
        f1 = self.portal['f1']
        alsoProvides(f1, IMicroblogContext)
        doc = api.content.create(
            container=f1,
            type='Document',
            title='My document',
        )
        su1 = StatusUpdate('foo', content_context=doc)
        self.assertEqual(f1, su1.microblog_context)

    def test_content_context_subscriber_sets_microblog_context(self):
        self.portal.invokeFactory('Folder', 'f1', title=u"Folder 1")
        f1 = self.portal['f1']
        alsoProvides(f1, IMicroblogContext)
        doc = api.content.create(
            container=f1,
            type='Document',
            title='My document',
        )
        api.content.transition(doc, to_state='published')
        found = [x for x in self.container.values()]
        su1 = found[0]
        self.assertEqual(f1, su1.microblog_context)

    def test_content_context_subscriber_sets_action_verb_published(self):
        self.portal.invokeFactory('Folder', 'f1', title=u"Folder 1")
        f1 = self.portal['f1']
        alsoProvides(f1, IMicroblogContext)
        doc = api.content.create(
            container=f1,
            type='Document',
            title='My document',
        )
        api.content.transition(doc, to_state='published')
        found = [x for x in self.container.values()]
        su1 = found[0]
        self.assertEqual('published', su1.action_verb)
