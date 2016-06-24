# -*- coding: utf-8 -*-

"""Move to ploneintranet.theme asap
"""

from plone import api
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from plone.app.contenttypes.behaviors.richtext import IRichText
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.app.textfield.value import RichTextValue
from ploneintranet.theme.interfaces import IThemeSpecific
from ploneintranet.layout.interfaces import IPloneintranetLayoutLayer
from ploneintranet.layout.interfaces import IPloneintranetContentLayer
from ploneintranet.todo.behaviors import ITodo
from ploneintranet.workspace.basecontent.baseviews import ContentView
from ploneintranet.workspace.basecontent.utils import dexterity_update
from ploneintranet.workspace.interfaces import IWorkspaceAppContentLayer
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.component import getSiteManager
from zope.interface import alsoProvides
from zope.lifecycleevent.interfaces import IAttributes
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

import os

html_input = u"""Intro of Plone Intranet
<h1>Overview</h1>
<p><span class="random">Quaive</span> is über-cool.
<ul>
<li>Red</li>
<li>Yellow
<li>Green</li>
</ul>
<blockquote>It's the awesomest thing.</blockquote>
<strong>Get your copy today!</strong>
"""

# All tags are properly closed. All text is properly wrapped.
# Unwanted tags get removed.
html_cleaned = u"""<p>Intro of Plone Intranet</p>
<h1>Overview</h1>
<p>Quaive is über-cool.</p>
<ul>
<li>Red</li>
<li>Yellow</li>
<li>Green</li>
</ul>
<p>It's the awesomest thing.
<strong>Get your copy today!</strong></p>"""


def test_image():
    from plone.namedfile.file import NamedBlobImage
    filename = os.path.join(os.path.dirname(__file__), u'plone_logo.png')
    return NamedBlobImage(
        data=open(filename, 'r').read(),
        filename=filename,
    )


class TestContentViews(BaseTestCase):

    def setUp(self):
        super(TestContentViews, self).setUp()
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        self.workspace = workspace_folder
        self.request = self.layer['request']
        alsoProvides(self.request, IThemeSpecific)
        alsoProvides(self.request, IPloneintranetLayoutLayer)
        alsoProvides(self.request, IPloneintranetContentLayer)
        alsoProvides(self.request, IWorkspaceAppContentLayer)
        alsoProvides(self.request, IPloneAppContenttypesLayer)

    def test_document_view(self):
        doc1 = api.content.create(
            container=self.workspace,
            type='Document',
            title=u'My Døcümént',
        )
        doc1.description = u'Déscription'
        raw_text = u"<p>iuhdiuahsd</p>"
        mime_type = 'text/plain'
        richtext = RichTextValue(raw=raw_text, mimeType=mime_type,
                                 outputMimeType='text/x-html-safe')
        doc1.text = richtext
        view = doc1.restrictedTraverse('document_view')
        self.assertIn('document_view.pt', view.index.filename)
        html = view()
        self.assertIn(u'My Døcümént', html)
        self.assertIn(u'<article class="document rich">', html)

    def test_image_view(self):
        img1 = api.content.create(
            container=self.workspace,
            type='Image',
            title=u'My îmage',
        )
        img1.description = u'Déscription'
        # image test commented out for now, enable when
        # img1.image = test_image()
        view = img1.restrictedTraverse('image_view')
        self.assertIn('document_view.pt', view.index.filename)
        html = view()
        self.assertIn(u'My îmage', html)
        self.assertIn(u'<article class="document preview">', html)
        self.assertIn(u'<figure>', html)
        # self.assertIn(
        #     u'<img src="http://nohost/plone/example-workspace/my-image/@@images',  # NOQA
        #     html
        # )

    def test_file_view(self):
        file1 = api.content.create(
            container=self.workspace,
            type='File',
            title=u'My Fîle',
        )
        file1.description = u'Déscription'
        view = file1.restrictedTraverse('file_view')
        self.assertIn('document_view.pt', view.index.filename)
        html = view()
        self.assertIn(u'My Fîle', html)


