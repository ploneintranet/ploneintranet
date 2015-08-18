# coding=utf-8
from collective.workspace.interfaces import IWorkspace
from plone import api
from plone.tiles.interfaces import IBasicTile
from ploneintranet.workspace.browser.tiles.sidebar import Sidebar
from ploneintranet.workspace.browser.tiles.sidebar import \
    SidebarSettingsMembers
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent
from zope.publisher.browser import TestRequest


class TestSidebar(BaseTestCase):

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
        provideAdapter(
            SidebarSettingsMembers,
            (Interface, Interface),
            IBasicTile,
            name=u"sidebarSettingsMember.default",
        )

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

        provideAdapter(Sidebar, (Interface, Interface), IBasicTile,
                       name=u"sidebar.default")
        sidebar = getMultiAdapter((ws, ws.REQUEST), name=u"sidebar.default")
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

        subsidebar = getMultiAdapter((myfolder, myfolder.REQUEST),
                                     name=u"sidebar.default")
        subitems = subsidebar.items()
        ids = [x['id'] for x in subitems]
        self.assertIn('example-subdocument',
                      ids,
                      "No such IDs found in sidebar navigation")

        # Check if search works
        tr = TestRequest(form={'sidebar-search': 'Folder'})
        sidebar = getMultiAdapter((ws, tr), name=u"sidebar.default")
        items = sidebar.items()
        self.assertEqual(len(items), 1)
        self.assertTrue(items[0]['id'] == 'myfolder')

        # Assert that substr works and we find all
        tr = TestRequest(form={'sidebar-search': 'exampl'})
        sidebar = getMultiAdapter((ws, tr), name=u"sidebar.default")
        items = sidebar.items()
        self.assertEqual(len(items), 3)

        # Test Groupings

        # … by tag

        tr = TestRequest(form={'grouping': 'label'})
        sidebar = getMultiAdapter((ws, tr), name=u"sidebar.default")
        items = sidebar.items()
        self.assertEqual(len(items), 4)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['foo', 'bar', 'baz', 'untagged']))
        self.assertEqual(
            sidebar.logical_parent(), None)

        # …and step into tag 'bar'
        tr = TestRequest(form={'grouping': 'label', 'groupname': 'bar'})
        sidebar = getMultiAdapter((ws, tr), name=u"sidebar.default")
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
        tr = TestRequest(form={'grouping': 'type'})
        sidebar = getMultiAdapter((ws, tr), name=u"sidebar.default")
        items = sidebar.items()
        self.assertEqual(
            sidebar.logical_parent(), None)

        tr = TestRequest(form={'grouping': 'type', 'groupname': 'text/html'})
        sidebar = getMultiAdapter((ws, tr), name=u"sidebar.default")
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
        tr = TestRequest(form={'grouping': 'author'})
        sidebar = getMultiAdapter((ws, tr), name=u"sidebar.default")
        items = sidebar.items()
        self.assertEqual(
            sidebar.logical_parent(), None)

        # …and step into author admin
        tr = TestRequest(form={'grouping': 'author', 'groupname': 'admin'})
        sidebar = getMultiAdapter((ws, tr), name=u"sidebar.default")
        items = sidebar.items()
        self.assertEqual(len(items), 3)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['example-document', 'example-subdocument', 'myfolder']))

        self.assertEqual(
            sidebar.logical_parent()['title'],
            'All Authors')

        # … by date
        tr = TestRequest(form={'grouping': 'date'})
        sidebar = getMultiAdapter((ws, tr), name=u"sidebar.default")
        items = sidebar.items()
        self.assertEqual(len(items), 4)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['ever', 'month', 'today', 'week']))
        self.assertEqual(
            sidebar.logical_parent(), None)

        # …and step into date 'today'
        tr = TestRequest(form={'grouping': 'date', 'groupname': 'today'})
        sidebar = getMultiAdapter((ws, tr), name=u"sidebar.default")
        items = sidebar.items()
        self.assertEqual(len(items), 3)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['example-document', 'example-subdocument', 'myfolder']))

        self.assertEqual(
            sidebar.logical_parent()['title'],
            'All Dates')

        # … by first_letter
        tr = TestRequest(form={'grouping': 'first_letter'})
        sidebar = getMultiAdapter((ws, tr), name=u"sidebar.default")
        items = sidebar.items()
        self.assertEqual(len(items), 2)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['a', 's']))
        self.assertEqual(
            sidebar.logical_parent(), None)

        # …and step into letter 's'
        tr = TestRequest(form={'grouping': 'first_letter', 'groupname': 'a'})
        sidebar = getMultiAdapter((ws, tr), name=u"sidebar.default")
        items = sidebar.items()
        self.assertEqual(len(items), 2)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['example-subdocument', 'myfolder']))

        self.assertEqual(
            sidebar.logical_parent()['title'],
            'All Letters')

        # Yet unknown grouping, don't break!
        tr = TestRequest(form={'grouping': 'theunknown'})
        sidebar = getMultiAdapter((ws, tr), name=u"sidebar.default")
        items = sidebar.items()
        self.assertEqual(len(items), 1)
        self.assertEqual(
            sorted([k['id'] for k in items]),
            sorted(['none']))
