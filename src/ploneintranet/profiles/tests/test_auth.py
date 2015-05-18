from ploneintranet.profiles.testing import (
    PLONEINTRANET_PROFILES_INTEGRATION_TESTING
)
import unittest


class TestAuth(unittest.TestCase):

    layer = PLONEINTRANET_PROFILES_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST

    def test_user_login(self):
        self.fail()
