from plone import api
from plone.api.exc import InvalidParameterError
from ploneintranet import api as pi_api
from ploneintranet.async.celeryconfig import ASYNC_ENABLED
from ploneintranet.async.tasks import GeneratePreview
from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.attachments.utils import IAttachmentStorage

import logging
import transaction


log = logging.getLogger(__name__)


def generate_previews_async(obj, event=None, purge=False):
    """ Generates the previews by dispatching them to the async service

    If purge is True, remove old previews before creating the new ones
    """
    try:
        file_types = api.portal.get_registry_record(
            'ploneintranet.docconv.file_types')
        html_types = api.portal.get_registry_record(
            'ploneintranet.docconv.html_types')
    except InvalidParameterError:
        file_types = ['File', ]
        html_types = ['Document', ]

    if hasattr(obj, 'portal_type') and \
       obj.portal_type not in file_types + html_types:
        log.info('Skipping documentconversion for %s (unsupported type)'
                 % obj.absolute_url(1))
        return

    # Need a commit to make sure the content is there
    if ASYNC_ENABLED:
        if purge:
            pi_api.previews.purge_previews(obj)
        transaction.commit()
        log.debug('generate_previews_async - async mode')
        generator = GeneratePreview(obj, obj.REQUEST)
        log.info('starting preview generation with a delay of 10 secs')

        generator(countdown=10)
    else:
        log.debug('generate_previews_async - sync mode')
        pi_api.previews.generate_previews(obj)


def handle_file_creation(obj, event=None, async=True):
    """ Need own subscriber as cdv insists on checking for its
        custom layout. Also we want our own async mechanism.
    """
    event_key = 'ploneintranet.previews.handle_file_creation'
    enabled = obj.REQUEST.get(event_key, True)  # default is enabled
    if not enabled:
        log.debug("%s disabled", event_key)
        return

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
    event_key = 'ploneintranet.previews.content_added_in_workspace'
    enabled = obj.REQUEST.get(event_key, True)  # default is enabled
    if not enabled:
        log.debug("%s disabled", event_key)
        return

    log.debug('content_added_in_workspace - calling generate_previews_async')
    generate_previews_async(obj)


def content_edited_in_workspace(obj, event):
    if not hasattr(obj.REQUEST, 'form'):
        return
    # XXX: Why can this even happen?
    try:
        request_url = obj.REQUEST.getURL()
    except AttributeError:
        request_url = ''
    if obj.REQUEST.form.get('file') or \
       obj.REQUEST.form.get('form.widgets.IFileField.file') or\
       obj.REQUEST.form.get('text') or\
       obj.REQUEST.get('method') == 'PUT' or\
       request_url.endswith('revertversion'):

        event_key = 'ploneintranet.previews.content_edited_in_workspace'
        enabled = obj.REQUEST.get(event_key, True)  # default is enabled
        if not enabled:
            log.debug("%s disabled", event_key)
            return

        generate_previews_async(obj, purge=True)


# def attachmentstoragable_added(obj, event):
#     generate_attachment_preview_images(obj)
