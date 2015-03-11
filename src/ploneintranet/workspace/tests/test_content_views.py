# -*- coding: utf-8 -*-

"""Move to ploneintranet.theme asap
"""

from plone import api
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from plone.app.textfield.value import RichTextValue
from ploneintranet.theme.interfaces import IThemeSpecific
from ploneintranet.theme.interfaces import IIntranetContentLayer
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.interface import alsoProvides


class TestAddContent(BaseTestCase):

    def setUp(self):
        super(TestAddContent, self).setUp()
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        self.workspace = workspace_folder
        self.request = self.layer['request']
        alsoProvides(self.request, IThemeSpecific)
        alsoProvides(self.request, IIntranetContentLayer)
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
        self.assertIn('ploneintranet.theme.browser.content.ContentView',
                      str(view.__class__.__mro__))
        html = view()
        self.assertIn(u'My Døcümént', html)
        self.assertIn(u'<strong class="title">%s</a>' % doc1.title, html)
