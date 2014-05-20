import unittest2 as unittest


from ploneintranet.invitations.testing import \
    PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING


class TestExample(unittest.TestCase):

    layer = PLONEINTRANET_INVITATIONS_INTEGRATION_TESTING

    def setUp(self):
        # you'll want to use this to set up anything you need for your tests
        # below
        pass

    def test_success(self):
        sum = 1 + 3
        self.assertEqual(sum, 4)

