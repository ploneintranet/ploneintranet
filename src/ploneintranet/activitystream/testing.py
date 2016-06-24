from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile

from zope.configuration import xmlconfig


class PloneIntranetActivitystream(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import ploneintranet.microblog
        xmlconfig.file('configure.zcml',
                       ploneintranet.microblog,
                       context=configurationContext)

        import plone.tiles
        xmlconfig.file('meta.zcml',
                       plone.tiles,
                       context=configurationContext)

        # Load ZCML for this package
        import ploneintranet.activitystream
        xmlconfig.file('configure.zcml',
                       ploneintranet.activitystream,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.microblog:default')
        applyProfile(portal, 'ploneintranet.activitystream:default')

PLONEINTRANET_ACTIVITYSTREAM_FIXTURE = PloneIntranetActivitystream()
PLONEINTRANET_ACTIVITYSTREAM_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(PLONEINTRANET_ACTIVITYSTREAM_FIXTURE, ),
                       name="PloneIntranetActivitystream:Integration")
PLONEINTRANET_ACTIVITYSTREAM_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(PLONEINTRANET_ACTIVITYSTREAM_FIXTURE, ),
                      name="PloneIntranetActivitystream:Functional")
