import unittest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plone import api
from ploneintranet import api as pi_api
from ploneintranet.microblog.interfaces import IMicroblogTool
from zope.component import queryUtility

from ploneintranet.microblog.testing import \
    PLONEINTRANET_MICROBLOG_CONTENTUPDATES_TESTING


class TestMicroblogEvents(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_CONTENTUPDATES_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])
        self.container = queryUtility(IMicroblogTool)

    def test_microblog(self):
        # 1st run events disabled
        pi_api.microblog.events_disable(self.request)
        doc = api.content.create(
            container=self.portal,
            type='Document',
            title='My document',
        )
        self.assertEqual(0, len([x for x in self.container.values()]))
        api.content.transition(doc, to_state='published')
        found = [x for x in self.container.values()]
        self.assertEqual(0, len(found))
        # 2nd run with events enabled
        pi_api.microblog.events_enable(self.request)
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

    def test_events_fallbackrequest(self):
        # 1st run events disabled
        pi_api.events.disable_microblog()
        doc = api.content.create(
            container=self.portal,
            type='Document',
            title='My document',
        )
        self.assertEqual(0, len([x for x in self.container.values()]))
        api.content.transition(doc, to_state='published')
        found = [x for x in self.container.values()]
        self.assertEqual(0, len(found))
        # 2nd run with events enabled
        pi_api.events.enable_microblog()
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
