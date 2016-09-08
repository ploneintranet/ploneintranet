# coding=utf-8
from email.header import decode_header
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from ploneintranet import api as pi_api
from ploneintranet.workspace import utils
from Products.CMFCore.interfaces import IFolderish
from zope import event
from zope.component import adapter
from zope.container.contained import ObjectAddedEvent
import logging
import quopri
import re

log = logging.getLogger(__name__)


def get_recipients_from_msg(msg, address_type):
    ''' Get the addresses from message.

    address_type is one of TO, CC, BCC, ...
    '''
    addresses = msg.get(address_type, '').strip()
    if not addresses:
        return ()
    return tuple(
        address.strip()
        for address in addresses.decode('utf8').split(u',')
    )


class BaseImporter(object):
    ''' Create objects from an email
    '''
    mailin_keyworkds = []

    def decode(self, text):
        ''' Perform some magin on text to decode it

        text should be a filename

        TODO: explain this better!
        '''
        enc_re = re.compile('=\?([^\?]*)\?([BQ])\?(.*)\?=')
        # get rid of line breaks
        lines = text.splitlines()
        decoded = []
        for line in lines:
            match = enc_re.search(line)
            if match:
                if match.group(2) == 'B':
                    line = match.group(3).decode('base64')
                elif match.group(2) == 'Q':
                    line = quopri.decodestring(match.group(3))
                line = line.decode(match.group(1))
            decoded.append(line)
        return ''.join(decoded)

    def create_attachment(self, mail, part):
        ''' Create an attachment for this mail
        '''
        cid = part['Content-Id']
        file_name = part.get_filename() or cid
        content_type = part.get_content_type()
        payload = part.get_payload(decode=True)

        type_name = self.registry.findTypeName(
            file_name,
            content_type,
            payload
        ) or 'File'

        obj = api.content.create(
            type=type_name,
            title=file_name,
            container=mail,
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
            else:
                log.warning('Discarding paylod for %s', obj.UID())

        obj.setSubject(self.mailin_keyworkds)
        event.notify(ObjectAddedEvent(obj))
        return obj


@adapter(IFolderish)
class MailImporter(BaseImporter):
    """ IMailImportAdapter which imports an email into a content object
        inside the appropriate workspace.
    """
    mail_portal_type = 'ploneintranet.workspace.mail'
    mailin_keyworkds = [
        'email upload',
    ]

    def __init__(self, context):
        self.context = context
        self.registry = api.portal.get_tool('content_type_registry')

    def get_parts(sefl, msg):
        ''' Returns the parts as a dictionary
        '''
        parts = {
            'attachments': [],
        }
        msg_parts = (part for part in msg.walk() if not part.is_multipart())
        for part in msg_parts:
            cdisposition = part.get('Content-Disposition')
            if cdisposition is None:
                ctype = part.get('Content-Type')
                if 'text/html' in ctype:
                    parts['html'] = part
                else:
                    parts['text'] = part
            else:
                parts['attachments'].append(part)
        return parts

    def create_mail(self, msg):
        ''' Create the mail looking in to
        '''
        title, encoding = decode_header(msg.get('Subject'))[0]
        if encoding:
            title = title.decode(encoding).encode('utf-8')
        mail = api.content.create(
            type=self.mail_portal_type,
            title=title,
            container=self.context,
            id=self.context.generateId('mail-'),
            safe_id=False,
        )
        mail.manage_addLocalRoles(
            api.user.get_current().id,
            ['Owner'],
        )

        mail.mail_from = msg.get('From', '').decode('utf8')
        mail.mail_to = get_recipients_from_msg(msg, 'TO')
        mail.mail_cc = get_recipients_from_msg(msg, 'CC')
        mail.mail_bcc = get_recipients_from_msg(msg, 'BCC')
        mail.subject = self.mailin_keyworkds
        return mail

    def get_payload(self, part, encoding='utf8'):
        ''' Get's the encoded payload from part
        '''
        return (
            part
            .get_payload(decode=True)
            .decode(part.get_content_charset())
            .encode(encoding)
        )

    def set_mail_body(self, mail, parts, attachments):
        ''' Set's the body for this email

        For html mail it takes care of fixing eventual links to the contents,
        that for emails rea something like src="cid:content-id"

        The attachment dictionary maps the cid to the objects
        attachments = {
            None: <File at /plone/.../signature.asc>,
            '<6B1...00>': <Image at /plone/.../quaive.jpg>
        }
        '''
        if 'html' in parts:
            body = self.get_payload(parts['html'])
            # 'cid:6B1EAA1C-F248-48C8-BC2F-3E8F2633E02E@Speedport_W_921V_1_39_000'
            for key in attachments:
                if key:
                    body = body.replace(
                        u'src="cid:%s"' % key[1:-1],
                        u'src="resolveuid/%s"' % attachments[key].UID(),
                    )
        elif 'text' in parts:
            body = self.get_payload(parts['text'])
        else:
            body = u''

        mail.mail_body = RichTextValue(body)

    def store_original_message(self, mail, msg):
        ''' Add the original message as file
        '''
        obj = api.content.create(
            container=mail,
            type='File',
            title=u'email.eml',
            file=NamedBlobFile(
                data=str(msg),
                filename=u'original-email.eml'
            )
        )
        return obj

    def create_statusupdates(self, mail):
        ''' Create the status updates related to the received email
        '''
        objs = [mail]
        # Append the attachments with the exception of the original mail
        objs.extend(mail.objectValues()[:-1])
        for obj in objs:
            pi_api.microblog.statusupdate.create(
                content_context=obj,
                action_verb=u'created',
                tags=obj.Subject(),
            )

    def add(self, msg):
        ''' Create an email with attachments inside this objr
        '''
        pi_api.events.disable_microblog()
        # Extract the various parts
        mail = self.create_mail(msg)
        parts = self.get_parts(msg)
        attachments = {
            part['Content-Id']: self.create_attachment(mail, part)
            for part in parts['attachments']
        }
        self.set_mail_body(mail, parts, attachments)

        self.store_original_message(mail, msg)
        self.create_statusupdates(mail)
        pi_api.events.enable_microblog()
        return mail
