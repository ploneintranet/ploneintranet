import datetime
import random
import socket
import subprocess
import time
import redis.exceptions
import logging

from Products.Five.browser import BrowserView
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides

from ploneintranet.async.celerytasks import add
from ploneintranet.async.interfaces import IAsyncRequest

logger = logging.getLogger(__name__)


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

    def check_user(self):
        if '__ac' in self.request.cookies:
            return self.ok("user", "Logged in as Plone user.")
        elif self.request._auth:
            return self.warn(
                "user",
                "Logged in as Zope user. Better to do this as a Plone user.")
        else:
            self.fail("user", "Cannot extract valid credentials.")

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

    def dispatch_roundtrip(self):
        """Verify async task execution via browser dispatch"""
        verify_checksum = self.request.get('checksum', None)
        url = '@@async-checktask'
        if not verify_checksum:
            return self._dispatch_initialize(url)
        else:
            return self._dispatch_verify(verify_checksum)

    def _dispatch_initialize(self, url):
        # intial dispatch of async task
        new_checksum = random.random()
        data = dict(checksum=new_checksum)
        try:
            request = IAsyncRequest(self.request)
            result = request.post(url, data)
        except redis.exceptions.ConnectionError:
            return self.fail("dispatch", "redis not available")
        msg = "<a href='?checksum=%s'>verify execution</a>" % new_checksum
        if result.ready():
            return self._dispatch_verify(new_checksum, 'SYNC')
        return self.warn("dispatch", "Job queued. %s" % msg)

    def _dispatch_verify(self, verify_checksum, mode='async'):
        # subsequent validation of async result
        got_checksum = get_checksum()
        if verify_checksum == got_checksum:
            return self.ok("dispatch", "%s execution verified" % mode)
        else:
            msg = "expected %s but got %s (%s)" % (
                verify_checksum, got_checksum, mode)
            return self.fail("dispatch", msg)


class CheckTaskView(BrowserView):
    """
    Helper view to check async browser call dispatch.

    StatusView delegates a task to this view and then
    checks that it has been executed asynchronously.

    This view sets a (random) checksum as an annotation on the portal
    and is able to get that annotation as well.

    Single-process deadlock is avoided as follows:
    - the annotation setter is delegated to this view via celery (async)
    - the annotation getter is called directly by StatusView (sync)

    You can also call this view directly, which is one of the main
    benefits of the ploneintranet async framework based on view delegation.
    In that case it will set the checksum if the `checksum` is
    set on the request (e.g. via ?checksum=whatever).
    If that variable is not set, it will return the existing checksum.

    This view bypasses CSRF, which is safe because the write is limited
    to a string annotation only.

    DO NOT BYPASS CSRF FOR ACTUAL BUSINESS OBJECT WRITES like file previews.
    Instead, include a proper authenticator in the POST data.
    """

    def __call__(self):
        """
        set: If `checksum` is set in request, write it to the zodb.
        get: Else return the existing `checksum`.
        """
        checksum = self.request.get('checksum', None)
        if checksum:
            alsoProvides(self.request, IDisableCSRFProtection)
            set_checksum(checksum)
            logger.info("Set checksum %s", checksum)
            return "Set checksum %s" % checksum
        else:
            try:
                got_checksum = get_checksum()
                logger.info("Got checksum %s", got_checksum)
                return "Got checksum %s" % got_checksum
            except KeyError:
                logger.warn("No checksum set yet.")
                return ("No checksum set yet. "
                        "Create one with ?checksum=foo")


# checksum get/set used by multiple views

KEY = "ploneintranet.async.status.checksum"


def set_checksum(checksum):
    # no CSRF, be paranoid
    safe_checksum = str(checksum)[:40]
    portal = api.portal.get()
    annotations = IAnnotations(portal)
    annotations[KEY] = safe_checksum


def get_checksum():
    portal = api.portal.get()
    annotations = IAnnotations(portal)
    return annotations[KEY]
