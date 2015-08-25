import os
import socket
import subprocess
import time

import redis.exceptions
from ploneintranet.async.testing import IntegrationTestCase


class TestDispatch(IntegrationTestCase):

    def test_environ(self):
        """Make sure async is switched on"""
        async_enabled = os.environ.get('ASYNC_ENABLED')
        self.assertEqual(async_enabled, 'true')

    def test_redis(self):
        """
        Verify that redis is running.

        Required for other tests.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res = sock.connect_ex(('127.0.0.1', 6379))
        sock.close()
        self.assertEqual(0, res, "redis server not reachable")

    def test_celery(self):
        """Verify that celery worker is running.

        Required for other tests.
        """
        cmd = '/app/bin/celery -A ploneintranet.async.celerytasks status'
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
