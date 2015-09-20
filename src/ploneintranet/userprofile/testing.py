from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig

from ploneintranet.testing import PLONEINTRANET_FIXTURE
import ploneintranet.userprofile


class PloneintranetuserprofileLayer(PloneSandboxLayer):

    defaultBases = (
        PLONE_APP_CONTENTTYPES_FIXTURE,
        PLONEINTRANET_FIXTURE
    )

    products = ('Products.membrane', )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.userprofile,
            context=configurationContext
        )
        for p in self.products:
            z2.installProduct(app, p)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.userprofile:testing')

    def tearDownZope(self, app):
        """Tear down Zope."""
        for p in reversed(self.products):
            z2.uninstallProduct(app, p)


PLONEINTRANET_USERPROFILE_FIXTURE = PloneintranetuserprofileLayer()

PLONEINTRANET_USERPROFILE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEINTRANET_USERPROFILE_FIXTURE,),
    name="PloneintranetuserprofileLayer:Integration"
)
PLONEINTRANET_USERPROFILE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEINTRANET_USERPROFILE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneintranetuserprofileLayer:Functional"
)
