import time
import random
import unittest2 as unittest
from zope.interface import implements
from zope.interface.verify import verifyClass

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

class TestStatusContainer(unittest.TestCase):

    def test_add_context(self):
        container = StatusContainer()
        su = StatusUpdate('test')
        container.add(su, object())
        self.assertEqual(1, len(list(container.items())))

    def test_items_context_nofilter(self):
        container = StatusContainer()
        mockcontext = object()
        su1 = StatusUpdate('test')
        su2 = StatusUpdate('foobar', context=mockcontext)
        container.add(su1)
        container.add(su2)
        self.assertEqual(2, len(list(container.items())))

    def test_items_context(self):
        container = StatusContainer()
        mockcontext = object()
        su1 = StatusUpdate('test')
        su2 = StatusUpdate('foobar', context=mockcontext)
        su3 = StatusUpdate('boo baz', context=object())
        container.add(su1)
        container.add(su2)
        container.add(su3)
        values = [x[1] for x in container.items(context=mockcontext)]
        self.assertEqual(1, len(values))
        self.assertEqual([su2], values)

    def test_items_tag_context(self):
        container = StatusContainer()
        mockcontext = object()
        su1 = StatusUpdate('test #foo')
        su2 = StatusUpdate('test #foo #bar', context=mockcontext)
        su3 = StatusUpdate('test #bar', context=mockcontext)
        container.add(su1)
        container.add(su2)
        container.add(su3)
        values = [x[1] for x in container.items(context=mockcontext)]
        self.assertEqual([su3, su2], values)
        values = [x[1] for x in container.items(tag='bar',
                                                context=mockcontext)]
        self.assertEqual([su3, su2], values)
        values = [x[1] for x in container.items(tag='foo',
                                                context=mockcontext)]
        self.assertEqual([su2], values)

    def test_values_tag_context(self):
        container = StatusContainer()
        mockcontext = object()
        su1 = StatusUpdate('test #foo')
        su2 = StatusUpdate('test #foo #bar', context=mockcontext)
        su3 = StatusUpdate('test #bar', context=mockcontext)
        container.add(su1)
        container.add(su2)
        container.add(su3)
        values = list(container.values(context=mockcontext))
        self.assertEqual([su3, su2], values)
        values = list(container.values(tag='bar',
                                       context=mockcontext))
        self.assertEqual([su3, su2], values)
        values = list(container.values(tag='foo',
                                       context=mockcontext))
        self.assertEqual([su2], values)

    def test_user_values_tag_context(self):
        container = StatusContainer()
        mockcontext1 = object()
        mockcontext2 = object()
        su1 = StatusUpdate('test #foo', context=mockcontext1, userid='arnold')
        su2 = StatusUpdate('test #foo', context=mockcontext2, userid='arnold')
        su3 = StatusUpdate('test #foo #bar', context=mockcontext2, userid='arnold')
        su4 = StatusUpdate('test #foo #bar', context=mockcontext2, userid='bernard')
        container.add(su1)
        container.add(su2)
        container.add(su3)
        container.add(su4)
        values = list(container.user_values(['arnold'], tag='foo',
                                            context=mockcontext1))
        self.assertEqual([su1], values)
        values = list(container.user_values(['arnold'], tag='bar',
                                            context=mockcontext1))
        self.assertEqual([], values)
        values = list(container.user_values(['bernard'], tag='bar',
                                            context=mockcontext1))
        self.assertEqual([], values)
        values = list(container.user_values(['bernard'], tag='bar',
                                            context=mockcontext2))
        self.assertEqual([su4], values)
        values = list(container.user_values(['arnold'], tag='foo',
                                            context=mockcontext2))
        self.assertEqual([su3, su2], values)

    def test_items_values_tag_context(self):
        container = StatusContainer()
        mockcontext1 = object()
        mockcontext2 = object()
        su1 = StatusUpdate('test #foo', context=mockcontext1, userid='arnold')
        su2 = StatusUpdate('test #foo', context=mockcontext2, userid='arnold')
        su3 = StatusUpdate('test #foo #bar', context=mockcontext2, userid='arnold')
        su4 = StatusUpdate('test #foo #bar', context=mockcontext2, userid='bernard')
        container.add(su1)
        container.add(su2)
        container.add(su3)
        container.add(su4)
        values = [x[1] for x in container.user_items(['arnold'], tag='foo',
                                                      context=mockcontext1)]
        self.assertEqual([su1], values)
        values = [x[1] for x in container.user_items(['arnold'], tag='bar',
                                                      context=mockcontext1)]
        self.assertEqual([], values)
        values = [x[1] for x in container.user_items(['bernard'], tag='bar',
                                                      context=mockcontext1)]
        self.assertEqual([], values)
        values = [x[1] for x in container.user_items(['bernard'], tag='bar',
                                                      context=mockcontext2)]
        self.assertEqual([su4], values)
        values = [x[1] for x in container.user_items(['arnold'], tag='foo',
                                                      context=mockcontext2)]
        self.assertEqual([su3, su2], values)
