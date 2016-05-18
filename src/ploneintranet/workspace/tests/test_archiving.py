# -*- coding: utf-8 -*-
from datetime import datetime
from plone import api
from ploneintranet.workspace.tests.base import FunctionalBaseTestCase
from zope.component import getMultiAdapter


class TestArchiving(FunctionalBaseTestCase):
    """
    Workspaces and Case Workspaces can be archived.
    """

    def setUp(self):
        super(TestArchiving, self).setUp()
        self.catalog = api.portal.get_tool('portal_catalog')
        self.login_as_portal_owner()

        self.archived_workspace = api.content.create(
            self.portal.workspaces,
            'ploneintranet.workspace.workspacefolder',
            'archived-workspace',
            title='Archived Workspace',
            archival_date=datetime(2015, 12, 25),
        )
        self.unarchived_workspace = api.content.create(
            self.portal.workspaces,
            'ploneintranet.workspace.workspacefolder',
            'unarchived-workspace',
            title='Unarchived Workspace',
        )

    def test_archived_items_in_default_search_results(self):
        """
        Searches return both archived and unarchived items
        """
        request = self.portal.REQUEST
        request.form['SearchableText'] = 'Workspace'
        search_view = getMultiAdapter(
            (self.portal, request), name='search')
        search_results = list(search_view.search_response())
        result_titles = [i.title for i in search_results]
        self.assertTrue(
            'Archived Workspace' in result_titles,
            'Archived items are included in search results'
        )
        self.assertTrue(
            'Unarchived Workspace' in result_titles,
            "Unarchived items aren't included in search results"
        )
