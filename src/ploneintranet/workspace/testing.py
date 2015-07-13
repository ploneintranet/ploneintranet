import collective.externaleditor
import collective.workspace
import Products.CMFPlacefulWorkflow

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.tiles.testing import PLONE_APP_TILES_FIXTURE
from plone.testing import z2
from zope.configuration import xmlconfig

import ploneintranet.workspace
import ploneintranet.microblog
import ploneintranet.activitystream
import ploneintranet.invitations
import ploneintranet.layout
import ploneintranet.network
import ploneintranet.theme


class PloneintranetworkspaceLayer(PloneSandboxLayer):

    defaultBases = (
        PLONE_APP_CONTENTTYPES_FIXTURE,
        PLONE_APP_TILES_FIXTURE
    )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
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

        xmlconfig.file(
            'configure.zcml',
            collective.workspace,
            context=configurationContext
        )

        xmlconfig.file(
            'configure.zcml',
            ploneintranet.microblog,
            context=configurationContext
        )

        xmlconfig.file(
            'configure.zcml',
            ploneintranet.activitystream,
            context=configurationContext
        )

        xmlconfig.file(
            'configure.zcml',
            ploneintranet.invitations,
            context=configurationContext
        )

        xmlconfig.file(
            'configure.zcml',
            Products.CMFPlacefulWorkflow,
            context=configurationContext
        )

        xmlconfig.file(
            'configure.zcml',
            ploneintranet.layout,
            context=configurationContext
        )

        xmlconfig.file(
            'configure.zcml',
            ploneintranet.network,
            context=configurationContext
        )

        xmlconfig.file(
            'configure.zcml',
            ploneintranet.theme,
            context=configurationContext
        )

        xmlconfig.file(
            'configure.zcml',
            ploneintranet.todo,
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
        applyProfile(portal, 'ploneintranet.todo:default')
        applyProfile(portal, 'ploneintranet.layout:default')
        applyProfile(portal, 'ploneintranet.network:default')
        applyProfile(portal, 'ploneintranet.theme:default')
        applyProfile(portal, 'collective.externaleditor:default')

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
