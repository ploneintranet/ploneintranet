from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class PlonesocialmessagingLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plonesocial.messaging
        xmlconfig.file(
            'configure.zcml',
            plonesocial.messaging,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plonesocial.messaging:default')

PLONESOCIAL_MESSAGING_FIXTURE = PlonesocialmessagingLayer()
PLONESOCIAL_MESSAGING_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONESOCIAL_MESSAGING_FIXTURE,),
    name="PlonesocialmessagingLayer:Integration"
)
PLONESOCIAL_MESSAGING_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONESOCIAL_MESSAGING_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PlonesocialmessagingLayer:Functional"
)
