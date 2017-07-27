# -*- coding: utf-8 -*-
from DateTime import DateTime
from json import dumps
from plone import api
from plone.app.event.base import default_timezone
from plone.memoize.view import memoize
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.browser.base import BasePanel
from ploneintranet.workspace.basecontent.utils import dexterity_update
from ploneintranet.workspace.basecontent.utils import get_selection_classes
from ploneintranet.workspace.utils import parent_workspace
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.container.interfaces import INameChooser
from zope.deprecation import deprecate
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent


class AddBase(BasePanel):
    ''' Basic stuff for adding contents
    '''
    title = _('Create document')
    template = ViewPageTemplateFile('templates/add_content.pt')
    can_edit = True
    _form_data_pat_inject_parts = (
        '#document-body',
        '#workspace-documents',
        '#global-statusmessage; loading-class: \'\'',
    )

    @memoize
    def form_timestamp(self):
        ''' Return a timestamp, used in the form to create unique selectors
        '''
        return DateTime().strftime('%s')

    @property
    @memoize
    def form_data_pat_validation(self):
        ''' Proper pat-validation options.
        We need to match the timestamp of the create button.
        '''
        return 'disable-selector:#form-buttons-create-{timestamp}'.format(
            timestamp=self.form_timestamp()
        )

    @property
    @memoize
    def portal(self):
        ''' Return the portal
        '''
        return api.portal.get()

    @property
    @memoize
    def workspace_container(self):
        ''' Return the workspace container
        '''
        return self.portal.workspaces

    @property
    @memoize
    def parent_workspace(self):
        ''' Return the parent workspace
        '''
        return parent_workspace(self.context)

    @property
    @memoize
    def user(self):
        ''' The currently authenticated ploneintranet user profile (if any)
        '''
        return pi_api.userprofile.get_current()

    @property
    @memoize
    def content_helper_view(self):
        ''' Use the content_helper_view
        '''
        return api.content.get_view(
            'content_helper_view',
            self.context,
            self.request,
        )

    @property
    @memoize
    def allusers_json_url(self):
        ''' Return @@allusers.json in the proper context
        '''
        return '{}/@@allusers.json'.format(
            self.parent_workspace.absolute_url()
        )

    def get_data_pat_autosuggest(self, fieldname):
        ''' Return the data-pat-autosuggest for a fieldname
        '''
        user = self.user
        if (
            fieldname == 'initiator' and
            self.request.method == 'GET' and
            user
        ):
            default_field_value = user.getId()
        else:
            default_field_value = ''

        prefill_json = self.content_helper_view.safe_member_prefill(
            self.context,
            fieldname,
            default=default_field_value,
        )
        if not prefill_json:
            prefill_json = '{}'

        if user and fieldname == 'initiator' and prefill_json == user.getId():
            prefill_json = dumps({
                user.username: user.fullname,
            })

        return '; '.join((
            'ajax-data-type: json',
            'maximum-selection-size: 1',
            'selection-classes: {}',
            'ajax-url: {}'.format(self.allusers_json_url),
            'allow-new-words: false',
            'prefill-json: {}'.format(prefill_json),
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

    def get_new_unique_id(self, container):
        ''' This will get a new unique id according to the request
        '''
        form = self.request.form
        title = self.title or form.get('title')
        request_id = form.get('id')

        chooser = INameChooser(container)
        new_id = chooser.chooseName(
            request_id or title,
            container
        )
        return new_id

    def get_new_object(self, container=None):
        ''' This will create a new object
        '''
        if not container:
            container = self.context
        obj = api.content.create(
            container=container,
            type=self.portal_type,
            id=self.get_new_unique_id(container),
            title=self.title or self.request.get('title'),
            safe_id=False,
        )
        return container[obj.getId()]

    def update(self, obj):
        ''' Update the object and returns the modified fields and errors
        '''
        modified, errors = dexterity_update(obj)
        return modified, errors

    def create(self, container=None):
        """
        Create content in the given container and return url.
        Uses dexterity_update to set the
        appropriate fields after creation.
        """
        if not self.validate():
            # BBB: do something clever that works with pat-inject
            # at the moment the @@add_something form is not a complete page
            # but just some markup,
            # so we cannot show that one here
            pass
        new = self.get_new_object(container)
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
        container_path = self.request.form.get('container', None)
        if container_path:
            container = self.context.restrictedTraverse(container_path)
        else:
            container = self.context

        if title is not None:
            self.portal_type = portal_type.strip()
            self.title = title.strip()
            if self.portal_type in api.portal.get_tool('portal_types'):
                url = self.create(container)
                return self.redirect(url)
        return self.template()


# AddWorkspace now lives in add_workspace.AddWorkspace


class AddFolder(AddBase):

    template = ViewPageTemplateFile('templates/add_folder.pt')
    title = _('Create folder')
    _form_data_pat_inject_parts = (
        '#workspace-documents',
        'nav.breadcrumbs',
    )


class AddLink(AddBase):
    ''' The add link view
    '''
    template = ViewPageTemplateFile('templates/add_form.pt')

    title = _('Create link')
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


class AddEvent(AddBase):

    template = ViewPageTemplateFile('templates/add_event.pt')
    title = _('Create event')

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

    @property
    @memoize
    def _form_data_pat_inject_parts(self):
        """ Returns the correct dpi config """
        selectors = []
        if self.request.get('app'):
            # When we are adding an event through the caendar we want to reload
            # the sidebar (first)...
            if not self.parent_workspace:
                selectors.append('#sidebar')
            else:
                selectors.append('#workspace-events')
            # ...and the calendar (which pat-depends on the sidebar, second)
            selectors.append('#document-content')
        else:
            # BBB: if we add an event in the workspace
            # it may not be enough to reload the sidebar
            # if we are viewing the calendar it should also be refreshed
            selectors.append('#workspace-events')
        parts = [
            "source: {0}; target: {0};".format(selector)
            for selector in selectors
        ]
        # and of course we want to update the status message
        parts.append(
            "source: {0}; target: {0}; loading-class: ''".format(
                '#global-statusmessage',
            )
        )
        return parts

    def redirect(self, url):
        ''' Try to find the proper redirect context.
        '''
        workspace = self.parent_workspace
        if self.request.get('app'):
            # This means the event is created using the fullcalendar tile
            if workspace:
                # Go to the workspace calendar
                container = self.request.get('container')
                if (
                    container and
                    container != u'/'.join(workspace.getPhysicalPath())
                ):
                    url = '%s/@@workspace-calendar?all_calendars=1'

                else:
                    url = '%s/@@workspace-calendar'
                url = url % workspace.absolute_url()
            else:
                # if not render the app view
                url = self.context.absolute_url() + '/@@app-calendar'
        else:
            # This is an event created on a workspace
            url = workspace.absolute_url() + '?show_sidebar#workspace-events'
        return self.request.response.redirect(url)

    def round_date(self, dt):
        ''' Round the datetime minutes and seconds to the next quarter,
        i.e. '2000/01/01 00:35:21' becomes '2000/01/01 00:30:00'
        '''
        remainder = float(dt) % 900
        if not remainder:
            return dt
        return dt + (900 - float(dt) % 900) / 86400

    @property
    @memoize
    def default_datetime(self):
        ''' Return the default date (the requested one or now)

        The request may come from several sources, e.g.:

        1. from the sidebar
        2. from the calendar month view
        3. from the calendar day and week views

        Each of this cases may have a date parameter in different formats.
        We try to convert it to a DateTime.
        '''
        requested_date = self.request.get('date', '')
        # The requeste_date, when called by the calendar day and week view,
        # will look like '2017-03-29T13:30:00'
        if 'T' in requested_date:
            # Strip the "T" to have the local timezone
            requested_date = requested_date.replace('T', ' ')
        else:
            # 'T' in not there, assume we have only the date in the request
            requested_date += ' 09:00'
        try:
            requested_date = ' '.join((requested_date, DateTime().localZone()))
            date = DateTime(requested_date)
        except SyntaxError:
            date = DateTime()
        return date

    @property
    @memoize
    def default_start(self):
        ''' The rounded default_datetime.
        '''
        return self.round_date(self.default_datetime)

    @property
    @memoize
    def default_end(self):
        ''' Like default_start, but add a time interval (in hours)

        We will have a 'T' in the request parameter
        if the request comes from the day or the week calendar view
        '''
        delta = 'T' in self.request.get('date', '') and 0.5 or 1.
        return self.default_start + delta / 24

    @deprecate(
        'The method round_minutes has been replaced '
        'by the more powerful round_date'
    )
    def round_minutes(self, time):
        hours, minutes = time.split(":")
        if minutes != "00":
            quarters = int(minutes) / 15 + 1
            minutes = str(quarters * 15)
        if minutes == "60":
            minutes = "00"
        return hours + ":" + minutes

    def get_selection_classes(self, field, default=None):
        """ identify all groups in the invitees """
        return get_selection_classes(self.context, field, default)
