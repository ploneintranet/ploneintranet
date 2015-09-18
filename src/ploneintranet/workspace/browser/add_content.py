# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.event.base import default_timezone
from plone.i18n.normalizer import idnormalizer
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.workspace.basecontent.utils import dexterity_update
from ploneintranet.workspace.case import create_case_from_template
from ploneintranet.workspace.utils import parent_workspace
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class AddContent(BrowserView):
    """
    Evaluate simple form and add arbitrary content.
    """

    template = ViewPageTemplateFile('templates/add_content.pt')
    can_edit = True

    def __call__(self, portal_type='', title=None):
        """Evaluate form and redirect"""
        if title is not None:
            self.portal_type = portal_type.strip()
            self.title = title.strip()
            if self.portal_type in api.portal.get_tool('portal_types'):
                url = self.create()
                return self.redirect(url)
        return self.template()

    def validate(self):
        ''' Validate input and return a truish
        '''
        return True

    def create(self):
        """
        Create content and return url. Uses dexterity_update to set the
        appropriate fields after creation.
        """
        if not self.validate():
            # BBB: do something clever that works with pat-inject
            # at the moment the @@add_something form is not a complete page
            # but just some markup,
            # so we cannot show that one here
            pass

        form = self.request.form
        new = None

        # BBB: this should be moved to a proper validate function!
        if self.portal_type == 'ploneintranet.workspace.case':
            template_id = form.get('template_id')
            if template_id:
                title = form.get('title')
                case_id = idnormalizer.normalize(title)
                new = create_case_from_template(template_id, case_id)
            else:
                api.portal.show_message(
                    _('Please specify which Case Template to use'),
                    request=self.request,
                    type="error",
                )
        else:
            container = self.context
            new = api.content.create(
                container=container,
                type=self.portal_type,
                title=self.title,
                safe_id=True,
            )

        if not new:
            return self.context.absolute_url()

        if self.portal_type == 'ploneintranet.workspace.workspacefolder':
            if 'scenario' in form:
                if form['scenario'] == '1':
                    external_visibility = 'secret'
                    join_policy = 'admin'
                    participant_policy = 'producers'
                elif form['scenario'] == '2':
                    external_visibility = 'private'
                    join_policy = 'team'
                    participant_policy = 'moderators'
                elif form['scenario'] == '3':
                    external_visibility = 'open'
                    join_policy = 'self'
                    participant_policy = 'publishers'
                else:
                    raise AttributeError

                new.set_external_visibility(external_visibility)
                new.join_policy = join_policy
                new.participant_policy = participant_policy

        modified, errors = dexterity_update(new)

        if modified and not errors:
            api.portal.show_message(
                _("Item created."), request=self.request, type="success")
            new.reindexObject()
            notify(ObjectModifiedEvent(new))

        if errors:
            api.portal.show_message(
                _("There was a problem: %s." % errors),
                request=self.request,
                type="error",
            )

        return new.absolute_url()

    def redirect(self, url):
        """
        Has its own method to allow overriding
        """
        url = '{}/view'.format(url)
        return self.request.response.redirect(url)


class AddFolder(AddContent):

    template = ViewPageTemplateFile('templates/add_folder.pt')


class AddTask(AddContent):

    template = ViewPageTemplateFile('templates/add_task.pt')

    def redirect(self, url):
        workspace = parent_workspace(self.context)
        return self.request.response.redirect(workspace.absolute_url())


class AddEvent(AddContent):

    template = ViewPageTemplateFile('templates/add_event.pt')

    def fix_start_end(self):
        ''' If the start date is lower than the end one,
        modify the request setting end = start + 1 hour
        '''
        localized_start = DateTime(
            '%s %s' % (
                ' '.join(self.request.get('start')),
                self.request.get('timezone', default_timezone())
            )
        )
        localized_end = localized_start + 1. / 24
        # If you know a smarter way to hijack the request,
        # please modify the following lines:)
        self.request.end = [
            localized_end.strftime('%Y-%m-%d'),
            localized_end.strftime('%H:%M'),
        ]
        self.request.form['end'] = self.request.end
        self.request.other['end'] = self.request.end

        ts = api.portal.get_tool('translation_service')
        msg = _(
            'dates_hijacked',
            default=(
                u'Start time should be lower than end time. '
                u'The system set the end time to: ${date}'
            ),
            mapping={
                u'date': ts.toLocalizedTime(localized_end)
            }
        )
        api.portal.show_message(
            msg,
            request=self.request,
            type="warning"
        )

    def validate(self):
        ''' Override base content validation

        Return truish if valid
        '''
        if self.request.get('start') > self.request.get('end'):
            self.fix_start_end()

        return True

    def redirect(self, url):
        workspace = parent_workspace(self.context)
        return self.request.response.redirect(workspace.absolute_url() +
                                              '#workspace-events')

    def default_start(self):
        now = DateTime()
        date = now.Date()
        time = self.round_minutes(now.TimeMinutes())
        result = DateTime(date + " " + time)
        return result

    def default_end(self):
        now = DateTime()
        date = now.Date()
        time = self.round_minutes(now.TimeMinutes())
        parts = time.split(":")
        parts[0] = str((int(parts[0]) + 1) % 24)
        result = DateTime(date + " " + parts[0] + ":" + parts[1])
        return result

    def round_minutes(self, time):
        hours, minutes = time.split(":")
        quarters = int(minutes) / 15 + 1
        minutes = str(quarters * 15)
        if minutes == "60":
            minutes = "00"
        return hours + ":" + minutes
