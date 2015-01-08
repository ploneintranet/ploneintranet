import unittest2 as unittest
from plonesocial.network.testing import PLONESOCIAL_NETWORK_INTEGRATION_TESTING
from plonesocial.network.likes import LikesContainer


class TestLikes(unittest.TestCase):

    #def setUp(self):
        #self.portal = self.layer['portal']

    def test_empty(self):
        container = LikesContainer()
        self.assertEqual(0, len(list(container.items())))

    def test_add_like(self):
        container = LikesContainer()
        container.add_like(
            'testperson@test.org', '827e65bd826a89790eba679e0c9ff864')
        likes = container._user_uuids_mapping['testperson@test.org']
        self.assertEqual(likes, ['827e65bd826a89790eba679e0c9ff864'])
