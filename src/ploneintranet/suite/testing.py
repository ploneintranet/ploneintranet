from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.testing import z2

import collective.workspace
import collective.z3cform.chosen
import slc.docconv
import collective.documentviewer


class PloneIntranetSuite(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ploneintranet
        self.loadZCML(package=ploneintranet)
        # Install product and call its initialize() function
        z2.installProduct(app, 'ploneintranet.suite')

        self.loadZCML(package=collective.workspace)
        z2.installProduct(app, 'collective.workspace')

        self.loadZCML(package=collective.z3cform.chosen)

        self.loadZCML(package=slc.docconv)

        self.loadZCML(package=collective.documentviewer)

        # plone social dependencies
        import ploneintranet.microblog
        self.loadZCML(package=ploneintranet.microblog)
        import ploneintranet.activitystream
        self.loadZCML(package=ploneintranet.activitystream)
        import ploneintranet.network
        self.loadZCML(package=ploneintranet.network)
        import ploneintranet.messaging
        self.loadZCML(package=ploneintranet.messaging)
        import ploneintranet.core
        self.loadZCML(package=ploneintranet.core)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'ploneintranet.suite:testing')

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
