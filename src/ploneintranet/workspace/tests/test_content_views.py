# -*- coding: utf-8 -*-

"""Move to ploneintranet.theme asap
"""

from plone import api
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from plone.app.textfield.value import RichTextValue
from ploneintranet.theme.interfaces import IThemeSpecific
from ploneintranet.layout.interfaces import IPloneintranetLayoutLayer
from ploneintranet.layout.interfaces import IPloneintranetContentLayer
from ploneintranet.workspace.interfaces import IWorkspaceAppContentLayer
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.interface import alsoProvides

import os


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
