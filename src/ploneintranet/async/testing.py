from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import helpers

from plone.testing import z2

from zope.configuration import xmlconfig

from collective.celery.testing import CELERY

class PloneintranetasyncLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, CELERY, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ploneintranet.async
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.async,
            context=configurationContext
        )

    def tearDownZope(self, app):
        pass

    def setUpPloneSite(self, portal):
        helpers.applyProfile(portal, 'ploneintranet.async:default')


PLONEINTRANET_async_FIXTURE = PloneintranetasyncLayer()
PLONEINTRANET_async_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEINTRANET_async_FIXTURE,),
    name='PloneintranetasyncLayer:Integration'
)
PLONEINTRANET_async_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEINTRANET_async_FIXTURE, z2.ZSERVER_FIXTURE),
    name='PloneintranetasyncLayer:Functional'
)
