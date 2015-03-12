from Products.Five.browser import BrowserView
from ploneintranet.core.integration import PLONESOCIAL
from ploneintranet.attachments.attachments import IAttachmentStorage
from zExceptions import NotFound
from zope.publisher.interfaces import IPublishTraverse
from zope.interface import implementer

try:
    from ploneintranet.docconv.client.interfaces import IDocconv
except ImportError:
    IDocconv = None


@implementer(IPublishTraverse)
class StatusAttachments(BrowserView):

    def __init__(self, context, request):
        super(StatusAttachments, self).__init__(context, request)
        self.status_id = self.attachment_id = self.preview_type = None

        if not request.path:
            return
        self.status_id = request.path.pop()
        self.status_id = int(self.status_id)
        if not request.path:
            return
        self.attachment_id = request.path.pop()
        if not request.path:
            return
        self.preview_type = request.path.pop()

    def _prepare_imagedata(self, obj, imgdata):
        R = self.request.RESPONSE
        R.setHeader('content-type', 'image/jpeg')
        R.setHeader('content-disposition', 'inline; '
                    'filename="{0}_preview.jpg"'.format(
                        self.attachment_id.encode('utf8')))
        if isinstance(imgdata, basestring):
            length = len(imgdata)
            R.setHeader('content-length', length)
            return imgdata
        else:
            length = imgdata.get_size(obj)
            R.setHeader('content-length', length)
            return imgdata.download(obj, REQUEST=self.request)

    def __call__(self):

        if not self.status_id:
            return self
        container = PLONESOCIAL.microblog
        status = container.get(self.status_id)
        if not self.attachment_id:
            # do we want to be able to traverse to the status update itself?
            # Returning only the id for now
            return self.status_id
        attachments = IAttachmentStorage(status)
        attachment = attachments.get(self.attachment_id)
        if not self.preview_type:
            self.request.response.setHeader(
                'content-type', attachment.getContentType())
            self.request.response.setHeader(
                'content-disposition', 'inline; '
                'filename="{0}"'.format(
                    self.attachment_id.encode('utf8')))
            return attachment
        if IDocconv is not None:
            docconv = IDocconv(attachment)
            if self.preview_type == 'thumb':
                if docconv.has_thumbs():
                    return self._prepare_imagedata(
                        attachment, docconv.get_thumbs()[0])
            elif self.preview_type == 'preview':
                if docconv.has_previews():
                    return self._prepare_imagedata(
                        attachment, docconv.get_previews()[0])
        raise NotFound

    def publishTraverse(self, request, name):
        request['TraversalRequestNameStack'] = []
        return self
