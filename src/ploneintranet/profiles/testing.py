from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.tiles.testing import PLONE_APP_TILES_FIXTURE
from plone.testing import z2
from zope.configuration import xmlconfig

import ploneintranet.profiles


class PloneintranetprofilesLayer(PloneSandboxLayer):

    defaultBases = (
        PLONE_APP_CONTENTTYPES_FIXTURE,
        PLONE_APP_TILES_FIXTURE
    )

    products = ('Products.membrane', )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.profiles,
            context=configurationContext
        )
        for p in self.products:
            z2.installProduct(app, p)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.profiles:default')

    def tearDownZope(self, app):
        """Tear down Zope."""
        for p in reversed(self.products):
            z2.uninstallProduct(app, p)


PLONEINTRANET_PROFILES_FIXTURE = PloneintranetprofilesLayer()

PLONEINTRANET_PROFILES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEINTRANET_PROFILES_FIXTURE,),
    name="PloneintranetprofilesLayer:Integration"
)
PLONEINTRANET_PROFILES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEINTRANET_PROFILES_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneintranetprofilesLayer:Functional"
)
