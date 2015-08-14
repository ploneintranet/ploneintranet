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

    def test_workspace_groups_hidden(self):
        """ collective.workspace groups should be hidden when enumerating """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace')
        groupname = 'Members:%s' % workspace_folder.UID()
        self.assertIsNotNone(
            api.group.get(groupname=groupname)
        )
        # Use pas search to mimic the control panel groups views
        pas_search = api.content.get_view('pas_search',
                                          self.portal, self.request)
        group_info = pas_search.searchGroups()
        self.assertNotIn(
            groupname,
            [x['id'] for x in group_info],
        )

    def test_placeful_workflow_policy(self):
        """ globally addable types should be configured to use the default
            chain in the ploneintranet policy """

        pwftool = api.portal.get_tool('portal_placeful_workflow')
        policy = pwftool['ploneintranet_policy']
        default_chain = policy.getDefaultChain(None)

        default_types = [
            'Collection',
            'Document',
            'Event',
            'File',
            'Image',
            'Link',
            'News Item',
        ]
        for portal_type in default_types:
            self.assertEqual(
                default_chain,
                policy.getChainFor(portal_type)
            )
