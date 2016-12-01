# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.userprofile.testing import PLONEINTRANET_USERPROFILE_FUNCTIONAL_TESTING  # noqa
from unittest import TestCase


class TestWorkgroupBase(TestCase):

    layer = PLONEINTRANET_USERPROFILE_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestWorkgroupBase, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # Create a groups folder and allow objects to be created there
        self.groups = api.content.create(
            self.portal,
            type='Folder',
            title='Groups',
        )
        pt = api.portal.get_tool('portal_types')
        pt['ploneintranet.userprofile.workgroup'].global_allow = True

        # create a test group
        self.group = api.content.create(
            container=self.groups,
            type='ploneintranet.userprofile.workgroup',
            canonical='Test group canonical name',
            title='Test group',
            description='',
            mail='testgroup@example.com',
        )

    def test_workgroup_is_a_group(self):
        ''' Basic test that checks that the workgroup is found as a group
        '''
        # Membrane is aware of it
        self.assertListEqual(
            [g._id for g in self.portal.acl_users.membrane_groups.getGroups()],
            ['Test group canonical name'],
        )
        # Also plone api (i.e. portal_groups.listGroups())
        self.assertIn(
            'Test group canonical name',
            [g.id for g in api.group.get_groups()]
        )
        # We can also get the group
        self.assertEqual(
            api.group.get('Test group canonical name').id,
            'Test group canonical name',
        )

    def test_workgroup_properties(self):
        ''' Test we can pick up the properties as expected
        '''
        group = api.group.get('Test group canonical name')
        self.assertEqual(
            group.getGroupTitleOrName(),
            'Test group'
        )
        self.assertEqual(group.getProperty('email'), self.group.mail)
        self.assertEqual(
            group.getProperty('description'),
            self.group.Description()
        )
        self.assertEqual(group.getProperty('title'), self.group.Title())
        self.assertEqual(group.getProperty('canonical'), self.group.canonical)
