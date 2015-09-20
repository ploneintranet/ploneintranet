from Products.PlonePAS.events import UserLoggedInEvent
from datetime import datetime
from plone import api
from plone.app.testing import login
from ploneintranet.userprofile.tests.base import BaseTestCase
from ploneintranet.userprofile.tests.test_sync import (
    install_mock_properties_plugin
)
from zope import event


class TestSubscribers(BaseTestCase):

    def test_new_user(self):
        self.login_as_portal_owner()
        install_mock_properties_plugin()

        username = 'adam'
        member = api.user.create(
            email="test@test.com",
            username=username,
        )
        login(self.portal, username)
        event.notify(UserLoggedInEvent(member))
        brains = api.portal.get_tool('membrane_tool').searchResults()
        self.assertEqual(len(brains), 1)
        self.assertIsInstance(brains[0].getObject().last_sync, datetime)
