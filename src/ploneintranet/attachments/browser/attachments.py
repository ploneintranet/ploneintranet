from AccessControl import Unauthorized
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from plone import api
from plone.rfc822.interfaces import IPrimaryFieldInfo
from ploneintranet.attachments.attachments import IAttachmentStorage
from ploneintranet.core.integration import PLONEINTRANET
from ploneintranet.docconv.client.interfaces import IDocconv
from zExceptions import NotFound
from zope.publisher.interfaces import IPublishTraverse
from zope.interface import implementer


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

    def _prepare_imagedata(self, obj, imgdata):
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
            length = imgdata.get_size(obj)
            R.setHeader('content-length', length)
            return imgdata.download(obj, REQUEST=self.request)

    def __call__(self):
        # FIXME
        if api.user.is_anonymous():
            raise Unauthorized()

        attachments = IAttachmentStorage(self.context)
        attachment = attachments[self.attachment_id]
        if not self.preview_type:
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

        docconv = IDocconv(attachment)
        if self.preview_type == 'thumb':
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
        container = PLONEINTRANET.microblog

        # FIXME
        if self.status_id not in container.allowed_status_keys():
            raise Unauthorized()

        return super(StatusAttachments, self).__call__()
