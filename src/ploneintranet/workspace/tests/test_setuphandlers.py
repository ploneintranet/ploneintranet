from ploneintranet.workspace.tests.base import BaseTestCase
from ploneintranet.workspace.config import INTRANET_USERS_GROUP_ID
from plone import api


class TestSetupHandlers(BaseTestCase):

    """ Check that the setuphandlers code sets the site up correctly """

    def test_groups_setup(self):
        """ Check that the dynamic group to hold all intranet users
            is set up correctly """
        group = api.group.get(groupname=INTRANET_USERS_GROUP_ID)
        self.assertIsNotNone(group, "Group not created properly")

        api.user.create(username='testuser',
                        email='testuser@plone.com')

        # new users should be added to it
        user_group_ids = [x.getId() for x
                          in api.group.get_groups(username='testuser')]
        self.assertIn(INTRANET_USERS_GROUP_ID,
                      user_group_ids)

        # should have 'reader' on the portal
        group_roles = api.group.get_roles(groupname=INTRANET_USERS_GROUP_ID,
                                          obj=self.portal)
        self.assertIn('Reader', group_roles)

        # as should our test user
        user_roles = api.user.get_roles(username='testuser',
                                        obj=self.portal)
        self.assertIn('Reader', user_roles)
