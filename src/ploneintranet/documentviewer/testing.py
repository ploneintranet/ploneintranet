# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import helpers

from plone.testing import z2

from zope.configuration import xmlconfig


class PloneintranetdocumentviewerLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.contenttypes
        self.loadZCML(package=plone.app.contenttypes)
        import slc.docconv
        self.loadZCML(package=slc.docconv)
        import collective.documentviewer
        self.loadZCML(package=collective.documentviewer)
        import ploneintranet.attachments
        self.loadZCML(package=ploneintranet.attachments)
        import ploneintranet.docconv.client
        self.loadZCML(package=ploneintranet.docconv.client)
        z2.installProduct(app, 'ploneintranet.docconv.client')
        import ploneintranet.documentviewer
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.documentviewer,
            context=configurationContext
        )

    def tearDownZope(self, app):
        pass

    def setUpPloneSite(self, portal):
        helpers.applyProfile(portal, 'ploneintranet.documentviewer:default')

PLONEINTRANET_documentviewer_FIXTURE = PloneintranetdocumentviewerLayer()
PLONEINTRANET_documentviewer_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEINTRANET_documentviewer_FIXTURE,),
    name='PloneintranetdocumentviewerLayer:Integration'
)
PLONEINTRANET_documentviewer_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEINTRANET_documentviewer_FIXTURE, z2.ZSERVER_FIXTURE),
    name='PloneintranetdocumentviewerLayer:Functional'
)
