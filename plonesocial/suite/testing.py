from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile

from zope.configuration import xmlconfig

class PlonesocialSuite(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import plonesocial.suite
        xmlconfig.file('configure.zcml',
                       plonesocial.suite,
                       context=configurationContext)


    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plonesocial.suite:default')

PLONESOCIAL_SUITE_FIXTURE = PlonesocialSuite()
PLONESOCIAL_SUITE_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(PLONESOCIAL_SUITE_FIXTURE, ),
                       name="PlonesocialSuite:Integration")