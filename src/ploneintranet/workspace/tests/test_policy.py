from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase


class TestPolicy(BaseTestCase):

    def test_groups_created(self):
        """
        When a workspace is created it should also create a number of groups
        which correlate to the various policies on a workspace:
        - Consumer
        - Producer
        - Publisher
        - Moderator
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'workspace')
        workspace_folder_uid = api.content.get_uuid(workspace_folder)

        self.assertIsNotNone(
            api.group.get('Consumers:%s' % workspace_folder_uid))
        self.assertIsNotNone(
            api.group.get('Producers:%s' % workspace_folder_uid))
        self.assertIsNotNone(
            api.group.get('Publishers:%s' % workspace_folder_uid))
        self.assertIsNotNone(
            api.group.get('Moderators:%s' % workspace_folder_uid))
