import unittest
from plone.app.testing import SITE_OWNER_NAME
from plone.testing import z2
from ploneintranet.simplesharing.testing import \
    PLONEINTRANET_SIMPLESHARING_INTEGRATION_TESTING


class BaseTestCase(unittest.TestCase):

    layer = PLONEINTRANET_SIMPLESHARING_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST

    def login_as_portal_owner(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)
