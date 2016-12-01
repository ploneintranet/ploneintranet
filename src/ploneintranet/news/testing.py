# -*- coding: utf-8 -*-
import unittest
from collective.mustread.testing import tempDb
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

from plone.testing import z2
from zope.configuration import xmlconfig


class PloneintranetNewsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.mustread
        self.loadZCML(package=collective.mustread)
        import ploneintranet.news
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.news,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.news:testing')


PLONEINTRANET_NEWS_FIXTURE = PloneintranetNewsLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEINTRANET_NEWS_FIXTURE,),
    name='PloneintranetNewsLayer:Integration'
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEINTRANET_NEWS_FIXTURE, z2.ZSERVER_FIXTURE),
    name='PloneintranetNewsLayer:Functional'
)


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.db = tempDb()  # auto teardown via __del__
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request'].clone()
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
