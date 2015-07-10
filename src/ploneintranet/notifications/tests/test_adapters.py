# -*- coding: utf-8 -*-
import time
from datetime import datetime
import transaction
from plone import api
from plone.app.testing.interfaces import TEST_USER_PASSWORD
from plone.app.testing.interfaces import TEST_USER_ROLES
from ploneintranet.notifications.testing import \
    PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING
from ploneintranet.notifications.testing import \
    PLONEINTRANET_NOTIFICATIONS_FUNCTIONAL_TESTING
from ploneintranet.microblog.statusupdate import StatusUpdate
from ploneintranet.microblog.testing import tearDownContainer
import unittest


class SetUpMixin(object):

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        # add another user
        self.pas = self.layer['portal']['acl_users']
        # We need another user
        self.pas.source_users.addUser(
            'test_user_adapters_',
            'test_user_adapters_',
            TEST_USER_PASSWORD
        )
        for role in TEST_USER_ROLES:
            self.pas.portal_role_manager.doAssignRoleToPrincipal(
                'test_user_adapters_',
                role
            )
        self.pas.portal_role_manager.doAssignRoleToPrincipal(
            'test_user_adapters_',
            'Contributor'
        )
        with api.env.adopt_user('test_user_adapters_'):
            api.user.get('test_user_adapters_').setProperties({
                'email': 'kelly@sjogren.se',
                'fullname': 'Kelly Sjögren',
            })  # randomly generated


class TestAdapters(SetUpMixin, unittest.TestCase):

    layer = PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING

    # These tests are disabled for now, as the implementation
    # is incomplete and missing any security considerations
    @unittest.skip('Skipping disabled features of pi.notifications')
    def test_page(self):
        ''' Let's try to create a page and inspect the created adapter
        '''
        with api.env.adopt_user('test_user_adapters_'):
            api.content.create(self.portal, 'Document', 'page1')

        pin = api.portal.get_tool('ploneintranet_notifications')
        message = pin.get_user_queue(api.user.get('test_user_adapters_'))[-1]

        self.assertEqual(message.predicate, 'GLOBAL_NOTICE')

        self.assertDictEqual(
            message.actors[0], {
                'fullname': 'Kelly Sj\xc3\xb6gren',
                'userid': 'test_user_adapters_',
                'email': 'kelly@sjogren.se'
            }
        )

        self.assertEqual(message.obj['id'], 'page1')
        self.assertEqual(message.obj['title'], 'page1')
        self.assertEqual(message.obj['url'], 'plone/page1')
        self.assertEqual(message.obj['read'], False)
        self.assertIsInstance(
            message.obj['message_last_modification_date'],
            datetime
        )


class TestStatusAdapters(SetUpMixin, unittest.TestCase):

    layer = PLONEINTRANET_NOTIFICATIONS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestStatusAdapters, self).setUp()
        transaction.commit()

    def tearDown(self):
        container = api.portal.get_tool('ploneintranet_microblog')
        tearDownContainer(container)

    # These tests are disabled for now, as the implementation
    # is incomplete and missing any security considerations
    @unittest.skip('Skipping disabled features of pi.notifications')
    def test_status_update(self):
        ''' Let's try to create a status_update and inspect the created adapter
        '''
        with api.env.adopt_user('test_user_adapters_'):
            su = StatusUpdate(u'Test à')
            pm = api.portal.get_tool('ploneintranet_microblog')
            pm.add(su)

        pin = api.portal.get_tool('ploneintranet_notifications')
        message = pin.get_user_queue(api.user.get('test_user_adapters_'))[-1]

        self.assertEqual(message.predicate, 'STATUS_UPDATE')

        self.assertDictEqual(
            message.actors[0], {
                'fullname': 'Kelly Sj\xc3\xb6gren',
                'userid': 'test_user_adapters_',
                'email': 'kelly@sjogren.se'
            }
        )

        self.assertIsInstance(message.obj['id'], long)
        self.assertEqual(message.obj['title'], u'Test \xe0')
        self.assertEqual(message.obj['url'], 'plone/@@stream/network')
        self.assertEqual(message.obj['read'], False)
        self.assertIsInstance(
            message.obj['message_last_modification_date'],
            datetime
        )

    # These tests are disabled for now, as the implementation
    # is incomplete and missing any security considerations
    @unittest.skip('Skipping disabled features of pi.notifications')
    def test_multiple_status_updates(self):
        ''' Let's try to create multiple status updates.

        This lets us enter into the threaded handling of status commits
        (where the commit is done at most once per second,
        in a separate thread)
        '''
        with api.env.adopt_user('test_user_adapters_'):
            pm = api.portal.get_tool('ploneintranet_microblog')
            # HIC SUNT LEONES
            #
            # The problem here is threaded queue flushing from the
            # status update container.
            # The objective is to run notifications adapters in a thread.
            # This however is complicated by the fact
            # that we have multiple transactions at once,
            # one here in the test (primary)
            # and another from the scheduled autoflush in another thread.
            # Once the latter one commits,
            # this transaction is hopelessly out of date
            # (keep in mind ZODB is MVCC)
            # and we must get a fresh new transaction.
            # To get this we can either commit or abort,
            # but if we commit, we have a conflict error
            # (this happens only in tests, really, I think due to DemoStorage)
            # so we must abort.
            # But if we abort, some status updates are going to be lost,
            # specifically the first and the last (more on this later).
            # So what we do is:
            #
            #  * Create a first expendable status
            #  * Create ten statuses we will test
            #  * Do some magic to ensure the damned threaded autoflush runs
            #  * Abort the transaction
            #  * PROFIT!
            #
            # Why the first status is lost?
            #
            # Because the queued autoflush "kicks in"
            # from the second status onward.
            # This means the first status gets added
            # within the "doomed" transaction (the one that we abort)
            # and not within the transaction that gets committed,
            # which is the one in the thread, so it gets lost.
            su = StatusUpdate(u'Test à FIRST')
            pm.add(su)
            for i in xrange(0, 10):
                su = StatusUpdate(u'Test à {}'.format(unicode(i + 1)))
                pm.add(su)
            time.sleep(2)
            if getattr(pm, '_v_timer', None) is not None:
                pm._v_timer.join()
            transaction.abort()
        pin = api.portal.get_tool('ploneintranet_notifications')
        messages = pin.get_user_queue(api.user.get('test_user_adapters_'))
        self.assertGreaterEqual(len(messages), 10)

        for i, message in enumerate(messages[-10:]):
            self.assertEqual(message.predicate, 'STATUS_UPDATE')
            self.assertEqual(message.obj['title'], u'Test à {}'.format(
                unicode(i + 1)
            ))
