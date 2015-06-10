# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.tiles.testing import PLONE_APP_TILES_FIXTURE
from plone.testing import z2
import collective.workspace
import collective.z3cform.chosen

import ploneintranet.suite
import ploneintranet.microblog
import ploneintranet.activitystream
import ploneintranet.network
import ploneintranet.messaging
import ploneintranet.core
import ploneintranet.microblog.statuscontainer
import ploneintranet.search
import ploneintranet.microblog.statuscontainer


class PloneIntranetSuite(PloneSandboxLayer):
    defaultBases = (
        PLONE_APP_CONTENTTYPES_FIXTURE,
        PLONE_APP_TILES_FIXTURE,
    )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        self.loadZCML(package=ploneintranet.suite)
        # Install product and call its initialize() function
        z2.installProduct(app, 'ploneintranet.suite')

        self.loadZCML(package=collective.workspace)
        z2.installProduct(app, 'collective.workspace')

        self.loadZCML(package=collective.z3cform.chosen)

        # plone social dependencies
        self.loadZCML(package=ploneintranet.microblog)

        self.loadZCML(package=ploneintranet.activitystream)
        self.loadZCML(package=ploneintranet.network)
        self.loadZCML(package=ploneintranet.messaging)
        self.loadZCML(package=ploneintranet.core)

        # Force microblog to disable async mode !!!
        ploneintranet.microblog.statuscontainer.MAX_QUEUE_AGE = 0

        self.loadZCML(package=ploneintranet.search)

    def setUpPloneSite(self, portal):
        # setup the default workflow
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'ploneintranet.suite:testing')

    def tearDownZope(self, app):
        # reset sync mode
        ploneintranet.microblog.statuscontainer.MAX_QUEUE_AGE = 1000
        # Uninstall product
        z2.uninstallProduct(app, 'ploneintranet.suite')


PLONEINTRANET_SUITE = PloneIntranetSuite()

PLONEINTRANET_SUITE_INTEGRATION = IntegrationTesting(
    bases=(PLONEINTRANET_SUITE,),
    name="PLONEINTRANET_SUITE_INTEGRATION")

PLONEINTRANET_SUITE_FUNCTIONAL = FunctionalTesting(
    bases=(PLONEINTRANET_SUITE,),
    name="PLONEINTRANET_SUITE_FUNCTIONAL")

PLONEINTRANET_SUITE_ROBOT = FunctionalTesting(
    bases=(PLONEINTRANET_SUITE,
           AUTOLOGIN_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="PLONEINTRANET_SUITE_ROBOT")
