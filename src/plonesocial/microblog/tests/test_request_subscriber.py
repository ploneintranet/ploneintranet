import time
import unittest2 as unittest
from threading import RLock
from zope.component import queryUtility

from plone import api

from plonesocial.microblog.testing import \
    PLONESOCIAL_MICROBLOG_REQUEST_SUBSCRIBER_INTEGRATION_TESTING
from plonesocial.microblog.testing import tearDownContainer

from plonesocial.microblog.interfaces import IMicroblogTool
from plonesocial.microblog.statusupdate import StatusUpdate


class RequestSubscriber(object):
    """This object is used to test that we can get the acquired global request
    (i.e. ``context.REQUEST``) within a status update subscription.
    """

    def __init__(self):
        self.lock = RLock()
        self.messages = []

    def __call__(self, obj, event):
        portal = api.portal.get()
        with self.lock:
            self.messages.append(
                (obj.text, portal.REQUEST.getURL())
            )


request_subscriber = RequestSubscriber()


class TestMicroblogRequestSubscriber(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_REQUEST_SUBSCRIBER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def tearDown(self):
        container = queryUtility(IMicroblogTool)
        tearDownContainer(container)

    def test_add_multi_portal(self):
        portal = api.portal.get()
        self.assertIsNotNone(portal)
        portal_request = portal.REQUEST
        tool = queryUtility(IMicroblogTool)
        for i in xrange(0, 10):
            su = StatusUpdate('Test {}'.format(str(i + 1)))
            if i == 5:
                time.sleep(1)
            # Next message triggers queue flush
            tool.add(su)
        # Here we need to sleep for some time to give the thread timer
        # queue committer in plonesocial.microblog
        # time to commit the statuses.
        time.sleep(2)
        self.assertEqual(
            request_subscriber.messages,
            [
                ('Test 1', portal_request.getURL()),
                ('Test 2', portal_request.getURL()),
                ('Test 3', portal_request.getURL()),
                ('Test 4', portal_request.getURL()),
                ('Test 5', portal_request.getURL()),
                ('Test 6', portal_request.getURL()),
                ('Test 7', portal_request.getURL()),
                ('Test 8', portal_request.getURL()),
                ('Test 9', portal_request.getURL()),
                ('Test 10', portal_request.getURL())
            ]
        )
