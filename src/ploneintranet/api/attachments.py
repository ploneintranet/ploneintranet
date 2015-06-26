# -*- coding: utf-8 -*-
import uuid

from plone.dexterity.interfaces import IDexterityFTI
from plone.namedfile import NamedBlobFile
from zope.component import queryUtility, createObject

from ploneintranet.attachments.attachments import IAttachmentStorage


def get_storage(obj):
    """Get the attachment storage for the given object

    :param obj: The Plone object to get attachment storage for
    :type obj: Plone content object
    :return: The attachment storage
    :rtype: IAttachmentStorage
    """
    return IAttachmentStorage(obj)


def add(obj, filename, data):
    """Add the given data as an attachment on the given Plone object

    :param obj: The Plone object to add the attachment to
    :type obj: Plone content object
    :param filename: The name to give the attached file
    :type filename: str|unicode
    :param data: The file data to add
    :type data: str
    """
    if not isinstance(filename, unicode):
        filename = filename.decode('utf-8')
    namedfile = NamedBlobFile(
        data=data,
        filename=filename,
    )
    file_id = '{0}-{1}'.format(filename, uuid.uuid4().hex)
    if namedfile.contentType.startswith('image'):
        fti = queryUtility(IDexterityFTI, name='Image')
        attachment = createObject(
            fti.factory,
            id=file_id,
            image=namedfile)
    else:
        fti = queryUtility(IDexterityFTI, name='File')
        attachment = createObject(
            fti.factory,
            id=file_id,
            file=namedfile)
    attachment_storage = get_storage(obj)
    attachment_storage.add(attachment)


def get(obj, prefix=None):
    """Get the attachments of the given object optionally named with `prefix`

    :param obj: The Plone object to add the attachment to
    :type obj: Plone content object
    :param prefix: Optional attachment name prefix to return
    :type prefix: str|unicode
    """
    attachment_storage = get_storage(obj)
    if prefix is None:
        return attachment_storage.values()
    return [v for k, v in attachment_storage.items() if k.startswith(prefix)]
