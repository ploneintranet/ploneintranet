from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.tiles.testing import PLONE_APP_TILES_FIXTURE
from plone.testing import z2
from zope.configuration import xmlconfig


class PloneintranetworkspaceLayer(PloneSandboxLayer):

    defaultBases = (
        PLONE_APP_CONTENTTYPES_FIXTURE,
        PLONE_APP_TILES_FIXTURE
    )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ploneintranet.workspace
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.workspace,
            context=configurationContext
        )
        xmlconfig.includeOverrides(
            configurationContext,
            'overrides.zcml',
            package=ploneintranet.workspace,
        )

        import collective.workspace
        xmlconfig.file(
            'configure.zcml',
            collective.workspace,
            context=configurationContext
        )

        import plonesocial.microblog
        xmlconfig.file(
            'configure.zcml',
            plonesocial.microblog,
            context=configurationContext
        )

        import plonesocial.activitystream
        xmlconfig.file(
            'configure.zcml',
            plonesocial.activitystream,
            context=configurationContext
        )

        import ploneintranet.invitations
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.invitations,
            context=configurationContext
        )

        import Products.CMFPlacefulWorkflow
        xmlconfig.file(
            'configure.zcml',
            Products.CMFPlacefulWorkflow,
            context=configurationContext
        )

        import ploneintranet.theme
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.theme,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        z2.installProduct(app, 'collective.workspace')
        z2.installProduct(app, 'Products.CMFPlacefulWorkflow')

    def tearDownZope(self, app):
        # Uninstall products installed above
        z2.uninstallProduct(app, 'collective.workspace')
        z2.uninstallProduct(app, 'Products.CMFPlacefulWorkflow')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.workspace:default')
        applyProfile(portal, 'ploneintranet.theme:default')

PLONEINTRANET_WORKSPACE_FIXTURE = PloneintranetworkspaceLayer()

PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEINTRANET_WORKSPACE_FIXTURE,),
    name="PloneintranetworkspaceLayer:Integration"
)
PLONEINTRANET_WORKSPACE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEINTRANET_WORKSPACE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneintranetworkspaceLayer:Functional"
)
PLONEINTRANET_WORKSPACE_ROBOT_TESTING = FunctionalTesting(
    bases=(PLONEINTRANET_WORKSPACE_FIXTURE,
           AUTOLOGIN_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="PLONEINTRANET_WORKSPACE_ROBOT")
