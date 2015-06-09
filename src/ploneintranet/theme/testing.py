# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig

import ploneintranet.theme


class PloneintranetThemeLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.theme,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.theme:default')


PLONEINTRANET_THEME_FIXTURE = PloneintranetThemeLayer()


PLONEINTRANET_THEME_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEINTRANET_THEME_FIXTURE,),
    name='PloneintranetThemeLayer:IntegrationTesting'
)


PLONEINTRANET_THEME_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEINTRANET_THEME_FIXTURE,),
    name='PloneintranetThemeLayer:FunctionalTesting'
)


PLONEINTRANET_THEME_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PLONEINTRANET_THEME_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='PloneintranetThemeLayer:AcceptanceTesting'
)
