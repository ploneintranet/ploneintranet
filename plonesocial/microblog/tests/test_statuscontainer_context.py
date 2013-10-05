import unittest2 as unittest
from zope.interface import implements
from zope.interface import alsoProvides
import Acquisition
from plone.uuid.interfaces import IUUID

from plonesocial.microblog.interfaces import IMicroblogContext
from plonesocial.microblog.interfaces import IStatusContainer
from plonesocial.microblog.interfaces import IStatusUpdate
from plonesocial.microblog import statuscontainer
from plonesocial.microblog import statusupdate

from plone.app.testing import TEST_USER_ID, setRoles

from plonesocial.microblog.testing import \
    PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING


class UUIDStatusContainer(statuscontainer.BaseStatusContainer):
    """Override actual implementation with unittest features"""

    implements(IStatusContainer)

    def _check_permission(self, perm="read"):
        pass


class StatusContainer(UUIDStatusContainer):

    def _context2uuid(self, context):
        return repr(context)


class UUIDStatusUpdate(statusupdate.StatusUpdate):

    """Override actual implementation with unittest features"""

    implements(IStatusUpdate)

    def __init__(self, text, context=None, userid='dude', creator=None):
        statusupdate.StatusUpdate.__init__(self, text, context)
        self.userid = userid
        if creator:
            self.creator = creator
        else:
            self.creator = userid

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

    def test_add_context(self):
        container = StatusContainer()
        su = StatusUpdate('test')
        container.add(su, object())
        self.assertEqual(1, len(list(container.items())))

    def test_items_context_nofilter(self):
        container = StatusContainer()
        mockcontext = MockContext()
        su1 = StatusUpdate('test')
        su2 = StatusUpdate('foobar', context=mockcontext)
        container.add(su1)
        container.add(su2)
        self.assertEqual(2, len(list(container.items())))

    def test_items_context(self):
        container = StatusContainer()
        mockcontext = MockContext()
        su1 = StatusUpdate('test')
        su2 = StatusUpdate('foobar', context=mockcontext)
        su3 = StatusUpdate('boo baz', context=MockContext())
        container.add(su1)
        container.add(su2)
        container.add(su3)
        values = [x[1] for x in container.context_items(mockcontext,
                                                        nested=False)]
        self.assertEqual(1, len(values))
        self.assertEqual([su2], values)

    def test_items_tag_context(self):
        container = StatusContainer()
        mockcontext = MockContext()
        su1 = StatusUpdate('test #foo')
        su2 = StatusUpdate('test #foo #bar', context=mockcontext)
        su3 = StatusUpdate('test #bar', context=mockcontext)
        container.add(su1)
        container.add(su2)
        container.add(su3)
        values = [x[1] for x in container.context_items(mockcontext,
                                                        nested=False)]
        self.assertEqual([su3, su2], values)
        values = [x[1] for x in container.context_items(mockcontext,
                                                        tag='bar',
                                                        nested=False)]
        self.assertEqual([su3, su2], values)
        values = [x[1] for x in container.context_items(mockcontext,
                                                        tag='foo',
                                                        nested=False)]
        self.assertEqual([su2], values)

    def test_values_tag_context(self):
        container = StatusContainer()
        mockcontext = MockContext()
        su1 = StatusUpdate('test #foo')
        su2 = StatusUpdate('test #foo #bar', context=mockcontext)
        su3 = StatusUpdate('test #bar', context=mockcontext)
        container.add(su1)
        container.add(su2)
        container.add(su3)
        values = list(container.context_values(mockcontext,
                                               nested=False))
        self.assertEqual([su3, su2], values)
        values = list(container.context_values(mockcontext,
                                               tag='bar',
                                               nested=False))
        self.assertEqual([su3, su2], values)
        values = list(container.context_values(mockcontext,
                                               tag='foo',
                                               nested=False))
        self.assertEqual([su2], values)

    def test_allowed_status_keys(self):
        container = StatusContainer()
        mockcontext1 = MockContext()
        mockcontext2 = MockContext()

        su0 = StatusUpdate('test')
        container.add(su0)
        su1 = StatusUpdate('test', context=mockcontext1)
        container.add(su1)
        su2 = StatusUpdate('test', context=mockcontext2)
        container.add(su2)

        values = [container.get(id) for id in container.allowed_status_keys()]
        self.assertEqual([su0, su1, su2], values)

        uid_blacklist = [container._context2uuid(mockcontext1)]
        values = [container.get(id)
                  for id in container._allowed_status_keys(uid_blacklist)]
        self.assertEqual([su0, su2], values)

        uid_blacklist = [container._context2uuid(mockcontext1),
                         container._context2uuid(mockcontext2)]
        values = [container.get(id)
                  for id in container._allowed_status_keys(uid_blacklist)]
        self.assertEqual([su0], values)


class TestNestedStatusContainer(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

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

    def test_items_nestedcontext_nofilter_child_only(self):
        su1 = StatusUpdate('test')
        su2 = StatusUpdate('foobar', context=self.child_context)
        self.container.add(su1)
        self.container.add(su2)
        self.assertEqual(2, len(list(self.container.items())))

    def test_items_nestedcontext_nofilter_child_and_parent(self):
        su1 = UUIDStatusUpdate('test', context=self.parent_context)
        su2 = UUIDStatusUpdate('foobar', context=self.child_context)
        self.container.add(su1)
        self.container.add(su2)
        items = self.container.context_items(self.parent_context, nested=True)
        self.assertEqual(2, len(list(items)))

    def test_items_triplenestedcontext_nofilter_child_and_parent(self):
        su1 = UUIDStatusUpdate('test', context=self.parent_context)
        su2 = UUIDStatusUpdate('foobar', context=self.child_context)
        su3 = UUIDStatusUpdate('foobar', context=self.grandchild_context)
        self.container.add(su1)
        self.container.add(su2)
        self.container.add(su3)
        items = self.container.context_items(self.parent_context, nested=True)
        self.assertEqual(3, len(list(items)))

    def XXtest_items_nestedcontext_filterparent_child_and_parent(self):
        su1 = StatusUpdate('test', context=self.parent_context)
        su2 = StatusUpdate('foobar', context=self.child_context)
        self.container.add(su1)
        self.container.add(su2)
        items = self.container.context_items(self.parent_context)
        self.assertEqual(2, len(list(items)))
