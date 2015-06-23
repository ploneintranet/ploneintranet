# Plone Intranet global test setup
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2


class PloneIntranetLayer(PloneSandboxLayer):

    """Generic testing layer that performs any steps
    necessary for *all* tests within ploneintranet"""

    # Make sure we are using default DX types
    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Because collective.indexing doesn't tear down its monkey patches
        # *every* test in ploneintranet needs to have it configured correctly
        import collective.indexing
        self.loadZCML(package=collective.indexing)
        z2.installProduct(app, 'collective.indexing')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'collective.indexing')

PLONEINTRANET_FIXTURE = PloneIntranetLayer()
