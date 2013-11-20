from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.testing import z2


class PloneIntranetSuite(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ploneintranet.suite
        self.loadZCML(package=ploneintranet.suite)
        # Install product and call its initialize() function
        z2.installProduct(app, 'ploneintranet.suite')

        # dependencies
        import ploneintranet.workspace
        self.loadZCML(package=ploneintranet.workspace)
        z2.installProduct(app, 'ploneintranet.workspace')

        import collective.workspace
        self.loadZCML(package=collective.workspace)
        z2.installProduct(app, 'collective.workspace')

        # plone social dependancies
        import plonesocial.microblog
        self.loadZCML(package=plonesocial.microblog)

        import plonesocial.activitystream
        self.loadZCML(package=plonesocial.activitystream)

        import plonesocial.network
        self.loadZCML(package=plonesocial.network)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'ploneintranet.suite:default')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'ploneintranet.suite')


PLONEINTRANET_SUITE = PloneIntranetSuite()

PLONEINTRANET_SUITE_INTEGRATION = IntegrationTesting(
    bases=(PLONEINTRANET_SUITE, ),
    name="PLONEINTRANET_SUITE_INTEGRATION")

PLONEINTRANET_SUITE_FUNCTIONAL = FunctionalTesting(
    bases=(PLONEINTRANET_SUITE, ),
    name="PLONEINTRANET_SUITE_FUNCTIONAL")

PLONEINTRANET_SUITE_ROBOT = FunctionalTesting(
    bases=(PLONEINTRANET_SUITE,
           AUTOLOGIN_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="PLONEINTRANET_SUITE_ROBOT")
