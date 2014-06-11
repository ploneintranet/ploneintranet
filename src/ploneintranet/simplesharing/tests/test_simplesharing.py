import unittest
from Products.CMFDefault.Document import Document
from plone.behavior.interfaces import IBehaviorAssignable, IBehavior
from zope.component import adapts, queryUtility, getUtility
from zope.interface import implements

from ploneintranet.simplesharing.behaviors import ISimpleSharing
from ploneintranet.simplesharing.tests.base import BaseTestCase


class TestingAssignable(object):
    implements(IBehaviorAssignable)
    adapts(Document)

    enabled = [ISimpleSharing]

    def __init__(self, context):
        self.context = context

    def supports(self, behavior_interface):
        return behavior_interface in self.enabled

    def enumerate_behaviors(self):
        for e in self.enabled:
            yield queryUtility(IBehavior, name=e.__identifier__)


class TestBehaviors(BaseTestCase):

    @unittest.skip("skipping visibility test")
    def test_visibility(self):
        behavior = getUtility(
            IBehavior,
            name='ploneintranet.simplesharing.behaviors.ISimpleSharing',
        )
        self.assertEqual(behavior.interface, ISimpleSharing)
        doc = Document('doc')
        sharing_adapter = ISimpleSharing(doc)
        self.assertIsNotNone(sharing_adapter)
