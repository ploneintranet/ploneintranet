import unittest2 as unittest
from zope.interface import implements
import Acquisition

from plonesocial.microblog.interfaces import IMicroblogContext
from plonesocial.microblog.interfaces import IStatusContainer
from plonesocial.microblog.interfaces import IStatusUpdate
from plonesocial.microblog import statuscontainer
from plonesocial.microblog import statusupdate


class StatusContainer(statuscontainer.BaseStatusContainer):
    """Override actual implementation with unittest features"""

    implements(IStatusContainer)

    def _check_permission(self, perm="read"):
        pass

    def _context2uuid(self, context):
        return repr(context)


class StatusUpdate(statusupdate.StatusUpdate):
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
        values = [x[1] for x in container.context_items(mockcontext)]
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
        values = [x[1] for x in container.context_items(mockcontext)]
        self.assertEqual([su3, su2], values)
        values = [x[1] for x in container.context_items(mockcontext,
                                                        tag='bar')]
        self.assertEqual([su3, su2], values)
        values = [x[1] for x in container.context_items(mockcontext,
                                                        tag='foo')]
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
        values = list(container.context_values(mockcontext))
        self.assertEqual([su3, su2], values)
        values = list(container.context_values(mockcontext,
                                               tag='bar'))
        self.assertEqual([su3, su2], values)
        values = list(container.context_values(mockcontext,
                                               tag='foo'))
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
