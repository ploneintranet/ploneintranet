from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile

from zope.configuration import xmlconfig

class PlonesocialActivitystream(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import plonesocial.activitystream
        xmlconfig.file('configure.zcml',
                       plonesocial.activitystream,
                       context=configurationContext)


    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plonesocial.activitystream:default')

PLONESOCIAL_ACTIVITYSTREAM_FIXTURE = PlonesocialActivitystream()
PLONESOCIAL_ACTIVITYSTREAM_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(PLONESOCIAL_ACTIVITYSTREAM_FIXTURE, ),
                       name="PlonesocialActivitystream:Integration")