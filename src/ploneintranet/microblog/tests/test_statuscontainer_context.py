import unittest2 as unittest
from zope.interface import implements
from zope.interface import alsoProvides
import Acquisition
from plone.uuid.interfaces import IUUID
from plone.app.testing import TEST_USER_ID, setRoles

from ploneintranet.microblog.interfaces import IMicroblogContext
from ploneintranet.microblog.interfaces import IStatusContainer
from ploneintranet.microblog import statuscontainer
from ploneintranet.microblog import statusupdate
from ploneintranet.microblog.testing import \
    PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING


class UUIDStatusContainer(statuscontainer.BaseStatusContainer):

    """Override actual implementation with unittest features"""

    implements(IStatusContainer)

    def _check_add_permission(self, statusupdate):
        pass

    def _blacklist_microblogcontext_uuids(self):
        try:
            return self.blacklist
        except AttributeError:
            return []


class StatusContainer(UUIDStatusContainer):

    def _context2uuid(self, context):
        return repr(context)


class UUIDStatusUpdate(statusupdate.StatusUpdate):

    """Override actual implementation with unittest features"""

    def _init_userid(self):
        pass

    def _init_creator(self):
        pass


class StatusUpdate(UUIDStatusUpdate):

    def _context2uuid(self, context):
        return repr(context)


class MockContext(Acquisition.Implicit):
    implements(IMicroblogContext)


class TestStatusContainer(unittest.TestCase):

    def setUp(self):
        self.container = StatusContainer()
        self.container.blacklist = []
        self.su1 = StatusUpdate('test', tags=['foo'])
        self.su1.userid = 'dude'
        self.mockcontext = MockContext()
        self.mockcontext2 = MockContext()
        self.su2 = StatusUpdate(
            'foobar',
            tags=['foo', 'bar'],
            microblog_context=self.mockcontext
        )
        self.su2.userid = 'dude'
        self.su3 = StatusUpdate(
            'boo baz',
            tags=['bar'],
            microblog_context=self.mockcontext
        )
        self.su3.userid = 'dude'
        self.su4 = StatusUpdate(
            'test',
            microblog_context=self.mockcontext2
        )
        self.su4.userid = 'dude'
        self.container.add(self.su1)
        self.container.add(self.su2)
        self.container.add(self.su3)
        self.container.add(self.su4)

    def test_items_context_nofilter(self):
        self.assertEqual(4, len(list(self.container.items())))

    def test_items_context(self):
        values = [x[1] for x in self.container.context_items(
            self.mockcontext,
            nested=False)]
        self.assertEqual(2, len(values))
        self.assertEqual([self.su3, self.su2], values)

    def test_items_tag_context(self):
        values = [x[1] for x in self.container.context_items(
            self.mockcontext,
            nested=False)]
        self.assertEqual([self.su3, self.su2], values)
        values = [x[1] for x in self.container.context_items(
            self.mockcontext,
            tag='bar',
            nested=False)]
        self.assertEqual([self.su3, self.su2], values)
        values = [x[1] for x in self.container.context_items(
            self.mockcontext,
            tag='foo',
            nested=False)]
        self.assertEqual([self.su2], values)

    def test_values_tag_context(self):
        values = list(self.container.context_values(
            self.mockcontext,
            nested=False))
        self.assertEqual([self.su3, self.su2], values)
        values = list(self.container.context_values(
            self.mockcontext,
            tag='bar',
            nested=False))
        self.assertEqual([self.su3, self.su2], values)
        values = list(self.container.context_values(
            self.mockcontext,
            tag='foo',
            nested=False))
        self.assertEqual([self.su2], values)

    def test_allowed_status_keys(self):
        values = [self.container.get(i) for i in
                  self.container.allowed_status_keys()]
        self.assertEqual([self.su1, self.su2, self.su3, self.su4], values)

        self.container.blacklist = [
            self.container._context2uuid(self.mockcontext)]
        values = [self.container.get(i)
                  for i in self.container.allowed_status_keys()]
        self.assertEqual([self.su1, self.su4], values)

        self.container.blacklist = [
            self.container._context2uuid(self.mockcontext),
            self.container._context2uuid(self.mockcontext2)]
        values = [self.container.get(i)
                  for i in self.container.allowed_status_keys()]
        self.assertEqual([self.su1], values)


class TestNestedStatusContainer(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.container = UUIDStatusContainer()
        parent_id = self.portal.invokeFactory('Folder', 'parent')
        self.parent_context = self.portal[parent_id]
        alsoProvides(self.parent_context, IMicroblogContext)
        self.parent_context.reindexObject()

        child_id = self.parent_context.invokeFactory('Folder', 'child')
        self.child_context = self.parent_context[child_id]
        alsoProvides(self.child_context, IMicroblogContext)
        self.child_context.reindexObject()

        grandchild_id = self.child_context.invokeFactory('Folder',
                                                         'grandchild')
        self.grandchild_context = self.child_context[grandchild_id]
        alsoProvides(self.grandchild_context, IMicroblogContext)
        self.grandchild_context.reindexObject()

    def test_nested_uuids(self):
        self.assertEqual(self.container.nested_uuids(self.parent_context),
                         [IUUID(self.parent_context),
                          IUUID(self.child_context),
                          IUUID(self.grandchild_context)])

    def test_items_nestedcontext_child(self):
        su1 = StatusUpdate('test')
        su1.userid = 'dude'
        su2 = StatusUpdate('foobar', microblog_context=self.child_context)
        su2.userid = 'dude'
        self.container.add(su1)
        self.container.add(su2)
        self.assertEqual(2, len(list(self.container.items())))

    def test_items_nestedcontext_child_and_parent(self):
        su1 = UUIDStatusUpdate('test', microblog_context=self.parent_context)
        su1.userid = 'dude'
        su2 = UUIDStatusUpdate('foobar', microblog_context=self.child_context)
        su2.userid = 'dude'
        self.container.add(su1)
        self.container.add(su2)
        items = self.container.context_items(self.parent_context, nested=True)
        self.assertEqual(2, len(list(items)))

    def test_items_nestedcontext_grandchild_and_child_and_parent(self):
        su1 = UUIDStatusUpdate('test', microblog_context=self.parent_context)
        su1.userid = 'dude'
        su2 = UUIDStatusUpdate('foobar', microblog_context=self.child_context)
        su2.userid = 'dude'
        su3 = UUIDStatusUpdate(
            'foobar',
            microblog_context=self.grandchild_context
        )
        su3.userid = 'dude'
        self.container.add(su1)
        self.container.add(su2)
        self.container.add(su3)
        items = self.container.context_items(self.parent_context, nested=True)
        self.assertEqual(3, len(list(items)))

    def test_items_nestedcontext_grandchild_and_child_no_parent(self):
        su2 = UUIDStatusUpdate('foobar', microblog_context=self.child_context)
        su2.userid = 'dude'
        su3 = UUIDStatusUpdate(
            'foobar',
            microblog_context=self.grandchild_context
        )
        su3.userid = 'dude'
        self.container.add(su2)
        self.container.add(su3)
        items = self.container.context_items(self.parent_context, nested=True)
        self.assertEqual(2, len(list(items)))

    def XXtest_items_nestedcontext_filterparent_child_and_parent(self):
        su1 = StatusUpdate('test', context=self.parent_context)
        su1.userid = 'dude'
        su2 = StatusUpdate('foobar', context=self.child_context)
        su2.userid = 'dude'
        self.container.add(su1)
        self.container.add(su2)
        items = self.container.context_items(self.parent_context)
        self.assertEqual(2, len(list(items)))
