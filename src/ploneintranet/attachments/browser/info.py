from Products.Five.browser import BrowserView
from zope.interface import implements

from ploneintranet.attachments.attachments import IAttachmentStorage
from ploneintranet.attachments.interfaces import IAttachmentInfo


class AttachmentInfo(BrowserView):
    implements(IAttachmentInfo)

    def get_attachment_ids(self):
        return IAttachmentStorage(self.context).keys()