class TestDexterityUpdate(BaseTestCase):

    def setUp(self):
        super(TestDexterityUpdate, self).setUp()
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        self.workspace = workspace_folder
        self.todo1 = api.content.create(
            container=self.workspace,
            type='todo',
            title=u'Todo1',
        )
        self.doc1 = api.content.create(
            container=self.workspace,
            type='Document',
            title=u'My Døcümént',
        )
        self.request = self.layer['request']

    def test_not_modified(self):
        modified, errors = dexterity_update(self.todo1)
        self.assertEqual(errors, [])
        self.assertFalse(modified)

    def test_description_modified(self):
        self.todo1.REQUEST.form = {'description': 'test'}
        modified, errors = dexterity_update(self.todo1)
        self.assertEqual(errors, [])
        self.assertEqual(modified, {IBasic: ['description']})

    def test_multiple_fields_modified(self):
        self.todo1.REQUEST.form = {
            'title': 'Todo 2000',
            'description': 'test',
            'due': '2015-10-24',
        }
        modified, errors = dexterity_update(self.todo1)
        self.assertEqual(errors, [])
        self.assertEqual(modified, {
            IBasic: ['description', 'title', ],
            ITodo: ['due', ],
        })

    def test_sanitize_in_action(self):
        self.doc1.REQUEST.form = {
            'text': html_input
        }
        modified, errors = dexterity_update(self.doc1)
        self.assertEqual(errors, [])
        self.assertEqual(modified, {IRichText: ['text']})
        # Ignore differences in line breaks, only the semantics matter.
        self.assertEqual(
            self.doc1.text.raw.replace('\n', ''),
            html_cleaned.replace('\n', ''))

    def test_sanitize_can_be_switched_off(self):
        api.portal.set_registry_record(
            'ploneintranet.workspace.sanitize_html', False)
        self.doc1.REQUEST.form = {
            'text': html_input
        }
        modified, errors = dexterity_update(self.doc1)
        self.assertEqual(errors, [])
        self.assertEqual(modified, {IRichText: ['text']})
        self.assertEqual(self.doc1.text.raw, html_input)


class TestContentViewUpdate(BaseTestCase):

    def setUp(self):
        super(TestContentViewUpdate, self).setUp()
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        self.workspace = workspace_folder
        self.todo1 = api.content.create(
            container=self.workspace,
            type='todo',
            title=u'Todo1',
        )
        self.request = self.layer['request']

        def catch_event(obj, event):
            self.event = event

        self.event = None
        self.catch_event = catch_event
        sm = getSiteManager()
        sm.registerHandler(self.catch_event, [ITodo, IObjectModifiedEvent])

    def tearDown(self):
        sm = getSiteManager()
        sm.unregisterHandler(self.catch_event, [ITodo, IObjectModifiedEvent])

    def test_event_thrown_on_field_change(self):
        self.request.form = {'description': 'test'}
        view = ContentView(self.todo1, self.request)
        view.can_edit = True
        view.update()
        self.assertTrue(IObjectModifiedEvent.providedBy(self.event))

    def test_no_event_thrown_on_workflow_change(self):
        self.request.form = {'workflow_action': 'finish'}
        view = ContentView(self.todo1, self.request)
        view.can_edit = True
        view.update()
        self.assertTrue(self.event is None)

    def test_event_descriptions(self):
        self.request.form = {'description': 'test'}
        view = ContentView(self.todo1, self.request)
        view.can_edit = True
        view.update()
        self.assertTrue(IObjectModifiedEvent.providedBy(self.event))
        self.assertTrue(IAttributes.providedBy(self.event.descriptions[0]))
        self.assertEqual(self.event.descriptions[0].interface,
                         IBasic)
        self.assertEqual(self.event.descriptions[0].attributes,
                         ('description',))

    def test_multiple_event_descriptions(self):
        self.request.form = {
            'title': 'Todo 2000',
            'description': 'test',
            'due': '2015-10-24',
        }
        view = ContentView(self.todo1, self.request)
        view.can_edit = True
        view.update()
        self.assertTrue(IObjectModifiedEvent.providedBy(self.event))
        self.assertTrue(IAttributes.providedBy(self.event.descriptions[0]))
        self.assertTrue(IAttributes.providedBy(self.event.descriptions[1]))
        descs = dict([(d.interface, d.attributes)
                      for d in self.event.descriptions])
        self.assertEqual(descs[IBasic], ('description', 'title'))
        self.assertEqual(descs[ITodo], ('due', ))
