from AccessControl import Unauthorized
import Acquisition
from plone import api
import unittest2 as unittest
from plone.app.testing import login, logout
from zope.interface import implements
from ploneintranet.microblog.testing import \
    PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

from ploneintranet.microblog.interfaces import IMicroblogContext
from ploneintranet.microblog.interfaces import IStatusContainer
from ploneintranet.microblog import statuscontainer
from ploneintranet.microblog.statusupdate import StatusUpdate


class StatusContainer(statuscontainer.BaseStatusContainer):

    """Override actual implementation with unittest features"""

    implements(IStatusContainer)

    def _check_add_permission(self, status):
        return

    def _blacklist_microblogcontext_uuids(self):
        return []


class UUIDStatusContainer(StatusContainer):

    def _check_delete_permission(self, status):
        return

    def _context2uuid(self, context):
        if context:
            return repr(context)


class UUIDStatusUpdate(StatusUpdate):

    def _context2uuid(self, context):
        if context:
            return repr(context)


class ContextlessStatusUpdate(StatusUpdate):

    def _init_microblog_context(self, *args):
        self._microblog_context_uuid = None

    def _init_content_context(self, *args):
        self._content_context_uuid = None


class MockMicroblogContext(Acquisition.Implicit):
    implements(IMicroblogContext)


class TestStatusContainer_Delete(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.container = StatusContainer()
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

    def test_admin_delete(self):
        login(self.portal, 'user_steve')
        su = StatusUpdate('foo')
        self.container.add(su)
        login(self.portal, 'user_admin')
        self.container.delete(su.id)
        with self.assertRaises(KeyError):
            self.container.get(su.id)

    def test_creator_delete(self):
        login(self.portal, 'user_steve')
        su = StatusUpdate('foo')
        self.container.add(su)
        self.container.delete(su.id)
        with self.assertRaises(KeyError):
            self.container.get(su.id)

    def test_other_cannot_delete(self):
        login(self.portal, 'user_steve')
        su = StatusUpdate('foo')
        self.container.add(su)
        login(self.portal, 'user_jane')
        with self.assertRaises(Unauthorized):
            self.container.delete(su.id)

    def test_anon_cannot_delete(self):
        logout()
        su = StatusUpdate('foo')
        self.container.add(su)
        login(self.portal, 'user_jane')
        with self.assertRaises(Unauthorized):
            self.container.delete(su.id)

    def test_status_mapping(self):
        su = StatusUpdate('foo')
        self.container.add(su)
        self.assertEquals(su, self.container._status_mapping.get(su.id))
        self.container.delete(su.id)
        self.assertEquals(None, self.container._status_mapping.get(su.id))

    def test_user_mapping(self):
        login(self.portal, 'user_steve')
        su = StatusUpdate('foo')
        self.container.add(su)
        found = [x for x in self.container._user_mapping.get('user_steve')]
        self.assertIn(su.id, found)
        self.container.delete(su.id)
        found = [x for x in self.container._user_mapping.get('user_steve')]
        self.assertNotIn(su.id, found)

    def test_tag_mapping(self):
        su = StatusUpdate('foo', tags=['foo', 'bar'])
        self.container.add(su)
        found = [x for x in self.container._tag_mapping.get('bar')]
        self.assertIn(su.id, found)
        self.container.delete(su.id)
        found = [x for x in self.container._tag_mapping.get('bar')]
        self.assertNotIn(su.id, found)

    def test_uuid_mapping(self):
        m_context = MockMicroblogContext()
        su = UUIDStatusUpdate('foo', microblog_context=m_context)
        uuid = su._microblog_context_uuid
        container = UUIDStatusContainer()
        container.add(su)
        found = [x for x in container._uuid_mapping.get(uuid)]
        self.assertIn(su.id, found)
        container.delete(su.id)
        found = [x for x in container._uuid_mapping.get(uuid)]
        self.assertNotIn(su.id, found)

    def test_content_uuid_mapping(self):
        c_context = object()
        su = UUIDStatusUpdate('foo', content_context=c_context)
        uuid = su._content_context_uuid
        container = UUIDStatusContainer()
        container.add(su)
        found = [x for x in container._content_uuid_mapping.get(uuid)]
        self.assertIn(su.id, found)
        container.delete(su.id)
        found = [x for x in container._content_uuid_mapping.get(uuid)]
        self.assertNotIn(su.id, found)

    def test_threadid_mapping(self):
        parent = ContextlessStatusUpdate('parent')
        self.container.add(parent)
        su = ContextlessStatusUpdate('child', thread_id=parent.id)
        self.container.add(su)
        found = [x for x in self.container._threadid_mapping.get(parent.id)]
        self.assertIn(su.id, found)
        self.container.delete(su.id)
        found = [x for x in self.container._threadid_mapping.get(parent.id)]
        self.assertNotIn(su.id, found)

    def test_mentions_mapping(self):
        su = StatusUpdate('foo', mention_ids=['user_steve', ])
        self.container.add(su)
        found = [x for x in self.container._mentions_mapping.get('user_steve')]
        self.assertIn(su.id, found)
        self.container.delete(su.id)
        found = [x for x in self.container._mentions_mapping.get('user_steve')]
        self.assertNotIn(su.id, found)

    def test_delete_reply(self):
        pass

    def test_delete_thread(self):
        pass
