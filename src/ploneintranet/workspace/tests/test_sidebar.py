# coding=utf-8
from collective.workspace.interfaces import IWorkspace
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestSidebar(BaseTestCase):

    def get_sidebar_default(self, context, params={}):
        ''' Returns the sidebar default tile on the context
        with the given parameters
        '''
        request = self.request.clone()
        request.form.update(params)
        return api.content.get_view('sidebar.default', context, request)

    def create_workspace(self):
        """ returns adapted workspace folder"""
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace'
        )
        return workspace_folder
        # return IWorkspace(workspace_folder)

    def test_sidebar_existing_users(self):

        ws = self.create_workspace()
        user = api.user.create(email="newuser@example.org", username="newuser")
        user_id = user.getId()

        self.assertNotIn(user_id, IWorkspace(ws).members, "Id already present")

        IWorkspace(ws).add_to_team(user=user_id)

        # Commenting out because they aren't (yet?) being used.
        # sidebarSettingsMembers = getMultiAdapter(
        #     (ws, ws.REQUEST), name=u"sidebarSettingsMember.default")
        # existing_users = sidebarSettingsMembers.existing_users()

        self.assertIn(
            user_id,
            IWorkspace(ws).members,
            "Id not found in worskpace member Ids",
        )

    def test_sidebar_items(self):
        """ Create some test content and test if items method works
        """
        self.login_as_portal_owner()
        ws = self.create_workspace()
        api.content.create(
            ws,
            'Document',
            'example-document',
            title='Some example Rich Text'
        )
        example_document = getattr(ws, 'example-document')
        example_document.setSubject((u'foo', u'bar'))
        notify(ObjectModifiedEvent(example_document))

        api.content.create(
            ws,
            'Folder',
            'myfolder',
            title='An example Folder'
        )
        myfolder = getattr(ws, 'myfolder')
        api.content.create(
            myfolder,
            'Document',
            'example-subdocument',
            title='Another example nested Rich Text'
        )
        example_subdocument = getattr(myfolder, 'example-subdocument')
        example_subdocument.setSubject((u'bar', u'baz'))
        notify(ObjectModifiedEvent(example_subdocument))

        sidebar = self.get_sidebar_default(ws)
        items = sidebar.items()

        titles = [x['title'] for x in items]
        self.assertIn('Some example Rich Text',
                      titles,
                      "File with that title not found in sidebar navigation")

        urls = [x['url'] for x in items]

        expected_url = (
            'http://nohost/plone/workspace-container/'
            'example-workspace/myfolder'
        )
        self.assertIn(
            expected_url,
            urls,
            "Folder with that url not found in sidebar navigation"
        )
        dpis = [x['dpi'] for x in items]
        self.assertIn(
            "source: #workspace-documents; target: #workspace-documents",
            dpis[0],
            "inject with that url not found in sidebar navigation")
        classes = [x['cls'] for x in items]
        self.assertIn('item group type-folder has-no-description',
                      classes,
                      "No such Classes found in sidebar navigation")
        ids = [x['id'] for x in items]
        self.assertNotIn('example-subdocument',
                         ids,
                         "No such IDs found in sidebar navigation")

        subsidebar = self.get_sidebar_default(myfolder)

        subitems = subsidebar.items()
        ids = [x['id'] for x in subitems]
        self.assertIn('example-subdocument',
                      ids,
                      "No such IDs found in sidebar navigation")

        # Check if search works
        sidebar = self.get_sidebar_default(ws, {'sidebar-search': 'Folder'})

        items = sidebar.items()
        self.assertEqual(len(items), 1)
        self.assertTrue(items[0]['id'] == 'myfolder')

        # Assert that substr works and we find all
        sidebar = self.get_sidebar_default(ws, {'sidebar-search': 'exampl'})
        items = sidebar.items()
        self.assertEqual(len(items), 3)

        # Test Groupings

        # … by tag
        sidebar = self.get_sidebar_default(ws, {'grouping': 'label'})
        items = sidebar.items()
        self.assertEqual(len(items), 4)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['foo', 'bar', 'baz', 'untagged']))
        self.assertEqual(
            sidebar.logical_parent(), None)

        # …and step into tag 'bar'
        sidebar = self.get_sidebar_default(
            ws,
            {'grouping': 'label', 'groupname': 'bar'},
        )
        items = sidebar.items()
        self.assertEqual(len(items), 2)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['example-document', 'example-subdocument']))
        self.assertEqual(
            sidebar.logical_parent()['title'],
            'All Tags')

        # … by type
        # XXX
        sidebar = self.get_sidebar_default(ws, {'grouping': 'type'})
        items = sidebar.items()
        self.assertEqual(
            sidebar.logical_parent(), None)

        sidebar = self.get_sidebar_default(
            ws,
            {'grouping': 'type', 'groupname': 'text/html'},
        )
        items = sidebar.items()
        self.assertEqual(len(items), 2)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['example-document', 'example-subdocument']))

        # …and step into type 'text/html'
        self.assertEqual(
            sidebar.logical_parent()['title'],
            'All Types')

        # … by author
        # XXX
        sidebar = self.get_sidebar_default(ws, {'grouping': 'author'})
        items = sidebar.items()
        self.assertEqual(
            sidebar.logical_parent(), None)

        # …and step into author admin
        sidebar = self.get_sidebar_default(
            ws,
            {'grouping': 'author', 'groupname': 'admin'},
        )
        items = sidebar.items()
        self.assertEqual(len(items), 3)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['example-document', 'example-subdocument', 'myfolder']))

        self.assertEqual(
            sidebar.logical_parent()['title'],
            'All Authors')

        # … by date
        sidebar = self.get_sidebar_default(ws, {'grouping': 'date'})
        items = sidebar.items()
        self.assertEqual(len(items), 4)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['ever', 'month', 'today', 'week']))
        self.assertEqual(
            sidebar.logical_parent(), None)

        # …and step into date 'today'
        sidebar = self.get_sidebar_default(
            ws,
            {'grouping': 'date', 'groupname': 'today'},
        )
        items = sidebar.items()
        self.assertEqual(len(items), 3)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['example-document', 'example-subdocument', 'myfolder']))

        self.assertEqual(
            sidebar.logical_parent()['title'],
            'All Dates')

        # … by first_letter
        sidebar = self.get_sidebar_default(ws, {'grouping': 'first_letter'})
        items = sidebar.items()
        self.assertEqual(len(items), 2)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['a', 's']))
        self.assertEqual(
            sidebar.logical_parent(), None)

        # …and step into letter 's'
        sidebar = self.get_sidebar_default(
            ws,
            {'grouping': 'first_letter', 'groupname': 'a'},
        )
        items = sidebar.items()
        self.assertEqual(len(items), 2)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['example-subdocument', 'myfolder']))

        self.assertEqual(
            sidebar.logical_parent()['title'],
            'All Letters')

        # Yet unknown grouping, don't break!
        sidebar = self.get_sidebar_default(ws, {'grouping': 'theunknown'})
        items = sidebar.items()
        self.assertEqual(len(items), 1)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['none']))
