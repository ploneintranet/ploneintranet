import logging
import transaction

from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.attachments.utils import IAttachmentStorage
from ploneintranet import api as pi_api

from ploneintranet.async.celeryconfig import ASYNC_ENABLED
from ploneintranet.async.tasks import GeneratePreview

log = logging.getLogger(__name__)


def generate_previews_async(obj, event=None):
    """ Generates the previews by dispatching them to the async service
    """
    # Need a commit to make sure the content is there
    transaction.commit()
    if ASYNC_ENABLED:
        generator = GeneratePreview(obj, obj.REQUEST)
        generator()
    else:
        pi_api.previews.generate_previews(obj)


def handle_file_creation(obj, event=None, async=True):
    """ Need own subscriber as cdv insists on checking for its
        custom layout. Also we want our own async mechanism.
    """
    if async:
        generate_previews_async(obj)
    else:
        pi_api.previews.generate_previews(obj)


def generate_attachment_preview_images(obj):
    if not IAttachmentStoragable.providedBy(obj):
        return
    attachment_storage = IAttachmentStorage(obj)
    for att_id in attachment_storage.keys():
        attachment = attachment_storage.get(att_id)
        if not pi_api.previews.has_previews(attachment):
            generate_previews_async(attachment)
            # pi_api.previews.generate_previews(attachment)


def content_added_in_workspace(obj, event):
    generate_previews_async(obj)
    # pi_api.previews.generate_previews(obj)


def content_edited_in_workspace(obj, event):
    if obj.REQUEST.form.get('file') or obj.REQUEST.get('method') == 'PUT':
        generate_previews_async(obj)
        # pi_api.previews.generate_previews(obj)


# def attachmentstoragable_added(obj, event):
#     generate_attachment_preview_images(obj)
