import collections
import json
import os
import subprocess
import sys
import time

from plone.app.robotframework.testing import PLONE_ROBOT_TESTING
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import IntegrationTesting, PloneSandboxLayer
from plone.app.testing import FunctionalTesting
from plone.testing import Layer
from plone.testing import z2
from zope.component import getUtility
import pkg_resources
import requests

from .. import testing

try:
    # Skip all SOLR tests and layers if SOLR has not been activated
    # (by checking availability of 'scorched' package)
    pkg_resources.get_distribution('scorched')
    SOLR_ENABLED = True
except pkg_resources.DistributionNotFound:
    SOLR_ENABLED = False

# /app/parts/test/../../bin => /app/bin
_BUILDOUT_BIN_DIR = os.path.abspath(
    os.path.join(os.getcwd(), os.pardir, os.pardir, 'bin'))


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
            solr_basepath='/solr'):
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
        """Start Solr and poll until it is up and running.
        """
        super(SolrLayer, self).setUp()
        if not SOLR_ENABLED:
            return

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
        """Stop Solr.
        """
        super(SolrLayer, self).tearDown()
        if not SOLR_ENABLED:
            return
        self._solr_cmd('stop')


SOLR_FIXTURE = SolrLayer()


NamedBaseLayers = collections.namedtuple(
    'NamedBaseLayers', ('pisearch', 'solr')
)


class PloneIntranetSearchSolrLayer(PloneSandboxLayer):
    """ Basic Plone layer with SOLR support """

    defaultBases = NamedBaseLayers(testing.FIXTURE, SOLR_FIXTURE)

    def setUpZope(self, app, configuration_context):
        super(PloneIntranetSearchSolrLayer, self).setUpZope(
            app,
            configuration_context
        )
        if not SOLR_ENABLED:
            return

        import ploneintranet.search.solr
        self.loadZCML(package=ploneintranet.search.solr)
        self.loadZCML(package=ploneintranet.search.solr,
                      name='testing.zcml')

    def testTearDown(self):
        if not SOLR_ENABLED:
            return

        from .interfaces import IMaintenance
        getUtility(IMaintenance).purge()


class PloneIntranetSearchSolrTestContentLayer(PloneIntranetSearchSolrLayer):
    """ Layer with SOLR support *and* example content """

    defaultBases = (testing.FIXTURE, SOLR_FIXTURE,
                    PLONE_APP_CONTENTTYPES_FIXTURE)

    def setUpZope(self, app, configuration_context):
        super(PloneIntranetSearchSolrTestContentLayer, self).setUpZope(
            app, configuration_context,
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

        if not SOLR_ENABLED:
            return

        # Final purge
        from .interfaces import IMaintenance
        getUtility(IMaintenance).purge()

    def testTearDown(self):
        # Skip purging after every test
        pass

FIXTURE = PloneIntranetSearchSolrLayer()
TEST_CONTENT_FIXTURE = PloneIntranetSearchSolrTestContentLayer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='PloneIntranetSearchSolrLayer:Integration'
)

ROBOT_TESTING = FunctionalTesting(
    bases=(TEST_CONTENT_FIXTURE,
           PLONE_ROBOT_TESTING,
           z2.ZSERVER_FIXTURE),
    name="PloneIntranetSearchSolrLayer:")


class IntegrationTestCase(testing.IntegrationTestCase):

    _last_response = NotImplemented

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        if not SOLR_ENABLED:
            self.skipTest('Skipping SOLR tests - SOLR not enabled')

    def failureException(self, msg):
        if isinstance(self._last_response, str):
            from pprint import pprint
            pprint(json.loads(self._last_response))
        return super(IntegrationTestCase, self).failureException(msg)
