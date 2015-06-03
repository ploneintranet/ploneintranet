from AccessControl import Unauthorized
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from ploneintranet.api.testing import FunctionalTestCase
from ploneintranet import api as pi_api
from ploneintranet.microblog.statusupdate import StatusUpdate


class TestStatusUpdate(FunctionalTestCase):

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_create(self):
        setRoles(self.portal, TEST_USER_ID, ('Member',))
        text = 'Hello this is my update'
        update = pi_api.microblog.statusupdate.create(text)
        self.assertIsInstance(update, StatusUpdate)
        self.assertEqual(update.text, text)

    def test_get(self):
        setRoles(self.portal, TEST_USER_ID, ('Member',))
        update = pi_api.microblog.statusupdate.create('Test')
        update2 = pi_api.microblog.statusupdate.create('Test2')
        self.assertEqual(
            pi_api.microblog.statusupdate.get(update.id),
            update)
        self.assertEqual(
            pi_api.microblog.statusupdate.get(update2.id),
            update2)
        self.assertRaises(
            Unauthorized,
            pi_api.microblog.statusupdate.get, 999999999)
