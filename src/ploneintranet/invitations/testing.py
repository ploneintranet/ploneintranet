from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import helpers

from plone.testing import z2

from zope.configuration import xmlconfig


class PloneintranetinvitationsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ploneintranet.invitations
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.invitations,
            context=configurationContext
        )
        import collective.MockMailHost

        self.loadZCML(package=collective.MockMailHost)

        # Install product and call its initialize() function
        z2.installProduct(app, 'collective.MockMailHost')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'collective.MockMailHost')

    def setUpPloneSite(self, portal):
        helpers.quickInstallProduct(portal, 'collective.MockMailHost')

        helpers.applyProfile(portal, 'collective.MockMailHost:default')

PLONEINTRANET_INVITATIONS_FIXTURE = PloneintranetinvitationsLayer()
PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEINTRANET_INVITATIONS_FIXTURE,),
    name='PloneintranetinvitationsLayer:Integration'
)
PLONEINTRANET_INVITATIONS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEINTRANET_INVITATIONS_FIXTURE, z2.ZSERVER_FIXTURE),
    name='PloneintranetinvitationsLayer:Functional'
)
