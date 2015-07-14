import logging
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from plone import api
from plone.rfc822.interfaces import IPrimaryFieldInfo
from ploneintranet import api as piapi
from ploneintranet.attachments.attachments import IAttachmentStorage
from ploneintranet.docconv.client.interfaces import IDocconv
from zExceptions import NotFound
from zope.publisher.interfaces import IPublishTraverse
from zope.interface import implementer

log = logging.getLogger(__name__)


@implementer(IPublishTraverse)
class Attachments(BrowserView):
    """ Attachments
    """
    attachment_id = None
    preview_type = None

    def publishTraverse(self, request, name):
        # @@attachments/{attachment_id}[/{preview_type}]
        self.attachment_id = name

        stack = request['TraversalRequestNameStack']
        if stack:
            self.preview_type = stack.pop()

        request['TraversalRequestNameStack'] = []
        return self

    def _prepare_imagedata(self, attachment, imgdata):
        R = self.request.RESPONSE
        R.setHeader('content-type', 'image/jpeg')
        R.setHeader(
            'content-disposition', 'inline; '
            'filename="{0}_preview.jpg"'.format(
                safe_unicode(self.attachment_id).encode('utf8')))
        if isinstance(imgdata, basestring):
            length = len(imgdata)
            R.setHeader('content-length', length)
            return imgdata
        else:
            length = imgdata.get_size(attachment)
            R.setHeader('content-length', length)
            blob = imgdata.get(attachment, raw=True)
            charset = 'utf-8'
            return blob.index_html(
                REQUEST=self.request, RESPONSE=R,
                charset=charset
            )

    def _get_page_imgdata(self, previews):
        page = int(self.request.get('page', 1))
        if page - 1 >= len(previews):
            page = 0
        elif page < 1:
            page = 1
        imgdata = previews[page - 1]
        return imgdata

    def _prepare_pdfdata(self, pdfdata):
        R = self.request.RESPONSE
        R.setHeader('content-type', 'application/pdf')
        R.setHeader(
            'content-disposition',
            'attachment; filename="%s"' % '.'.join(
                (self.context.getId(), u'pdf')).encode('utf8'))
        if isinstance(pdfdata, basestring):
            length = len(pdfdata)
            R.setHeader('content-length', length)
            return pdfdata
        else:
            length = pdfdata.get_size(self.context)
            R.setHeader('content-length', length)
            blob = pdfdata.get(self.context, raw=True)
            charset = 'utf-8'
            return blob.index_html(
                REQUEST=self.request, RESPONSE=R,
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

    def render_attachments(self, attachments):
        """replaces ploneintranet/docconv/client/view.py helpers"""

        attachment = attachments[self.attachment_id]
        if not self.preview_type or self.preview_type in (
                'pdf-not-available', 'request-pdf'):
            return self._render_nopreview(attachment)

        docconv = IDocconv(attachment)

        # upload stage
        if self.preview_type == 'docconv_image_thumb.jpg':
            if docconv.has_thumbs():
                previews = docconv.get_thumbs()
                imgdata = self._get_page_imgdata(previews)
                return self._prepare_imagedata(attachment, imgdata)
        elif self.preview_type == 'docconv_image_preview.jpg':
            if docconv.has_previews():
                previews = docconv.get_previews()
                imgdata = self._get_page_imgdata(previews)
                return self._prepare_imagedata(attachment, imgdata)
        elif self.preview_type == 'pdf':
            if docconv.has_pdf():
                pdfdata = docconv.get_pdf()
                return self._prepare_pdfdata(pdfdata)

        # normal view stage
        elif self.preview_type == 'thumb':
            if docconv.has_thumbs():
                return self._prepare_imagedata(
                    attachment, docconv.get_thumbs()[0])
        elif self.preview_type == 'preview':
            if docconv.has_previews():
                return self._prepare_imagedata(
                    attachment, docconv.get_previews()[0])
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

        raise NotFound


@implementer(IPublishTraverse)
class StatusAttachments(Attachments):
    """ Attachments on a statusupdate
    """

    status_id = None

    def publishTraverse(self, request, name):
        # @@status-attachment/{status_id}/{attachment_id}[/{preview_type}]
        self.status_id = int(name)

        stack = request['TraversalRequestNameStack']
        self.attachment_id = stack.pop()
        if stack:
            self.preview_type = stack.pop()

        request['TraversalRequestNameStack'] = []
        return self

    def __call__(self):
        container = piapi.microblog.get_microblog()
        # requires ViewStatusUpdate on the statusupdate returned
        statusupdate = container.get(self.status_id)
        attachments = IAttachmentStorage(statusupdate)
        return self.render_attachments(attachments)
