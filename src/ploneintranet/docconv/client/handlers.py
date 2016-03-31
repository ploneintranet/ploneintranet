import logging
import transaction

from ploneintranet.docconv.client import SUPPORTED_CONTENTTYPES
from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.attachments.utils import IAttachmentStorage
from ploneintranet import api as pi_api

from ploneintranet.async.celeryconfig import ASYNC_ENABLED
from ploneintranet.async.tasks import GeneratePreview

log = logging.getLogger(__name__)


def generate_previews_async(obj, event=None):
    """ Generates the previews by dispatching them to the async service
    """
    if hasattr(obj, 'portal_type') and \
       obj.portal_type not in SUPPORTED_CONTENTTYPES:
        log.info('Skipping documentconversion for %s (unsupported type)'
                 % obj.absolute_url(1))
        return
    # Need a commit to make sure the content is there
    if ASYNC_ENABLED:
        transaction.commit()
        log.debug('generate_previews_async - async mode')
        generator = GeneratePreview(obj, obj.REQUEST)
        log.info('starting preview generation with a delay of 5 secs')
        generator(countdown=5)
    else:
        log.debug('generate_previews_async - sync mode')
        pi_api.previews.generate_previews(obj)


def handle_file_creation(obj, event=None, async=True):
    """ Need own subscriber as cdv insists on checking for its
        custom layout. Also we want our own async mechanism.
    """
    if async:
        log.debug('handle_file_creation - async mode')
        generate_previews_async(obj)
    else:
        log.debug('handle_file_creation - sync mode')
        pi_api.previews.generate_previews(obj)


def generate_attachment_preview_images(obj):
    if not IAttachmentStoragable.providedBy(obj):
        return
    attachment_storage = IAttachmentStorage(obj)
    for att_id in attachment_storage.keys():
        attachment = attachment_storage.get(att_id)
        if not pi_api.previews.has_previews(attachment):
            log.debug('generate_attachment_preview_images'
                      ' - generating attachment preview')
            generate_previews_async(attachment)


def content_added_in_workspace(obj, event):
    log.debug('content_added_in_workspace - calling generate_previews_async')
    generate_previews_async(obj)
    # pi_api.previews.generate_previews(obj)


def content_edited_in_workspace(obj, event):
    if not hasattr(obj.REQUEST, 'form'):
        return
    if obj.REQUEST.form.get('file') or\
       obj.REQUEST.form.get('form.widgets.IFileField.file') or\
       obj.REQUEST.get('method') == 'PUT':
        pi_api.previews.generate_previews(obj)


# def attachmentstoragable_added(obj, event):
#     generate_attachment_preview_images(obj)
