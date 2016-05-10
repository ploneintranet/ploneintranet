from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.tiles.testing import PLONE_APP_TILES_FIXTURE
from plone.testing import z2
from zope.configuration import xmlconfig

import Products.CMFPlacefulWorkflow
import ploneintranet.activitystream
import ploneintranet.invitations
import ploneintranet.layout
import ploneintranet.microblog
import ploneintranet.network
import ploneintranet.theme
import ploneintranet.userprofile
import ploneintranet.workspace


class PloneintranetworkspaceLayer(PloneSandboxLayer):

    defaultBases = (
        PLONE_APP_CONTENTTYPES_FIXTURE,
        PLONE_APP_TILES_FIXTURE,
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

        import collective.workspace
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

        xmlconfig.file(
            'configure.zcml',
            ploneintranet.search,
            context=configurationContext
        )

        xmlconfig.file(
            'configure.zcml',
            ploneintranet.docconv.client,
            context=configurationContext
        )
        import collective.indexing
        self.loadZCML(package=collective.indexing)
        z2.installProduct(app, 'collective.indexing')

        xmlconfig.file(
            'configure.zcml',
            ploneintranet.userprofile,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        z2.installProduct(app, 'collective.workspace')
        z2.installProduct(app, 'Products.CMFPlacefulWorkflow')
        z2.installProduct(app, 'Products.membrane')

    def tearDownZope(self, app):
        # Uninstall products installed above
        z2.uninstallProduct(app, 'collective.workspace')
        z2.uninstallProduct(app, 'Products.CMFPlacefulWorkflow')
        z2.uninstallProduct(app, 'collective.indexing')
        z2.uninstallProduct(app, 'Products.membrane')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'Products.membrane:default')
        applyProfile(portal, 'ploneintranet.workspace:default')
        applyProfile(portal, 'ploneintranet.todo:default')
        applyProfile(portal, 'ploneintranet.layout:default')
        applyProfile(portal, 'ploneintranet.network:default')
        applyProfile(portal, 'ploneintranet.search:default')
        applyProfile(portal, 'ploneintranet.docconv.client:default')
        applyProfile(portal, 'ploneintranet.theme:default')
        applyProfile(portal, 'collective.externaleditor:default')
        applyProfile(portal, 'ploneintranet.userprofile:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.acl_users.userFolderAddUser('admin', 'secret', ['Manager'], [])


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
