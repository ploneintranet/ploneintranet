# -*- coding: utf-8 -*-
"""A Cart Action for downloading all items listed in cart as a ZIP file."""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from StringIO import StringIO
from datetime import datetime
from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView

import zipfile


class DownloadView(BaseCartView):
    """Download Action implementation for downloading items listed in cart."""

    def confirm(self):
        index = ViewPageTemplateFile("templates/download_confirmation.pt")
        return index(self)

    def downloadable_items(self):
        for obj in self.items:
            downloadable = []
            not_downloadable = []
            # make sure obj is a file by checking if filename is set
            file_obj = getattr(obj, 'file', None)
            if file_obj:
                filename = file_obj.filename
                if filename:
                    downloadable.append(obj)
            if obj not in downloadable:
                not_downloadable.append(obj)
            return (downloadable, not_downloadable)

    def download(self):
        """Download cart content.

        Before downloading items are packed into a zip archive (only the
        items that are files are included).

        """
        output = StringIO()
        zf = zipfile.ZipFile(output, mode='w')

        downloadable, not_downloadable = self.downloadable_items()
        try:
            for obj in downloadable:
                zf.writestr(obj.file.filename, obj.file.data)
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
