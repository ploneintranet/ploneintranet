import time
import Queue
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import TEST_USER_ID
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.testing import Layer
from plone.testing import z2
from plone.testing import zca

from zope.configuration import xmlconfig
from ploneintranet.testing import PLONEINTRANET_FIXTURE


def tearDownContainer(container):
    from ploneintranet.microblog.statuscontainer import STATUSQUEUE
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


class PloneIntranetMicroblog(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,
                    PLONEINTRANET_FIXTURE)

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import ploneintranet.microblog
        xmlconfig.file('configure.zcml',
                       ploneintranet.microblog,
                       context=configurationContext)
        # no content updates, except on
        #   PLONEINTRANET_MICROBLOG_CONTENTUPDATES_TESTING
        # run tests sync, except for test_statuscontainer_queued
        ploneintranet.microblog.statuscontainer.ASYNC = False
        import ploneintranet.activitystream
        xmlconfig.file('configure.zcml',
                       ploneintranet.activitystream,
                       context=configurationContext)
        import ploneintranet.attachments
        self.loadZCML(package=ploneintranet.attachments)
        z2.installProduct(app, 'ploneintranet.attachments')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.microblog:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])


PLONEINTRANET_MICROBLOG_FIXTURE = PloneIntranetMicroblog()
PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(PLONEINTRANET_MICROBLOG_FIXTURE, ),
                       name="PloneIntranetMicroblog:Integration")
PLONEINTRANET_MICROBLOG_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(PLONEINTRANET_MICROBLOG_FIXTURE, ),
                      name="PloneIntranetMicroblog:Functional")


class PloneIntranetMicroblogSubcriber(Layer):

    defaultBases = (PLONEINTRANET_MICROBLOG_FIXTURE, )

    def __init__(self, zcml_file):
        super(PloneIntranetMicroblogSubcriber, self).__init__()
        self.zcml_file = zcml_file

    def setUp(self):
        self['configurationContext'] = context = zca.stackConfigurationContext(
            self.get('configurationContext')
        )
        import ploneintranet.microblog
        ploneintranet.microblog.statuscontainer.ASYNC = False
        xmlconfig.file(
            self.zcml_file,
            ploneintranet.microblog,
            context=context
        )

    def tearDown(self):
        del self['configurationContext']


PLONEINTRANET_MICROBLOG_PORTAL_SUBSCRIBER_FIXTURE = \
    PloneIntranetMicroblogSubcriber('tests/testing_portal_subscriber.zcml')
PLONEINTRANET_MICROBLOG_PORTAL_SUBSCRIBER_INTEGRATION_TESTING = \
    IntegrationTesting(
        bases=(PLONEINTRANET_MICROBLOG_PORTAL_SUBSCRIBER_FIXTURE, ),
        name="PloneIntranetMicroblogPortalSubscriber:Integration"
    )

PLONEINTRANET_MICROBLOG_REQUEST_SUBSCRIBER_FIXTURE = \
    PloneIntranetMicroblogSubcriber('tests/testing_request_subscriber.zcml')
PLONEINTRANET_MICROBLOG_REQUEST_SUBSCRIBER_INTEGRATION_TESTING = \
    IntegrationTesting(
        bases=(PLONEINTRANET_MICROBLOG_REQUEST_SUBSCRIBER_FIXTURE, ),
        name="PloneIntranetMicroblogRequestSubscriber:Integration"
    )

PLONEINTRANET_MICROBLOG_CONTENTUPDATES_FIXTURE = \
    PloneIntranetMicroblogSubcriber('subscribers.zcml')
PLONEINTRANET_MICROBLOG_CONTENTUPDATES_TESTING = \
    FunctionalTesting(
        bases=(PLONEINTRANET_MICROBLOG_CONTENTUPDATES_FIXTURE, ),
        name="PloneIntranetMicroblogContentupdatesSubscriber:Functional"
    )
