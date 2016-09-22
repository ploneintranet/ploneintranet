# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone import api
from plone.app.event.base import default_timezone
from plone.i18n.normalizer import idnormalizer
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.basecontent.utils import dexterity_update
from ploneintranet.workspace.basecontent.utils import get_selection_classes
from ploneintranet.workspace.utils import parent_workspace
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent


class AddBase(BrowserView):
    ''' Basic stuff for adding contents
    '''
    template = ViewPageTemplateFile('templates/add_content.pt')
    can_edit = True
    pat_inject = ' && '.join((
        'source: #document-body; target: #document-body',
        'source: #workspace-documents; target: #workspace-documents',
    ))

    def redirect(self, url):
        """
        Has its own method to allow overriding
        """
        url = '{}/view?show_sidebar'.format(url)
        return self.request.response.redirect(url)

    def validate(self):
        ''' Validate input and return a truish
        '''
        return True

    def get_new_unique_id(self):
        ''' This will get a new unique id according to the request
        '''
        form = self.request.form
        title = self.title or form.get('title')
        request_id = form.get('id')

        chooser = INameChooser(self.context)
        new_id = chooser.chooseName(
            idnormalizer.normalize(request_id or title),
            self.context
        )
        return new_id

    def get_new_object(self):
        ''' This will create a new object
        '''
        obj = api.content.create(
            container=self.context,
            type=self.portal_type,
            id=self.get_new_unique_id(),
            title=self.title or self.request.get('title'),
            safe_id=False,
        )
        return self.context[obj.getId()]

    def update(self, obj):
        ''' Update the object and returns the modified fields and errors
        '''
        modified, errors = dexterity_update(obj)
        return modified, errors

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

        new = self.get_new_object()
        modified, errors = self.update(new)

        if not errors:
            api.portal.show_message(
                _("Item created."),
                request=self.request,
                type="success"
            )
            new.reindexObject()
            notify(ObjectCreatedEvent(new))
        else:
            api.portal.show_message(
                _("There was a problem: %s." % errors),
                request=self.request,
                type="error",
            )

        return new.absolute_url()

    def __call__(self):
        """Render form, or handle POST and redirect"""
        title = self.request.form.get('title', None)
        portal_type = self.request.form.get('portal_type', '')
        if title is not None:
            self.portal_type = portal_type.strip()
            self.title = title.strip()
            if self.portal_type in api.portal.get_tool('portal_types'):
                url = self.create()
                return self.redirect(url)
        return self.template()


# AddWorkspace now lives in add_workspace.AddWorkspace


class AddFolder(AddBase):

    template = ViewPageTemplateFile('templates/add_folder.pt')


class AddLink(AddBase):
    ''' The add link view
    '''
    template = ViewPageTemplateFile('templates/add_form.pt')

    form_title = _('Create link')
    form_portal_type = 'Link'
    form_input_title_placeholder = _('Link name')

    def extra_fields(self):
        ''' BBB: this should be done in a cleaner way...
        '''
        return '''
            <input name="remoteUrl"
                   type="url"
                   placeholder="http(s)://..."
                   value="{remoteUrl}"
                   required="required"
              />
        '''.format(
            remoteUrl=self.request.form.get('remoteUrl', '')
        )


class AddTask(AddBase):

    template = ViewPageTemplateFile('templates/add_task.pt')

    def redirect(self, url):
        workspace = parent_workspace(self.context)
        url = workspace.absolute_url() + '?show_sidebar'
        return self.request.response.redirect(url)


class AddEvent(AddBase):

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
        url = workspace.absolute_url() + '?show_sidebar#workspace-events'
        return self.request.response.redirect(url)

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

    def get_selection_classes(self, field, default=None):
        """ identify all groups in the invitees """
        return get_selection_classes(self.context, field, default)
