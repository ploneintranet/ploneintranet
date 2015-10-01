import logging

from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.attachments.utils import IAttachmentStorage
from ploneintranet import api as pi_api

log = logging.getLogger(__name__)


def handle_file_creation(obj, event=None):
    """ Need own subscriber as cdv insists on checking for its
        custom layout. Also we want our own async mechanism.
    """
    pi_api.previews.generate_previews(obj)


def generate_attachment_preview_images(obj):
    if not IAttachmentStoragable.providedBy(obj):
        return
    attachment_storage = IAttachmentStorage(obj)
    for att_id in attachment_storage.keys():
        attachment = attachment_storage.get(att_id)
        if not pi_api.previews.has_previews(attachment):
            pi_api.previews.generate_previews(attachment)


def content_added_in_workspace(obj, event):
    pi_api.previews.generate_previews(obj)


def content_edited_in_workspace(obj, event):
    if obj.REQUEST.form.get('file') or obj.REQUEST.get('method') == 'PUT':
        pi_api.previews.generate_previews(obj)


# def attachmentstoragable_added(obj, event):
#     generate_attachment_preview_images(obj)
