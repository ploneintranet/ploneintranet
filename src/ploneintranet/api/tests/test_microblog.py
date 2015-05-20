from ploneintranet.api.testing import IntegrationTestCase
from ploneintranet import api as pi_api
from ploneintranet.microblog.statusupdate import StatusUpdate


class TestMicroblog(IntegrationTestCase):

    def test_create_statusupdate(self):
        text = 'Hello this is my update'
        update = pi_api.microblog.create_statusupdate(text)
        self.assertIsInstance(update, StatusUpdate)
        self.assertEqual(update.text, text)

    def test_get_statusupdate(self):
        update = pi_api.microblog.create_statusupdate('Test')
        update2 = pi_api.microblog.create_statusupdate('Test2')
        self.assertEqual(
            pi_api.microblog.get_statusupdate(update.id),
            update)
        self.assertEqual(
            pi_api.microblog.get_statusupdate(update2.id),
            update2)
        self.assertIsNone(
            pi_api.microblog.get_statusupdate(999999999)
        )
