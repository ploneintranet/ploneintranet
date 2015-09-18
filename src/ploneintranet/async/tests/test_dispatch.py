import random
import subprocess
import time
import transaction

import redis.exceptions

from ploneintranet.async.browser.status import get_checksum
from ploneintranet.async.tasks import Post

from ploneintranet.async.testing import IntegrationTestCase
from ploneintranet.async.testing import FunctionalTestCase


class TestDispatch(IntegrationTestCase):

    def test_redis(self):
        """
        Verify that redis is running.

        Required for other tests.
        """
        self.assertTrue(self.redis_running(), "redis server not reachable")

    def test_celery(self):
        """Verify that celery worker is running.

        Required for other tests.
        """
        # pwd = /(buildout:dir)/parts/test
        cmd = '../../bin/celery -A ploneintranet.async.celerytasks status'
        try:
            res = subprocess.check_output(cmd.split(' '))
            self.assertTrue("online" in res, "no celery workers online")
        except subprocess.CalledProcessError:
            self.fail("celery worker is not available")

    def test_task(self):
        """Verify delayed task execution"""
        # delay import with side effects until after setup
        from ploneintranet.async.celerytasks import add
        try:
            result = add.delay(2, 2, 1)
        except redis.exceptions.ConnectionError:
            self.fail("redis not available")
        self.assertFalse(result.ready(), "result should be delayed")
        time.sleep(1)
        if not result.ready():
            time.sleep(1)  # catch unexpected delay
        self.assertTrue(result.ready(), "result should've been ready")
        self.assertEqual(result.get(), 4)


class TestPost(FunctionalTestCase):

    def test_post(self):
        """Verify http post async task execution"""
        if not self.redis_running():
            self.fail("requires redis")
            return

        self.basic_auth()  # set up basic authentication
        url = '@@async-checktask'
        checksum = random.random()
        data = dict(checksum=checksum)
        result = Post(self.portal, self.request)(url, data)
        self.waitfor(result)
        # we need to commit in order to see the other transaction
        transaction.commit()
        try:
            got_checksum = get_checksum()
        except KeyError:
            self.fail('no checksum annotations available at all!')
        # the checksum got mangled a bit in transmission
        self.assertEqual(str(checksum), str(got_checksum))


# actual "business logic" task tests are in test_tasks
