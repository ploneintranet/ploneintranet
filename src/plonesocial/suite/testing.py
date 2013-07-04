from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import applyProfile

from plone.testing import z2

from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE

from zope.configuration import xmlconfig


class PlonesocialSuite(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import plonesocial.suite
        import plonesocial.microblog
        import plonesocial.activitystream
        import plonesocial.network
        import plonesocial.theme
        xmlconfig.file('configure.zcml',
                       plonesocial.suite,
                       context=configurationContext)
        xmlconfig.file('configure.zcml',
                       plonesocial.microblog,
                       context=configurationContext)
        xmlconfig.file('configure.zcml',
                       plonesocial.activitystream,
                       context=configurationContext)
        xmlconfig.file('configure.zcml',
                       plonesocial.network,
                       context=configurationContext)
        xmlconfig.file('configure.zcml',
                       plonesocial.theme,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # Installs all the Plone stuff. Workflows etc.
        applyProfile(portal, 'Products.CMFPlone:testfixture')
        # use the demo profile for a populated test site
        applyProfile(portal, 'plonesocial.suite:demo')
        # demo profile does also provide default content
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory('Folder', 'f1', title=u"Folder 1")
        f1 = portal['f1']
        f1.invokeFactory('Document', 'd1', title=u"Test Document 1")


PLONESOCIAL_SUITE_FIXTURE = PlonesocialSuite()

PLONESOCIAL_SUITE_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(PLONESOCIAL_SUITE_FIXTURE, ),
                       name="PlonesocialSuite:Integration")

PLONESOCIAL_ROBOT_TESTING = FunctionalTesting(
    bases=(AUTOLOGIN_LIBRARY_FIXTURE, PLONESOCIAL_SUITE_FIXTURE, z2.ZSERVER),
    name="PloneSocial:Robot")


from Testing.ZopeTestCase.threadutils import setNumberOfThreads
from Testing.ZopeTestCase.threadutils import QuietThread, zserverRunner
import time


def startZServer(host='127.0.0.1', number_of_threads=1, log=None):
    '''Starts an HTTP ZServer thread.'''
    _Z2HOST = host
    _Z2PORT = 55555
    setNumberOfThreads(number_of_threads)
    t = QuietThread(target=zserverRunner, args=(_Z2HOST, _Z2PORT, log))
    t.setDaemon(1)
    t.start()
    time.sleep(0.1)  # Sandor Palfy
    return 'http://%s:%s/plone' % (_Z2HOST, _Z2PORT)
