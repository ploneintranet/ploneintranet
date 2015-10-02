# -*- coding: utf-8 -*-
"""Base module for unittesting."""
import base64
import os
import socket
import subprocess
import time
import unittest

from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD

from plone.testing import z2
from plone.testing import Layer

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from ploneintranet.testing import PLONEINTRANET_FIXTURE

from ploneintranet.async.celerytasks import app

# /app/parts/test/../../bin => /app/bin
_BUILDOUT_BIN_DIR = os.path.abspath(
    os.path.join(os.getcwd(), os.pardir, os.pardir, 'bin'))


class CeleryLayer(Layer):
    """A Celery test layer that fires up and shuts down a Celery worker,
    but only if there's not already a Celery worker running.
    """

    tasks = 'ploneintranet.async.celerytasks'

    def setUp(self):
        """Check whether celery is already running, else start a worker"""
        super(CeleryLayer, self).setUp()
        self.worker = None
        if not self._celery_running():
            self._celery_worker()

    def tearDown(self):
        """Stop celery but only if we started it"""
        if self.worker:
            self.worker.terminate()
        super(CeleryLayer, self).tearDown()

    def _celery_worker(self):
        command = ['%s/celery' % _BUILDOUT_BIN_DIR, '-A', self.tasks, 'worker']
        self.worker = subprocess.Popen(
            command,
            close_fds=True,
            cwd=_BUILDOUT_BIN_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print('Celery worker (PID:{0.pid})'.format(self.worker))

    def _celery_running(self):
        command = ['%s/celery' % _BUILDOUT_BIN_DIR, '-A', self.tasks, 'status']
        try:
            res = subprocess.check_output(
                command,
                stderr=subprocess.PIPE
            )
            return "online" in res
        except subprocess.CalledProcessError:
            return False


CELERY_FIXTURE = CeleryLayer()


class PloneintranetAsyncLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,
                    PLONEINTRANET_FIXTURE,
                    CELERY_FIXTURE)

    def setUp(self):
        """Activate the async stack"""
        super(PloneintranetAsyncLayer, self).setUp()
        # force async regardless of buildout config
        app.conf.CELERY_ALWAYS_EAGER = False

    def tearDown(self):
        """Restore original environment"""
        super(PloneintranetAsyncLayer, self).tearDown()

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import ploneintranet.async
        self.loadZCML(package=ploneintranet.async)

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ploneintranet.async:default')

    def tearDownZope(self, app):
        """Tear down Zope."""
        pass


FIXTURE = PloneintranetAsyncLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="PloneintranetAsyncLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, z2.ZSERVER_FIXTURE),  # NB ZServer enabled!
    name="PloneintranetAsyncLayer:Functional")


class BaseTestCase(unittest.TestCase):
    """Shared utils for integration and functional tests"""

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST
        self.basic_auth()

    def basic_auth(self,
                   username=TEST_USER_NAME,
                   password=TEST_USER_PASSWORD):
        # fake needed credentials at Post.__init__
        cred = base64.encodestring('%s:%s' % (username, password))
        self.request._auth = 'Basic %s' % cred.strip()

    def redis_running(self):
        """All tests require redis."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res = sock.connect_ex(('127.0.0.1', 6379))
        sock.close()
        return res == 0

    def waitfor(self, result, timeout=3.0):
        """Wait until result succeeds"""
        i = 0.0
        while not result.ready():
            time.sleep(.1)
            i += .1
            if i >= timeout:
                self.fail("Did not get a result in %s seconds" % i)


class IntegrationTestCase(BaseTestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(BaseTestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
