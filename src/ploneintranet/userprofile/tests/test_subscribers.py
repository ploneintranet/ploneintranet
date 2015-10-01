from Products.PlonePAS.events import UserLoggedInEvent
from datetime import datetime
from plone import api
from plone.app.testing import login
from ploneintranet.userprofile.tests.base import BaseTestCase
from ploneintranet.userprofile.tests.test_sync import (
    install_mock_pas_plugin,
)
from zope import event


class TestSubscribers(BaseTestCase):

    def setUp(self):
        super(TestSubscribers, self).setUp()
        self.login_as_portal_owner()
        install_mock_pas_plugin()

    def test_new_user(self):
        username = 'adam'
        member = api.user.create(email='test@test.com', username=username)
        login(self.portal, username)
        event.notify(UserLoggedInEvent(member))
        brains = api.portal.get_tool('membrane_tool').searchResults()
        self.assertEqual(len(brains), 1)
        obj = brains[0].getObject()
        self.assertIsInstance(getattr(obj, 'last_sync', None), datetime)
