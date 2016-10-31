# -*- coding: utf-8 -*-
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.memoize.view import memoize
from plone.registry.interfaces import IRegistry
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from zope.component import getUtility

import logging

logger = logging.getLogger(__name__)


def get_invitee_details(context):
    """invitees is stored as a comma separated string of user ids.

    :rtype list of dicts: [{
        'id': 'user_id', 'name' 'user_title', 'email': 'user_email'}]
    """
    invitees = context.invitees
    if not invitees or not isinstance(invitees, basestring):
        return []
    users = pi_api.userprofile.get_users_from_userids_and_groupids(
        ids=invitees.split(',')
    )
    details = []
    for user in users:
        u_id = user.getId()
        name = user.getProperty('fullname') or user.getId() or u_id
        if not user.getProperty('email'):
            continue
        details.append({
            'id': user,
            'name': name,
            'email': user.getProperty('email'),
            'uid': u_id
        })
    return details


class EmailInvitees(BrowserView):
    """ Email the invitees a message with a link to the event
    """

    message_text = ViewPageTemplateFile('templates/email_invitees_text.pt')
    message_html = ViewPageTemplateFile('templates/email_invitees_html.pt')

    def get_message_html(self):
        ''' Get and compile an email message in html format
        '''
        return self.message_html().encode('utf-8')

    def get_message_text(self):
        ''' Get and compile an email message in plain text format
        '''
        return self.message_text().encode('utf-8')

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
            recipient = '{} <{}>'.format(self.invitee_name, invitee['email'])

            msg = MIMEMultipart('alternative')
            msg['Subject'] = self.get_subject()
            msg['From'] = self.get_sender()
            msg['To'] = recipient
            part1 = MIMEText(self.get_message_text(), 'plain')
            part2 = MIMEText(self.get_message_html(), 'html')
            part1.set_charset('utf-8')
            part2.set_charset('utf-8')
            msg.attach(part1)
            msg.attach(part2)
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
        self.request.response.redirect(self.context.absolute_url())
