# coding=utf-8
from collective.workspace.interfaces import IWorkspace
from plone import api
from ploneintranet.workspace.interfaces import IGroupingStorage
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.annotation import IAnnotations
from zope.component import getAdapter
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

    def create_workspace(self, ws_id='example-workspace'):
        """ returns adapted workspace folder"""
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            ws_id,
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
        # item was modified, therefore the id was created from the title
        self.assertEquals(
            example_document.getId(),
            'some-example-rich-text')

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
        # item was modified, therefore the id was created from the title
        self.assertEquals(
            example_subdocument.getId(),
            'another-example-nested-rich-text')

        sidebar = self.get_sidebar_default(ws)
        items = sidebar.items()

        titles = [x['title'] for x in items]
        self.assertIn('Some example Rich Text',
                      titles,
                      "File with that title not found in sidebar navigation")

        urls = [x['url'] for x in items]

        expected_url = (
            'http://nohost/plone/workspace-container/'
            'example-workspace/myfolder/@@sidebar.documents'
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
        self.assertNotIn('another-example-nested-rich-text',
                         ids,
                         "No such IDs found in sidebar navigation")

        subsidebar = self.get_sidebar_default(myfolder)

        subitems = subsidebar.items()
        ids = [x['id'] for x in subitems]
        self.assertIn('another-example-nested-rich-text',
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
            sorted(['some-example-rich-text', 'another-example-nested-rich-text']))  # noqa
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
            sorted(['some-example-rich-text', 'another-example-nested-rich-text']))  # noqa

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
        # we are grouping by author, folders are excluded
        items = sidebar.items()
        self.assertEqual(len(items), 2)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['some-example-rich-text', 'another-example-nested-rich-text']))  # noqa

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

        # we are grouping by date, folders are excluded
        items = sidebar.items()
        self.assertEqual(len(items), 2)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['some-example-rich-text', 'another-example-nested-rich-text']))  # noqa

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
        self.assertEqual(len(items), 1)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['another-example-nested-rich-text']))

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

    def test_sidebar_update_relations(self):
        # Prepare the test
        ws1 = self.create_workspace()
        ws2 = self.create_workspace(ws_id='ws2')
        ws3 = self.create_workspace(ws_id='ws3')
        sidebar1 = api.content.get_view(
            'sidebar.settings.advanced', ws1, self.request.clone()
        )
        sidebar2 = api.content.get_view(
            'sidebar.settings.advanced', ws2, self.request.clone()
        )
        sidebar3 = api.content.get_view(
            'sidebar.settings.advanced', ws3, self.request.clone()
        )
        # Adding fake stuff will not break the method
        sidebar1.update_relation_targets(['foo'])

        # We now create a relation on ws1 and want the sidebar to update also
        # the relation target
        ws1.related_workspaces = [ws2.UID()]
        sidebar1.update_relation_targets([])
        self.assertListEqual(
            ws2.related_workspaces,
            [ws1.UID()]
        )
        # We add another relation
        ws3.related_workspaces = [ws2.UID()]
        sidebar3.update_relation_targets([])
        self.assertListEqual(
            ws2.related_workspaces,
            [ws1.UID(), ws3.UID()]
        )
        # We now remove both the relation from the target
        ws2.related_workspaces = []
        sidebar2.update_relation_targets([ws1.UID(), ws3.UID()])
        self.assertListEqual(ws1.related_workspaces, [])
        self.assertListEqual(ws2.related_workspaces, [])
        self.assertListEqual(ws3.related_workspaces, [])

    def test_sidebar_archived_items(self):
        ''' Check if the sidebar is showing/hiding updated items properly
        '''
        self.login_as_portal_owner()
        ws = self.create_workspace()
        doc = api.content.create(
            ws,
            'Document',
            title='Archivable Document'
        )
        sidebar = api.content.get_view(
            'sidebar.documents',
            ws, self.request.clone()
        )
        self.assertIn(
            '<strong class="title"> Archivable Document </strong>',
            ' '.join(sidebar().split()),
        )
        IAnnotations(doc)['slc.outdated'] = True
        doc.reindexObject(idxs=['outdated'])

        # Clean memoize.view cache
        sidebar.request = self.request.clone()
        self.assertNotIn('Archivable Document', sidebar())

        # Clean memoize.view cache
        sidebar.request = self.request.clone()
        sidebar.request.set('documents-show-extra-admin', 'archived_documents')
        self.assertIn('Archivable Document', sidebar())
        self.assertIn(
            '<strong class="title"> Archivable Document '
            '<abbr class="iconified icon-archive">(Archived)</abbr> </strong>',
            ' '.join(sidebar().split()),
        )

    def test_sidebar_archived_tags(self):
        ''' Check if the sidebar is showing/hiding archived tags properly
        '''
        self.login_as_portal_owner()
        ws = self.create_workspace()
        doc = api.content.create(
            ws,
            'Document',
            title='Tagged Document'
        )
        doc.subject = ['Test Tag']
        storage = getAdapter(ws, IGroupingStorage)
        storage.update_groupings(doc)
        request = self.request.clone()
        request.form['grouping'] = 'label'
        sidebar = api.content.get_view(
            'sidebar.documents',
            ws, request
        )
        self.assertIn(
            '<strong class="title"> Test Tag </strong>',
            ' '.join(sidebar().split()),
        )
        storage.get_groupings().get('label').get('Test Tag').archived = True

        # Clean memoize.view cache
        sidebar.request = self.request.clone()
        sidebar.request.form['grouping'] = 'label'
        self.assertNotIn('Test Tag', sidebar())

        # Clean memoize.view cache
        sidebar.request = self.request.clone()
        sidebar.request.form['grouping'] = 'label'
        sidebar.request.set('documents-show-extra-admin', 'archived_tags')
        self.assertIn('Test Tag', sidebar())
        self.assertIn(
            '<strong class="title"> Test Tag </strong> '
            '<dfn class="byline"><em>(Archived)</em></dfn>',
            ' '.join(sidebar().split()),
        )
