from Products.Archetypes.event import ObjectEditedEvent
from Products.CMFCore.interfaces import IFolderish
from ploneintranet.workspace import utils
from plone import api
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from plone.namedfile.file import NamedBlobImage
from plone.namedfile.file import NamedBlobFile
from zope import component
from zope import event
import logging
import quopri
import re

log = logging.getLogger(__name__)

MAILIN_LABEL = 'email upload'


class BaseImporter(object):
    """ """

    def decode(self, string):
        enc_re = re.compile('=\?([^\?]*)\?([BQ])\?(.*)\?=')
        # get rid of line breaks
        lines = map(lambda s: s.strip('\r'), string.split('\n'))
        decoded = []
        for line in lines:
            match = enc_re.search(line)
            if match:
                if match.group(2) == 'B':
                    decoded.append(
                        match.group(3).decode('base64').decode(match.group(1)))
                elif match.group(2) == 'Q':
                    decoded.append(
                        quopri.decodestring(
                            match.group(3)).decode(match.group(1)))
            else:
                decoded.append(line)
        return ''.join(decoded)

    def process_email_attachment(self, index, part, container):
        file_name = part.get_filename()
        content_type = part.get_content_type()
        payload = part.get_payload(decode=1)
        if not file_name:
            file_name = 'attachment-%d' % index
        else:
            # handle base64 or quoted printable encoding
            file_name = self.decode(file_name)
        type_name = self.registry.findTypeName(
            file_name, content_type, payload)
        obj = api.content.create(
            type=type_name,
            title=file_name,
            container=container
        )
        if type_name == 'File':
            obj.file = NamedBlobFile(
                data=payload,
                filename=unicode(file_name)
            )
        elif type_name == 'Image':
            obj.image = NamedBlobImage(
                data=payload,
                filename=unicode(file_name)
            )
        else:
            primary = utils.get_primary_field(obj)
            if primary:
                primary[1].set(obj, payload)
        obj.setSubject([MAILIN_LABEL])
        event.notify(ObjectEditedEvent(obj))
        return True


class MailImporter(BaseImporter):
    """ IMailImportAdapter which imports an email into a content object
        inside the appropriate workspace.
    """
    component.adapts(IFolderish)

    def __init__(self, context):
        self.context = context
        self.normalizer = component.queryUtility(IFileNameNormalizer)
        self.registry = api.portal.get_tool('content_type_registry')

    def add(self, msg):
        """ Extract attachments inside this container.
        """
        result = False

        # Extract the various parts
        for index, part in enumerate(msg.walk()):
            if part.is_multipart():
                # Ignore the multipart container, we will eventually walk
                # through all of its contents.
                continue
            if part.get_filename() is None and \
                    part.get('Content-Disposition') in [None, 'inline']:
                # ignore email body
                result = True
            else:
                result = self.process_email_attachment(
                    index, part, self.context)

        return result
