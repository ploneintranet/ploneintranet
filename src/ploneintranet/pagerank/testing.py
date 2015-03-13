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

        # we're loading all of ploneintranet so we can
        # use the included demo site for testing

        import ploneintranet.socialsuite
        self.loadZCML(package=ploneintranet.socialsuite)

        import ploneintranet.microblog
        self.loadZCML(package=ploneintranet.microblog)

        import ploneintranet.activitystream
        self.loadZCML(package=ploneintranet.activitystream)

        import ploneintranet.network
        self.loadZCML(package=ploneintranet.network)

        import plone.app.contenttypes
        self.loadZCML(
            'configure.zcml',
            package=plone.app.contenttypes,
        )

        import ploneintranet.socialtheme
        self.loadZCML(package=ploneintranet.socialtheme)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'plone.app.contenttypes:default')
        # Installs all the Plone stuff. Workflows etc.
        self.applyProfile(portal, 'Products.CMFPlone:testfixture')
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'ploneintranet.pagerank:testing')

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
