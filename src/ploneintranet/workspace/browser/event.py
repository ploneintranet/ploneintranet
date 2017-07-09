# -*- coding: utf-8 -*-
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from plone import api
from plone.memoize.view import memoize
from plone.registry.interfaces import IRegistry
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility

import logging
import re


logger = logging.getLogger(__name__)


def get_invitees(context):
    '''invitees is stored as a comma separated string of user ids
    or emails addresses.

    This function transforms them into users
    '''
    invitees = context.invitees
    if not invitees or not isinstance(invitees, basestring):
        return []
    invitees = invitees.split(',')
    principalids = set()
    # BBB: we may want to think to a better regexp to extract principalid
    # when the invitee looks like "John Doe <john.doe@example.net>"
    pattern = re.compile(r'(.*)<(.*)>')
    for invitee in invitees:
        match = pattern.match(invitee)
        if match:
            principalids.add(match.groups()[-1])
        else:
            principalids.add(invitee)

    return pi_api.userprofile.get_users_from_userids_and_groupids(principalids)


def get_invitee_details(context, skip_no_emails=True):
    """invitees is stored as a comma separated string of user ids
    or emails addresses.

    :rtype list of dicts: [{
        'id': 'user_id', 'name' 'user_title', 'email': 'user_email'}]
    """
    details = []
    invitees = get_invitees(context)
    for invitee in invitees:
        email = getattr(invitee, 'email', u'')
        if not email and skip_no_emails:
            continue
        userid = invitee.getId()
        name = invitee.fullname or userid
        details.append({
            'id': invitee,
            'name': name,
            'email': email,
            'uid': userid
        })
    return details


class EmailInvitees(BrowserView):
    """ Email the invitees a message with a link to the event
    """

    message_html = ViewPageTemplateFile('templates/email_invitees_html.pt')

    def get_message_html(self):
        ''' Get and compile an email message in html format
        '''
        return self.message_html().encode('utf-8')

    def get_sender(self):
        ''' Return the email sender
        '''
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix='plone')
        return u'{} <{}>'.format(
            mail_settings.email_from_name,
            mail_settings.email_from_address
        )

    def get_subject(self):
        ''' Return the email subject based on this event title and dates
        '''
        return u'{}: {}'.format(
            self.context.title,
            self.context.start.strftime('%Y/%m/%d %H:%M')
        )

    def iter_messages(self):
        ''' Return the payload to deliver a s mime/multipart message
        '''
        invitees = get_invitee_details(self.context)

        for invitee in invitees:
            self.invitee_name = invitee['name']
            if isinstance(self.invitee_name, unicode):
                self.invitee_name = self.invitee_name.encode('utf8')
            recipient = '{} <{}>'.format(self.invitee_name, invitee['email'])
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self.get_subject()
            msg['From'] = self.get_sender()
            msg['To'] = recipient
            html = self.get_message_html()
            part = MIMEText(html, 'html')
            part.set_charset('utf-8')
            msg.attach(part)
            yield msg

    @memoize
    def send(self):
        ''' Send the messages and return the errors
        '''
        errors = 0
        for msg in self.iter_messages():
            try:
                api.portal.send_email(
                    recipient=msg['To'],
                    subject=msg['Subject'],
                    body=msg,
                )
            except Exception, error:
                logger.error("MailHost error: {0}".format(error))
                api.portal.show_message(
                    _(u'Error sending email'), self.request, 'error')
                errors += 1
        return errors

    def __call__(self):
        ''' Send email and report on success of failures
        '''
        errors = self.send()
        if errors == 0:
            api.portal.show_message(
                _(u'Emails sent successfully'),
                self.request,
                'success'
            )
        else:
            api.portal.show_message(
                u'%d errors, see logs for more details' % errors,
                self.request,
                'error'
            )
        # self.request.response.redirect(self.context.absolute_url())
        msg = ViewPageTemplateFile('templates/globalstatusmessage.pt')
        return msg(self)
