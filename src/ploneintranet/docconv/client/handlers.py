import logging

from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.attachments.utils import IAttachmentStorage
from ploneintranet.docconv.client.interfaces import IDocconv

from collective.documentviewer.settings import GlobalSettings
from collective.documentviewer.utils import allowedDocumentType
from collective.documentviewer.utils import getPortal
from .convert import Converter

log = logging.getLogger(__name__)


def handle_file_creation(obj, event=None):
    """ Need own subscriber as cdv insists on checking for its
        custom layout. Also we want our own async mechanism.
    """
    site = getPortal(obj)
    gsettings = GlobalSettings(site)

    if not allowedDocumentType(obj, gsettings.auto_layout_file_types):
        return

    if gsettings.auto_convert:
        # ASYNC HERE
        converter = Converter(obj)
        if not converter.can_convert:
            return
        converter()


def generate_attachment_preview_images(obj):
    if not IAttachmentStoragable.providedBy(obj):
        return
    attachment_storage = IAttachmentStorage(obj)
    for att_id in attachment_storage.keys():
        docconv = IDocconv(attachment_storage.get(att_id))
        if not docconv.has_thumbs():
            docconv.generate_all()


def content_added_in_workspace(obj, event):
    handle_file_creation(obj, event)


def content_edited_in_workspace(obj, event):
    if obj.REQUEST.form.get('file') or obj.REQUEST.get('method') == 'PUT':
        handle_file_creation(obj, event)


def attachmentstoragable_added(obj, event):
    generate_attachment_preview_images(obj)
