from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.MailHost.MailHost import MailHostError
from base64 import b64encode
from collective.documentviewer.settings import GlobalSettings
from collective.documentviewer.utils import allowedDocumentType
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from plone import api
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from ploneintranet.api import previews
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView
from ploneintranet.workspace.utils import parent_workspace

import logging

log = logging.getLogger(__name__)


class MailView(BaseCartView):

    @property
    def workspace(self):
        return parent_workspace(self.context)

    def confirm(self):
        index = ViewPageTemplateFile("templates/mail_send_confirmation.pt")
        return index(self)

    def send(self):
        msg = MIMEMultipart()

        form = self.request.form
        message = form.get('message')
        message += "\n\n"
        message += _("""The following items have been shared with you:""")
        attachable_uids = form.get('attachable_uids', [])
        unattachable_uids = form.get('unattachable_uids', [])
        all_uids = attachable_uids + unattachable_uids
        for uid in all_uids:
            obj = api.content.get(UID=uid)
            if obj:
                message += """
* {}/view""".format(obj.absolute_url())
        current_user = api.user.get_current()
        from_name = (
            current_user.getProperty('fullname') or current_user.getId())
        from_email = current_user.getProperty('email') or ''
        from_address = '{} <{}>'.format(from_name, from_email)
        msg["From"] = from_address
        msg["Subject"] = _(u"Some items have been sent to you.")
        body = MIMEText(message, 'plain', 'utf-8')
        msg.attach(body)

        recipients = form.get('recipients')
        if not recipients:
            # Should we show an error notification?
            log.debug('No recipients were selected, no email has been sent.')

        to_addresses = []
        for recipient in recipients.split(','):
            to_user = api.user.get(recipient)
            if not to_user:
                to_addresses.append(recipient)
            else:
                name = to_user.getProperty('fullname') or to_user.getId()
                email = to_user.getProperty('email')
                to_addresses.append('{} <{}>'.format(name, email))

        msg["To"] = ', '.join(to_addresses)

        for uid in attachable_uids:
            obj = api.content.get(UID=uid)
            if obj and hasattr(obj, 'file'):
                att = MIMEBase(*obj.file.contentType.split("/"))
                att.set_payload(b64encode(obj.file.data))
                att.add_header('Content-Transfer-Encoding', 'base64')
                att.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=obj.Title(),
                )
                msg.attach(att)

        mailhost = api.portal.get_tool('MailHost')
        try:
            mailhost.send(msg.as_string())
        except MailHostError, e:
            log.error(e.message)
        self.request.response.redirect(self.context.absolute_url())

    def attachable_objs(self):
        """
        We can only attach files. When implemented, we will also attach the PDF
        version of Documents
        """
        objs = []
        for obj in self.items:
            if IFile.providedBy(obj) or IImage.providedBy(obj):
                objs.append(obj)
        return objs

    def get_previews(self, obj):
        portal = api.portal.get()
        gsettings = GlobalSettings(portal)

        preview_details = {'class': 'not-generated', 'has_preview': False}
        if not allowedDocumentType(obj, gsettings.auto_layout_file_types):
            preview_details['class'] = 'not-possible'
        elif previews.has_previews(obj):
            preview_urls = previews.get_preview_urls(obj)
            if preview_urls:
                preview_details = {
                    'class': '',
                    'url': preview_urls[0],
                    'page_count': len(preview_urls),
                    'has_preview': True,
                }
        return preview_details
