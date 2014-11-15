from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.testing import z2


class PloneIntranetPagerank(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ploneintranet.pagerank
        self.loadZCML(package=ploneintranet.pagerank)
        # Install product and call its initialize() function
        z2.installProduct(app, 'ploneintranet.pagerank')

        # dependencies
        import plonesocial.suite
        self.loadZCML(package=plonesocial.suite)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'ploneintranet.pagerank:default')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'ploneintranet.pagerank')


PLONEINTRANET_PAGERANK = PloneIntranetPagerank()

PLONEINTRANET_PAGERANK_INTEGRATION = IntegrationTesting(
    bases=(PLONEINTRANET_PAGERANK, ),
    name="PLONEINTRANET_PAGERANK_INTEGRATION")

PLONEINTRANET_PAGERANK_FUNCTIONAL = FunctionalTesting(
    bases=(PLONEINTRANET_PAGERANK, ),
    name="PLONEINTRANET_PAGERANK_FUNCTIONAL")

PLONEINTRANET_PAGERANK_ROBOT = FunctionalTesting(
    bases=(PLONEINTRANET_PAGERANK,
           AUTOLOGIN_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="PLONEINTRANET_PAGERANK_ROBOT")
