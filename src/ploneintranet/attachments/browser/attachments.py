import logging
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from plone import api
from plone.rfc822.interfaces import IPrimaryFieldInfo
from ploneintranet import api as pi_api
from ploneintranet.attachments.attachments import IAttachmentStorage
from zExceptions import NotFound
from zope.publisher.interfaces import IPublishTraverse
from zope.interface import implementer
from plone.app.blob.download import handleRequestRange
from collective.documentviewer.settings import Settings
from webdav.common import rfc1123_date
from plone.app.blob.iterators import BlobStreamIterator
from AccessControl import getSecurityManager
from Products.CMFCore import permissions
from AccessControl import Unauthorized
from plone.app.blob.utils import openBlob
import os
log = logging.getLogger(__name__)


@implementer(IPublishTraverse)
class Attachments(BrowserView):
    """ Attachments
    """
    attachment_id = None
    preview_type = None
    page = None

    def publishTraverse(self, request, name):  # noqa
        # @@attachments/{attachment_id}[/{preview_type}]
        self.attachment_id = name

        stack = request['TraversalRequestNameStack']
        if stack:
            self.preview_type = stack.pop()
        if stack:
            try:
                self.page = int(stack.pop())
            except ValueError:
                self.page = 1
        request['TraversalRequestNameStack'] = []
        return self

    def _prepare_imagedata(self, attachment, imgdata):
        r = self.request.RESPONSE
        r.setHeader('content-type', 'image/jpeg')
        r.setHeader(
            'content-disposition', 'inline; '
            'filename="{0}_preview.jpg"'.format(
                safe_unicode(self.attachment_id).encode('utf8')))
        if isinstance(imgdata, basestring):
            length = len(imgdata)
            r.setHeader('content-length', length)
            return imgdata
        else:
            length = imgdata.get_size(attachment)
            r.setHeader('content-length', length)
            blob = imgdata.get(attachment, raw=True)
            charset = 'utf-8'
            return blob.index_html(
                REQUEST=self.request, RESPONSE=r,
                charset=charset
            )

    def _prepare_pdfdata(self, pdfdata):
        r = self.request.RESPONSE
        r.setHeader('content-type', 'application/pdf')
        r.setHeader(
            'content-disposition',
            'attachment; filename="%s"' % '.'.join(
                (self.context.getId(), u'pdf')).encode('utf8'))
        if isinstance(pdfdata, basestring):
            length = len(pdfdata)
            r.setHeader('content-length', length)
            return pdfdata
        else:
            length = pdfdata.get_size(self.context)
            r.setHeader('content-length', length)
            blob = pdfdata.get(self.context, raw=True)
            charset = 'utf-8'
            return blob.index_html(
                REQUEST=self.request, RESPONSE=r,
                charset=charset
            )

    def _render_nopreview(self, attachment):
        primary_field = IPrimaryFieldInfo(attachment).value
        mimetype = primary_field.contentType
        data = primary_field.data
        self.request.response.setHeader(
            'content-type', mimetype)
        self.request.response.setHeader(
            'content-disposition', 'inline; '
            'filename="{0}"'.format(
                safe_unicode(self.attachment_id).encode('utf8')))
        return data

    def __call__(self):
        # requires View on self.context
        attachments = IAttachmentStorage(self.context)
        # separate rendering out for subclass use
        return self.render_attachments(attachments)

    def render_attachment_preview(self, attachment):
        sm = getSecurityManager()
        if not sm.checkPermission(permissions.View, self.context):
            raise Unauthorized

        r = self.request.response
        settings = Settings(attachment)

        if self.preview_type not in ('large', 'normal', 'small'):
            self.preview_type = 'small'
        if self.page is None:
            self.page = 1
        filepath = u'%s/dump_%s.%s' % (self.preview_type,
                                       self.page,
                                       settings.pdf_image_format)
        blob = settings.blob_files[filepath]
        blobfi = openBlob(blob)
        length = os.fstat(blobfi.fileno()).st_size
        blobfi.close()
        ext = os.path.splitext(os.path.normcase(filepath))[1][1:]
        if ext == 'txt':
            ct = 'text/plain'
        else:
            ct = 'image/%s' % ext

        r.setHeader('Content-Type', ct)
        r.setHeader('Last-Modified',
                    rfc1123_date(self.context._p_mtime))
        r.setHeader('Accept-Ranges', 'bytes')
        r.setHeader("Content-Length", length)
        request_range = handleRequestRange(self.context,
                                           length,
                                           self.request,
                                           self.request.response)
        return BlobStreamIterator(blob, **request_range)

    def render_attachments(self, attachments):
        """replaces ploneintranet/docconv/client/view.py helpers"""

        attachment = attachments[self.attachment_id]
        if not self.preview_type or self.preview_type in (
                'pdf-not-available', 'request-pdf'):
            return self._render_nopreview(attachment)

        # old way of doing things
        # upload stage
        if self.preview_type == 'pdf':
            if pi_api.previews.has_pdf():
                pdfdata = pi_api.previews.get_pdf()
                return self._prepare_pdfdata(pdfdata)
        # normal view stage
        elif self.preview_type == '@@images':
            images = api.content.get_view(
                'images',
                attachment.aq_base,
                self.request,
            )
            return self._prepare_imagedata(
                attachment,
                str(images.scale(scale='preview').data.data)
            )
        else:
            return self.render_attachment_preview(attachment)

        raise NotFound


@implementer(IPublishTraverse)
class StatusAttachments(Attachments):
    """ Attachments on a statusupdate
    """

    status_id = None

    def publishTraverse(self, request, name):  # noqa
        # @@status-attachment/{status_id}/{attachment_id}[/{preview_type}]
        self.status_id = int(name)

        stack = request['TraversalRequestNameStack']
        self.attachment_id = stack.pop()
        if stack:
            self.preview_type = stack.pop()

        request['TraversalRequestNameStack'] = []
        return self

    def __call__(self):
        container = pi_api.microblog.get_microblog()
        # requires ViewStatusUpdate on the statusupdate returned
        statusupdate = container.get(self.status_id)
        attachments = IAttachmentStorage(statusupdate)
        return self.render_attachments(attachments)
