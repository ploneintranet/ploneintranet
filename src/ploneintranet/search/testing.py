# -*- coding: utf-8 -*-
"""Base module for unittesting ploneintranet.search."""
from contextlib import contextmanager

import transaction
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app import testing
from plone import api
import unittest2 as unittest
import ploneintranet.search
import ploneintranet.docconv.client
from ploneintranet.testing import PLONEINTRANET_FIXTURE


TEST_USER_1_NAME = 'icarus'

TEST_USER_1_EMAIL = 'icarus@ploneintranet.org'


@contextmanager
def login_session(username):
    """Temporarily login as another user.

    Re-logging-in the previous user after exiting the context.
    """
    portal = api.portal.get()
    prev_login = None
    try:
        if not api.user.is_anonymous():
            prev_login = api.user.get_current().getUserName()
        testing.logout()
        testing.login(portal, username)
        yield username
    finally:
        testing.logout()
        if prev_login:
            testing.login(portal, prev_login)


class PloneintranetSearchLayer(testing.PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,
                    PLONEINTRANET_FIXTURE)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=ploneintranet.search)
        self.loadZCML(package=ploneintranet.docconv.client)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'ploneintranet.docconv.client:default')
        self.applyProfile(portal, 'ploneintranet.search:default')
        with login_session(testing.TEST_USER_NAME):
            api.user.create(username=TEST_USER_1_NAME, email=TEST_USER_1_EMAIL)

    def tearDownPloneSite(self, portal):
        with api.env.adopt_roles(roles=['Manager']):
            api.user.delete(username=TEST_USER_1_NAME)
        super(PloneintranetSearchLayer, self).tearDownPloneSite(portal)


FIXTURE = PloneintranetSearchLayer()
INTEGRATION_TESTING = testing.IntegrationTesting(
    bases=(FIXTURE,), name="PloneintranetSearchLayer:Integration")
FUNCTIONAL_TESTING = testing.FunctionalTesting(
    bases=(FIXTURE,), name="PloneintranetSearchLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING

    def _create_content(self, **kw):
        obj = api.content.create(**kw)
        obj.reindexObject()
        self._created.append(obj)
        return obj

    def _delete_content(self, obj):
        api.content.delete(obj=obj)

    def setUp(self):
        self._created = []
        super(IntegrationTestCase, self).setUp()

    def tearDown(self):
        super(IntegrationTestCase, self).tearDown()
        for obj in self._created:
            obj_id = obj.getId()
            if obj_id in self.layer['portal']:
                with api.env.adopt_roles(roles=['Manager']):
                    self._delete_content(obj)
            transaction.commit()


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
