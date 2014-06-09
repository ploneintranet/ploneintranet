from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class PloneintranetsimplesharingLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ploneintranet.simplesharing
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.simplesharing,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')


PLONEINTRANET_SIMPLESHARING_FIXTURE = PloneintranetsimplesharingLayer()
PLONEINTRANET_SIMPLESHARING_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEINTRANET_SIMPLESHARING_FIXTURE,),
    name="PloneintranetsimplesharingLayer:Integration"
)
PLONEINTRANET_SIMPLESHARING_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEINTRANET_SIMPLESHARING_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneintranetsimplesharingLayer:Functional"
)
