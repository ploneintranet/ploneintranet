import datetime
import socket
import subprocess
import time
import redis.exceptions

from Products.Five.browser import BrowserView
from ploneintranet.async.celerytasks import add


class StatusView(BrowserView):
    """
    Helper view for portal managers to manually check async.

    This re-implements rather than re-uses some of the tests
    from test_dispatch, because the port setup for interactive
    testing is likely to be different from the test fixture.
    """

    def time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def ok(self, check, msg='...'):
        return "[OK] %s: %s" % (check, msg)

    def fail(self, check, msg='...'):
        return "FAIL %s: %s!" % (check, msg)

    def warn(self, check, msg='...'):
        return "WARN %s: %s!" % (check, msg)

    def redis_running(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res = sock.connect_ex(('127.0.0.1', 6379))
        sock.close()
        if res == 0:
            return self.ok('redis', 'running OK.')
        else:
            return self.fail('redis', 'not available')

    def celery_running(self):
        cmd = 'bin/celery -A ploneintranet.async.celerytasks status'
        try:
            res = subprocess.check_output(cmd.split(' '))
            # drop terminal prompt from output
            res = res.strip().split('\n')[-1]
            return self.ok('celery', res)

        except subprocess.CalledProcessError:
            return self.fail('celery', 'no worker available')

    def task_roundtrip(self):
        try:
            result = add.delay(2, 2, 1)
        except redis.exceptions.ConnectionError:
            return self.fail("task", "redis not available")
        if result.ready():
            if result.get() == 4:
                return self.warn("task", "runs sync (output OK).")
            else:
                return self.fail("task", "runs sync (invalid)")
        i = 0
        while i < 5:
            time.sleep(1)
            i += 1
            if result.ready():
                break
        if not result.ready():
            return self.fail("task", "no result after %s seconds" % i)
        else:
            return self.ok("task", "completed asynchronously.")
