from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile

from zope.configuration import xmlconfig

class PlonesocialNetwork(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import plonesocial.network
        xmlconfig.file('configure.zcml',
                       plonesocial.network,
                       context=configurationContext)


    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plonesocial.network:default')

PLONESOCIAL_NETWORK_FIXTURE = PlonesocialNetwork()
PLONESOCIAL_NETWORK_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(PLONESOCIAL_NETWORK_FIXTURE, ),
                       name="PlonesocialNetwork:Integration")