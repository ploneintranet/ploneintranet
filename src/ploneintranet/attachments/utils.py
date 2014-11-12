import logging
from Acquisition import aq_base
from datetime import datetime, timedelta
from plone.app.blob.content import ATBlob
from plone.app.blob.markings import markAs
from ploneintranet.attachments.attachments import IAttachmentStorage
from zope.container.interfaces import DuplicateIDError

log = logging.getLogger(__name__)


def extract_attachments(file_upload, workspace=None, token=None):
    if not file_upload:
        return
    if not isinstance(file_upload, list):
        file_upload = [file_upload, ]
    attachments = []
    for file_field in file_upload:
        attachment = None
        if token is not None and workspace is not None:
            attachment = pop_temporary_attachment(workspace, file_field, token)
        if attachment is None:
            attachment = create_attachment(file_field)
        attachments.append(attachment)
    return attachments


def pop_temporary_attachment(workspace, file_field, token):
    temp_attachments = IAttachmentStorage(workspace)
    temp_id = '{0}-{1}'.format(token, file_field.filename)
    if temp_id in temp_attachments.keys():
        temp_att = aq_base(temp_attachments.get(temp_id))
        temp_att.id = file_field.filename
        temp_att.update_data(file_field.read())
        temp_attachments.remove(temp_id)
        return temp_att
    return None


def create_attachment(file_field):
        attachment = ATBlob(file_field.filename)
        if file_field.headers.get('content-type').split('/')[0] == 'image':
            subtype = 'Image'
        else:
            subtype = 'File'
        markAs(attachment, subtype)
        if hasattr(attachment, '_setPortalTypeName'):
            attachment._setPortalTypeName(subtype)
        attachment.initializeArchetype()
        attachment.update_data(file_field.read())
        return attachment


def add_attachments(attachments, attachment_storage):
    for attachment in attachments:
        filename = attachment.getId()
        i = 0
        while filename in attachment_storage.keys():
            if i > 9999:
                raise DuplicateIDError
            i += 1
            filename = '{0}-{1}'.format(attachment.getId(), i)
        if attachment.id != filename:
            attachment.id = filename
        attachment_storage.add(attachment)


def clean_up_temporary_attachments(workspace, maxage=1):
    temp_attachments = IAttachmentStorage(workspace)
    for key in temp_attachments.keys():
        keyparts = key.split('-')
        datestr = keyparts[1]
        try:
            date = datetime.strptime(datestr, '%Y%m%d%H%M%S%f')
        except ValueError:
            date = datetime.min  # No proper datestr, treat as old
        if datetime.now() - date > timedelta(maxage):
            temp_attachments.remove(key)
            log.info('Cleaned up temporary attachment {0} from '
                     '{1}'.format(key, workspace.Title()))


def extract_and_add_attachments(file_upload, obj, workspace=None, token=None):
    """Create attachments from a file upload field.

    Extract file data from file_upload, create file/image objects and add
    them as attachments to obj. If workspace and token are given, reuse
    previously uploaded temporary attachments if they exist.
    """
    if not file_upload:
        return
    if not isinstance(file_upload, list):
        file_upload = [file_upload, ]
    attachment_storage = IAttachmentStorage(obj)
    attachments = extract_attachments(
        file_upload, workspace=workspace, token=token)
    add_attachments(attachments, attachment_storage)
    if workspace:
        clean_up_temporary_attachments(workspace)
