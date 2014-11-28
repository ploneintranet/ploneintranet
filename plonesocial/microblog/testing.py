from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import applyProfile
from plone.testing import z2

from zope.configuration import xmlconfig


class PlonesocialMicroblog(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import plonesocial.microblog
        xmlconfig.file('configure.zcml',
                       plonesocial.microblog,
                       context=configurationContext)
        import ploneintranet.attachments
        self.loadZCML(package=ploneintranet.attachments)
        z2.installProduct(app, 'ploneintranet.attachments')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plonesocial.microblog:default')

PLONESOCIAL_MICROBLOG_FIXTURE = PlonesocialMicroblog()
PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(PLONESOCIAL_MICROBLOG_FIXTURE, ),
                       name="PlonesocialMicroblog:Integration")
