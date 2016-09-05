# -*- coding: utf-8 -*-
"""A Cart Action for downloading all items listed in cart as a ZIP file."""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from StringIO import StringIO
from datetime import datetime
from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.docconv.client import HTML_CONTENTTYPES
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView

import zipfile


class DownloadView(BaseCartView):
    """Download Action implementation for downloading items listed in cart."""

    def confirm(self):
        index = ViewPageTemplateFile("templates/download_confirmation.pt")
        return index(self)

    def downloadable_items(self):
        files = []
        pdfs = []
        images = []
        no_pdfs = []
        folders = []
        for obj in self.items:
            # make sure obj is a file by checking if filename is set
            file_obj = getattr(obj, 'file', None)
            if file_obj:
                filename = file_obj.filename
                if filename:
                    files.append(obj)
            elif getattr(obj, 'image', None):
                images.append(obj)
            elif obj.portal_type in HTML_CONTENTTYPES:
                pdf = obj.restrictedTraverse('pdf')
                if pdf.has_pdf():
                    pdfs.append(obj)
                else:
                    no_pdfs.append(obj)
            elif obj.portal_type == 'Folder':
                folders.append(obj)
        return {
            'files': files,
            'pdfs': pdfs,
            'images': images,
            'no_pdfs': no_pdfs,
            'folders': folders
        }

    def download(self):
        """Download cart content.

        Before downloading items are packed into a zip archive (only the
        items that are files are included).

        """
        output = StringIO()
        zf = zipfile.ZipFile(output, mode='w')

        downloadable_items = self.downloadable_items()
        try:
            for obj in downloadable_items['files']:
                zf.writestr(obj.file.filename, obj.file.data)
            for obj in downloadable_items['images']:
                zf.writestr(obj.image.filename, obj.image.data)
            for pdf_obj in downloadable_items['pdfs']:
                pdf_view = pdf_obj.restrictedTraverse('pdf')
                zf.writestr(pdf_obj.getId() + '.pdf', pdf_view.get_pdf())
        finally:
            zf.close()

        if zf.filelist:
            self.request.response.setHeader(
                "Content-Type",
                "application/zip"
            )
            now = datetime.now()
            zipfilename = "download-%s-%s-%s.zip" % (
                now.year, now.month, now.day)
            self.request.response.setHeader(
                'Content-Disposition',
                "attachment; filename=%s" % zipfilename
            )
            return output.getvalue()
        else:
            api.portal.show_message(
                message=_(u"There are no downloadable items in your cart."),
                request=self.request,
                type="warning")
            self.request.response.redirect(self.context.absolute_url())
