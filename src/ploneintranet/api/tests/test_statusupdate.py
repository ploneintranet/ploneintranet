import unittest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plone import api
from ploneintranet.api.testing import FunctionalTestCase
from ploneintranet import api as pi_api
from ploneintranet.microblog.statusupdate import StatusUpdate
from ploneintranet.microblog.interfaces import IMicroblogTool
from zope.component import queryUtility

from ploneintranet.microblog.testing import \
    PLONEINTRANET_MICROBLOG_CONTENTUPDATES_TESTING


class TestStatusUpdate(FunctionalTestCase):

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_create(self):
        setRoles(self.portal, TEST_USER_ID, ('Member',))
        text = 'Hello this is my update'
        update = pi_api.microblog.statusupdate.create(text)
        self.assertIsInstance(update, StatusUpdate)
        self.assertEqual(update.text, text)

    def test_get(self):
        setRoles(self.portal, TEST_USER_ID, ('Member',))
        update = pi_api.microblog.statusupdate.create('Test')
        update2 = pi_api.microblog.statusupdate.create('Test2')
        self.assertEqual(
            pi_api.microblog.statusupdate.get(update.id),
            update)
        self.assertEqual(
            pi_api.microblog.statusupdate.get(update2.id),
            update2)
        self.assertRaises(
            KeyError,
            pi_api.microblog.statusupdate.get, 999999999)


class TestStatusUpdateEvents(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_CONTENTUPDATES_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])
        self.container = queryUtility(IMicroblogTool)

    def test_events_disable_enable(self):
        # 1st run events disabled
        pi_api.microblog.statusupdate.events_disable(self.request)
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
        pi_api.microblog.statusupdate.events_enable(self.request)
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

    def test_events_disable_enable_fallbackrequest(self):
        # 1st run events disabled
        pi_api.microblog.statusupdate.events_disable()
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
        pi_api.microblog.statusupdate.events_enable()
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
