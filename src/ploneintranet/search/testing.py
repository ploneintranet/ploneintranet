# -*- coding: utf-8 -*-
"""Base module for unittesting ploneintranet.search."""
import json
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from pprint import pprint

from plone import api
from plone.app import testing
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import PLONE_ROBOT_TESTING
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import Layer
from plone.testing import z2
from ploneintranet.testing import PLONEINTRANET_FIXTURE
from zope.component import getUtility
import ploneintranet.docconv.client
import ploneintranet.search
import requests
import transaction
import unittest2 as unittest


TEST_USER_1_NAME = 'icarus'

TEST_USER_1_EMAIL = 'icarus@ploneintranet.org'

# /app/parts/test/../../bin => /app/bin
_BUILDOUT_BIN_DIR = os.path.abspath(
    os.path.join(os.getcwd(), os.pardir, os.pardir, 'bin'))


@contextmanager
def login_session(username):
    """Temporarily login as another user.

    Re-logging-in the previous user after exiting the context.
    """
    portal = api.portal.get()
    prev_login = None
    try:
        if not api.user.is_anonymous():
            prev_login = api.user.get_current().getUserName()
        testing.logout()
        testing.login(portal, username)
        yield username
    finally:
        testing.logout()
        if prev_login:
            testing.login(portal, prev_login)


class SolrLayer(Layer):
    """A SOLR test layer that fires up and shuts down a SOLR instance.

    This layer can be used to unit test a Solr configuration without having to
    fire up Plone.
    """
    proc = None

    def __init__(
            self,
            bases=None,
            name=None,
            module=None,
            solr_host='localhost',
            solr_port=8984,
            solr_basepath='/solr'
    ):
        name = name if name is not None else type(self).__name__
        super(SolrLayer, self).__init__(bases, name, module)
        self.solr_host = solr_host
        self.solr_port = solr_port
        self.solr_basepath = solr_basepath
        self.solr_url = 'http://{0}:{1}{2}'.format(
            solr_host,
            solr_port,
            solr_basepath
        )

    def _solr_cmd(self, cmd):
        self.proc = subprocess.Popen(
            ['./solr-test', cmd],
            close_fds=True,
            cwd=_BUILDOUT_BIN_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        (out, err) = self.proc.communicate()
        print('SOLR instance (PID:{0.pid} : {1})'.format(self.proc, cmd))

    def setUp(self):
        """Start Solr and poll until it is up and running."""
        super(SolrLayer, self).setUp()
        self._solr_cmd('start')
        # Poll Solr until it is up and running
        solr_ping_url = '{0}/core1/admin/ping'.format(self.solr_url)
        n_attempts = 10
        i = 0
        while i < n_attempts:
            try:
                response = requests.get(solr_ping_url, timeout=1)
                if response.status_code == 200:
                    if '<str name="status">OK</str>' in response.text:
                        sys.stdout.write('[Solr Layer Connected] ')
                        sys.stdout.flush()
                        break
            except requests.ConnectionError:
                pass
            time.sleep(1)
            sys.stdout.write('.')
            sys.stdout.flush()
            i += 1

        if i == n_attempts:
            self._solr_cmd('stop')
            raise EnvironmentError('Solr Test Instance could not be started')

    def tearDown(self):
        """Stop Solr."""
        super(SolrLayer, self).tearDown()
        self._solr_cmd('stop')


SOLR_FIXTURE = SolrLayer()


class PloneintranetSearchLayer(PloneSandboxLayer):
    """Basic Plone layer with SOLR support."""

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,
                    PLONEINTRANET_FIXTURE,
                    SOLR_FIXTURE)

    def setUpZope(self, app, configuration_context):
        super(PloneintranetSearchLayer, self).setUpZope(
            app,
            configuration_context
        )
        self.loadZCML(package=ploneintranet.search)
        self.loadZCML(package=ploneintranet.search, name='testing.zcml')
        self.loadZCML(package=ploneintranet.docconv.client)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'ploneintranet.docconv.client:default')
        self.applyProfile(portal, 'ploneintranet.search:default')
        with login_session(testing.TEST_USER_NAME):
            api.user.create(username=TEST_USER_1_NAME, email=TEST_USER_1_EMAIL)

    def tearDownPloneSite(self, portal):
        with api.env.adopt_roles(roles=['Manager']):
            api.user.delete(username=TEST_USER_1_NAME)
        super(PloneintranetSearchLayer, self).tearDownPloneSite(portal)

    def testTearDown(self):
        from .interfaces import IMaintenance
        getUtility(IMaintenance).purge()


FIXTURE = PloneintranetSearchLayer()


class PloneintranetSearchSuiteLayer(PloneintranetSearchLayer):
    """ Layer with SOLR support *and* example content """

    def setUpZope(self, app, configuration_context):
        super(PloneintranetSearchSuiteLayer, self).setUpZope(
            app,
            configuration_context
        )
        import ploneintranet.suite
        self.loadZCML(package=ploneintranet.suite)

        import ploneintranet.microblog.statuscontainer
        ploneintranet.microblog.statuscontainer.MAX_QUEUE_AGE = 0

        z2.installProduct(app, 'collective.workspace')
        z2.installProduct(app, 'collective.indexing')
        z2.installProduct(app, 'Products.membrane')

    def setUpPloneSite(self, portal):
        # setup the default workflow
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'ploneintranet.suite:testing')

    def tearDownPloneSite(self, portal):
        self.applyProfile(portal, 'ploneintranet.suite:uninstall')
        # Final purge
        from .interfaces import IMaintenance
        getUtility(IMaintenance).purge()

    def testTearDown(self):
        # Skip purging after every test
        pass


INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='PloneIntranetSearchLayer:Integration'
)

FUNCTIONAL_TESTING = testing.FunctionalTesting(
    bases=(FIXTURE,),
    name='PloneintranetSearchLayer:Functional'
)

SUITE_FIXTURE = PloneintranetSearchSuiteLayer()


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING

    _last_response = NotImplemented

    def failureException(self, msg):
        if isinstance(self._last_response, str):
            pprint(json.loads(self._last_response))
        return super(IntegrationTestCase, self).failureException(msg)

    def _create_content(self, **kw):
        obj = api.content.create(**kw)
        obj.reindexObject()
        self._created.append(obj)
        return obj

    def _delete_content(self, obj):
        api.content.delete(obj=obj)

    def setUp(self):
        self._created = []
        super(IntegrationTestCase, self).setUp()

    def tearDown(self):
        super(IntegrationTestCase, self).tearDown()
        for obj in self._created:
            obj_id = obj.getId()
            if obj_id in self.layer['portal']:
                with api.env.adopt_roles(roles=['Manager']):
                    self._delete_content(obj)
            transaction.commit()


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING


ROBOT_TESTING = FunctionalTesting(
    bases=(SUITE_FIXTURE,
           PLONE_ROBOT_TESTING,
           z2.ZSERVER_FIXTURE),
    name='PloneintranetSearchLayer:'
)
