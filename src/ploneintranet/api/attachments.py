# -*- coding: utf-8 -*-
import uuid

from plone.dexterity.interfaces import IDexterityFTI
from plone.namedfile import NamedBlobFile
from zope.component import queryUtility, createObject

from ploneintranet.attachments.attachments import IAttachmentStorage


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
        attachment = createObject(fti.factory,
                                  id=file_id,
                                  image=namedfile)
    else:
        fti = queryUtility(IDexterityFTI, name='File')
        attachment = createObject(fti.factory,
                                  id=file_id,
                                  file=namedfile)
    attachment_storage = IAttachmentStorage(obj)
    attachment_storage.add(attachment)
