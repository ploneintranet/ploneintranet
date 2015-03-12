# -*- coding: utf-8 -*-
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2
from zope.configuration import xmlconfig


class PloneIntranetmessagingLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ploneintranet.messaging
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.messaging,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.messaging:default')


PLONEINTRANET_MESSAGING_FIXTURE = PloneIntranetmessagingLayer()
PLONEINTRANET_MESSAGING_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEINTRANET_MESSAGING_FIXTURE,),
    name='PloneIntranetmessagingLayer:Integration'
)
PLONEINTRANET_MESSAGING_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEINTRANET_MESSAGING_FIXTURE, z2.ZSERVER_FIXTURE),
    name='PloneIntranetmessagingLayer:Functional'
)
