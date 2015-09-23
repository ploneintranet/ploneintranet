import unittest2 as unittest
from zope.interface import alsoProvides
from plone.uuid.interfaces import IUUID
from plone.app.testing import TEST_USER_ID, setRoles

from ploneintranet.microblog.testing import \
    PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING
from ploneintranet.microblog.statuscontainer import BaseStatusContainer
from ploneintranet.microblog.interfaces import IMicroblogContext
from ploneintranet.microblog import statusupdate


class StatusContainer(BaseStatusContainer):
    """we don't care about permission checks for the uuid integration"""

    def _check_add_permission(self, statusupdate):
        pass

    def _blacklist_microblogcontext_uuids(self):
        return []


class StatusUpdate(statusupdate.StatusUpdate):
    """Override actual implementation with test features.
    Does NOT override the uuid functionality.
    """

    def _init_userid(self):
        pass

    def _init_creator(self):
        pass


class TestUUIDIntegration(unittest.TestCase):
    """Verify plone.app.uuid integration for BaseStatusContainer
    and StatusUpdate"""

    layer = PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_statuscontainer_context2uuid(self):
        """Unittests fake uuids. Integration test with real uuids."""
        self.portal.invokeFactory('Folder', 'f1', title=u"Folder 1")
        f1 = self.portal['f1']
        container = StatusContainer()
        self.assertEquals(container._context2uuid(f1), IUUID(f1))

    def test_statusupdate_context2uuid(self):
        """Unittests fake uuids. Integration test with real uuids."""
        self.portal.invokeFactory('Folder', 'f1', title=u"Folder 1")
        f1 = self.portal['f1']
        update = StatusUpdate('test')
        self.assertEquals(update._context2uuid(f1), IUUID(f1))

    def test_statusupdate_context_roundtrip(self):
        """Unittests fake uuids. Integration test with real uuids."""
        self.portal.invokeFactory('Folder', 'f1', title=u"Folder 1")
        f1 = self.portal['f1']
        alsoProvides(f1, IMicroblogContext)
        update = StatusUpdate('test', microblog_context=f1)
        self.assertEquals(update.microblog_context, f1)

    def test_context_api(self):
        """Unittests fake uuids. Integration test with real uuids."""
        container = StatusContainer()
        self.portal.invokeFactory('Folder', 'f1', title=u"Folder 1")
        mockcontext1 = self.portal['f1']
        alsoProvides(mockcontext1, IMicroblogContext)
        self.portal.invokeFactory('Folder', 'f2', title=u"Folder 2")
        mockcontext2 = self.portal['f2']
        alsoProvides(mockcontext2, IMicroblogContext)
        su1 = StatusUpdate('test', tags=['foo'],
                           microblog_context=mockcontext1)
        su1.userid = 'arnold'
        su2 = StatusUpdate('test', tags=['foo'],
                           microblog_context=mockcontext2)
        su2.userid = 'arnold'
        su3 = StatusUpdate('test', tags=['foo', 'bar', ],
                           microblog_context=mockcontext2)
        su3.userid = 'arnold'
        su4 = StatusUpdate('test',
                           microblog_context=mockcontext2)
        su4.userid = 'bernard'
        container.add(su1)
        container.add(su2)
        container.add(su3)
        container.add(su4)
        values = [x[1] for x in container.context_items(
            mockcontext1,
            tag='foo')]
        self.assertEqual([su1], values)
        values = [x[1] for x in container.context_items(mockcontext1,
                                                        tag='bar')]
        self.assertEqual([], values)
        values = [x[1] for x in container.context_items(mockcontext2,
                                                        tag='foo')]
        self.assertEqual([su3, su2], values)
        values = [x[1] for x in container.context_items(mockcontext2)]
        self.assertEqual([su4, su3, su2], values)
        values = [x[1] for x in container.items()]
        self.assertEqual([su4, su3, su2, su1], values)
