import time
import Queue
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import applyProfile
from plone.testing import Layer
from plone.testing import z2
from plone.testing import zca

from zope.configuration import xmlconfig


def tearDownContainer(container):
    from plonesocial.microblog.statuscontainer import STATUSQUEUE
    # stop the thread timer
    try:
        container._v_timer.cancel()
        time.sleep(1)  # allow for thread cleanup
    except AttributeError:
        pass

    # we have an in-memory queue, purge it
    while True:
        try:
            STATUSQUEUE.get(block=False)
        except Queue.Empty:
            break


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


class PlonesocialMicroblogSubcriber(Layer):

    defaultBases = (PLONESOCIAL_MICROBLOG_FIXTURE,)

    def __init__(self, zcml_file):
        super(PlonesocialMicroblogSubcriber, self).__init__()
        self.zcml_file = zcml_file

    def setUp(self):
        self['configurationContext'] = context = zca.stackConfigurationContext(
            self.get('configurationContext')
        )
        import plonesocial.microblog
        xmlconfig.file(
            self.zcml_file,
            plonesocial.microblog,
            context=context
        )

    def tearDown(self):
        del self['configurationContext']


PLONESOCIAL_MICROBLOG_PORTAL_SUBSCRIBER_FIXTURE = \
    PlonesocialMicroblogSubcriber('tests/testing_portal_subscriber.zcml')
PLONESOCIAL_MICROBLOG_PORTAL_SUBSCRIBER_INTEGRATION_TESTING = \
    IntegrationTesting(
        bases=(PLONESOCIAL_MICROBLOG_PORTAL_SUBSCRIBER_FIXTURE, ),
        name="PlonesocialMicroblogPortalSubscriber:Integration"
    )


PLONESOCIAL_MICROBLOG_REQUEST_SUBSCRIBER_FIXTURE = \
    PlonesocialMicroblogSubcriber('tests/testing_request_subscriber.zcml')
PLONESOCIAL_MICROBLOG_REQUEST_SUBSCRIBER_INTEGRATION_TESTING = \
    IntegrationTesting(
        bases=(PLONESOCIAL_MICROBLOG_REQUEST_SUBSCRIBER_FIXTURE, ),
        name="PlonesocialMicroblogRequestSubscriber:Integration"
    )
