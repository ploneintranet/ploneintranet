from ploneintranet.workspace.tests.base import BaseTestCase
from ploneintranet.workspace.config import INTRANET_USERS_GROUP_ID
from plone import api


class TestSubscribers(BaseTestCase):

    def test_workspace_state_changed(self):
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
        roles = api.group.get_roles(
            groupname=INTRANET_USERS_GROUP_ID,
            obj=workspace_folder,
        )
        self.assertNotIn('Guest', roles)

        # Transition to open should add the role
        api.content.transition(obj=workspace_folder,
                               to_state='open')
        roles = api.group.get_roles(
            groupname=INTRANET_USERS_GROUP_ID,
            obj=workspace_folder,
        )
        self.assertIn('Guest', roles)

        # Transition to another state should remove it
        api.content.transition(obj=workspace_folder,
                               to_state='private')
        roles = api.group.get_roles(
            groupname=INTRANET_USERS_GROUP_ID,
            obj=workspace_folder,
        )
        self.assertNotIn('Guest', roles)
