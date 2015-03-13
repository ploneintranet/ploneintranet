# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import helpers
from plone.testing import z2
from zope.configuration import xmlconfig


class PloneintranetNotificationsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ploneintranet.notifications
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.notifications,
            context=configurationContext
        )
        import ploneintranet.microblog
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.microblog,
            context=configurationContext
        )

    def tearDownZope(self, app):
        pass

    def setUpPloneSite(self, portal):
        helpers.applyProfile(portal, 'plone.app.contenttypes:default')
        helpers.applyProfile(portal, 'ploneintranet.microblog:default')
        helpers.applyProfile(portal, 'ploneintranet.notifications:default')

PLONEINTRANET_NOTIFICATIONS_FIXTURE = PloneintranetNotificationsLayer()
PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEINTRANET_NOTIFICATIONS_FIXTURE,),
    name='PloneintranetNotificationsLayer:Integration'
)
PLONEINTRANET_NOTIFICATIONS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEINTRANET_NOTIFICATIONS_FIXTURE, z2.ZSERVER_FIXTURE),
    name='PloneintranetNotificationsLayer:Functional'
)
