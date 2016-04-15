from json import loads
from plone import api
from ploneintranet import api as pi_api
from ploneintranet.workspace.testing import \
    PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING
from plone.testing import z2
from plone.app.testing.interfaces import SITE_OWNER_NAME

import unittest2 as unittest


class TestAllUsersAndGroupsWidgets(unittest.TestCase):

    layer = PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST
        super(TestAllUsersAndGroupsWidgets, self).setUp()
        self.view = self.portal.unrestrictedTraverse(
            'allusers-and-groups.json')

    def login_as_portal_owner(self):
        """
        helper method to login as site admin
        """
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)

    def test_groups_search(self):
        self.request.form['q'] = 'Administrators'
        results = loads(self.view())
        group_ids = [i['id'] for i in results]
        self.assertTrue('Administrators' in group_ids)
        self.assertTrue('Site Administrators' in group_ids)

    def test_users_search(self):
        self.login_as_portal_owner()
        pi_api.userprofile.create(
            username='johndoe',
            email='johndoe@doe.com',
        )
        self.request.form['q'] = 'john'
        results = loads(self.view())
        user_ids = [i['id'] for i in results]
        self.assertTrue('johndoe' in user_ids)
        self.assertEqual(len(results), 1)

    def test_workspace_prefill(self):
        self.login_as_portal_owner()
        pi_api.userprofile.create(username='johndoe', email='johndoe@doe.com')
        ws = api.content.create(
            container=self.portal.workspaces,
            id='ws',
            type='ploneintranet.workspace.workspacefolder',
        )
        event = api.content.create(
            container=ws,
            id='event',
            type='Event',
            invitees='Administrators,johndoe,nobody',
        )
        prefill = ws.member_and_group_prefill(event, 'invitees')
        self.assertEqual(
            prefill,
            '{"Administrators": "Administrators", "johndoe": "johndoe"}'
        )
