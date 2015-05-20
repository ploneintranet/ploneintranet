from ploneintranet.api.testing import IntegrationTestCase
from ploneintranet import api as pi_api
from ploneintranet.microblog.statusupdate import StatusUpdate


class TestStatusUpdate(IntegrationTestCase):

    def test_create(self):
        text = 'Hello this is my update'
        update = pi_api.microblog.statusupdate.create(text)
        self.assertIsInstance(update, StatusUpdate)
        self.assertEqual(update.text, text)

    def test_get(self):
        update = pi_api.microblog.statusupdate.create('Test')
        update2 = pi_api.microblog.statusupdate.create('Test2')
        self.assertEqual(
            pi_api.microblog.statusupdate.get(update.id),
            update)
        self.assertEqual(
            pi_api.microblog.statusupdate.get(update2.id),
            update2)
        self.assertIsNone(
            pi_api.microblog.statusupdate.get(999999999)
        )
