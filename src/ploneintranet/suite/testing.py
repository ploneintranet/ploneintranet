# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.tiles.testing import PLONE_APP_TILES_FIXTURE
from plone.testing import z2

from ploneintranet.search.solr.testing import (SOLR_FIXTURE,
                                               PloneIntranetSearchSolrLayer)


class PloneIntranetSuite(PloneSandboxLayer):

    defaultBases = (
        PLONE_APP_CONTENTTYPES_FIXTURE,
        PLONE_APP_TILES_FIXTURE,
    )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ploneintranet.suite
        self.loadZCML(package=ploneintranet.suite)
        # Load resource to disable transitions and animations in robot tests
        import ploneintranet.suite.tests
        self.loadZCML(package=ploneintranet.suite.tests)
        # Install product and call its initialize() function
        z2.installProduct(app, 'ploneintranet.suite')

        import collective.workspace
        self.loadZCML(package=collective.workspace)
        z2.installProduct(app, 'collective.workspace')

        import ploneintranet.workspace
        self.loadZCML(package=ploneintranet.workspace)

        import collective.z3cform.chosen
        self.loadZCML(package=collective.z3cform.chosen)

        import collective.documentviewer
        self.loadZCML(package=collective.documentviewer)

        # plone social dependencies
        import ploneintranet.microblog
        self.loadZCML(package=ploneintranet.microblog)
        # enable event driven content updates
        self.loadZCML(name='subscribers.zcml',
                      package=ploneintranet.microblog)
        # Force microblog to disable async mode !!!
        import ploneintranet.microblog.statuscontainer
        ploneintranet.microblog.statuscontainer.ASYNC = False

        import ploneintranet.activitystream
        self.loadZCML(package=ploneintranet.activitystream)

        import ploneintranet.network
        self.loadZCML(package=ploneintranet.network)

        import ploneintranet.messaging
        self.loadZCML(package=ploneintranet.messaging)

        import ploneintranet.core
        self.loadZCML(package=ploneintranet.core)

        z2.installProduct(app, 'collective.indexing')
        z2.installProduct(app, 'Products.membrane')

        import ploneintranet.search
        self.loadZCML(package=ploneintranet.search)

        # WTF? AttributeError: 'module' object has no attribute 'startswith'
        # import ploneintranet.library
        # self.loadZCML(ploneintranet.library)

    def setUpPloneSite(self, portal):
        # setup the default workflow
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'ploneintranet.suite:testing')
        setRoles(portal, TEST_USER_ID, ['Manager'])

    def tearDownPloneSite(self, portal):
        self.applyProfile(portal, 'ploneintranet.suite:uninstall')

    def tearDownZope(self, app):
        # reset sync mode
        import ploneintranet.microblog.statuscontainer
        ploneintranet.microblog.statuscontainer.ASYNC = True
        # Uninstall product
        z2.uninstallProduct(app, 'ploneintranet.suite')
        z2.uninstallProduct(app, 'collective.indexing')
        z2.uninstallProduct(app, 'Products.membrane')


class PloneIntranetSuiteSolr(PloneIntranetSearchSolrLayer,
                             PloneIntranetSuite):
    """A solr-enabled suite layer with testcontent.
    We don't use PloneIntranetSearchSolrTestContentLayer since that does
    not load all our suite dependencies. Instead, we mixin PloneIntranetSuite.

    NOTE we don't support solr rollbacks so use solr read-only for now
    - which is why we don't purge after every test
    - we only purge when tearing down the layer

    Because this results in the absence of test isolation in solr, be
    very careful when adding solr based robot tests. All those tests
    should be strictly readonly, or you risk the write of one test
    causing a fail in an unrelated test, via solr pollution.
    """

    defaultBases = (
        SOLR_FIXTURE,
        PLONE_APP_CONTENTTYPES_FIXTURE,
        PLONE_APP_TILES_FIXTURE,
    )

    def setUpZope(self, app, configurationContext):
        # first activate solr
        PloneIntranetSearchSolrLayer.setUpZope(self, app, configurationContext)
        # then load the testcontent
        PloneIntranetSuite.setUpZope(self, app, configurationContext)

    def setUpPloneSite(self, portal):
        self.purge_solr()
        PloneIntranetSuite.setUpPloneSite(self, portal)

    def tearDownPloneSite(self, portal):
        # also uninstalls the suite
        PloneIntranetSuite.tearDownPloneSite(self, portal)
        self.purge_solr()

    def testTearDown(self):
        # Skip purging after every test
        pass


PLONEINTRANET_SUITE = PloneIntranetSuite()

PLONEINTRANET_SUITE_INTEGRATION = IntegrationTesting(
    bases=(PLONEINTRANET_SUITE, ),
    name="PLONEINTRANET_SUITE_INTEGRATION")

PLONEINTRANET_SUITE_FUNCTIONAL = FunctionalTesting(
    bases=(PLONEINTRANET_SUITE, ),
    name="PLONEINTRANET_SUITE_FUNCTIONAL")

# Having both non-solr and a solr layered robot tests
# breaks on premature z2 teardown.
# So now running all robot tests on solr enabled stack.
# NB: solr is not actually used outside search and library.

PLONEINTRANET_SUITE_ROBOT = FunctionalTesting(
    bases=(PLONEINTRANET_SUITE,
           AUTOLOGIN_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="PLONEINTRANET_SUITE_ROBOT")

PLONEINTRANET_SUITE_SOLR = PloneIntranetSuiteSolr()

PLONEINTRANET_SUITE_SOLR_ROBOT = FunctionalTesting(
    bases=(PLONEINTRANET_SUITE_SOLR,
           AUTOLOGIN_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="PLONEINTRANET_SUITE_SOLR_ROBOT")
