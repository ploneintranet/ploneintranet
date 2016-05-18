# -*- coding: utf-8 -*-
from DateTime import DateTime
from datetime import datetime
from plone import api
from plone.app.event.base import default_timezone
from plone.i18n.normalizer import idnormalizer
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.basecontent.utils import dexterity_update
from ploneintranet.workspace.basecontent.utils import get_selection_classes
from ploneintranet.workspace.config import TEMPLATES_FOLDER
from ploneintranet.workspace.unrestricted import execute_as_manager
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

    def redirect(self, url):
        """
        Has its own method to allow overriding
        """
        url = '{}/view'.format(url)
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

    def __call__(self, portal_type='', title=None):
        """Evaluate form and redirect"""
        if title is not None:
            self.portal_type = portal_type.strip()
            self.title = title.strip()
            if self.portal_type in api.portal.get_tool('portal_types'):
                url = self.create()
                return self.redirect(url)
        return self.template()


class AddWorkspace(AddBase):
    """
    Evaluate simple form and add arbitrary content.
    """
    TEMPLATES_FOLDER = TEMPLATES_FOLDER

    # BBB: this hardcoded class attributes should be dynamic properties
    # I see two possible way:
    # 1. Generic setup: store the information in the portal_type definition xml
    # 2. Portal_registry: add two properties
    # If it is easy I would go for 1.
    types_with_template = (
        'ploneintranet.workspace.case',
        'ploneintranet.workspace.workspacefolder',
    )
    types_with_policy = (
        'ploneintranet.workspace.workspacefolder',
    )

    def get_template(self):
        ''' Get a template to copy
        '''
        template_id = self.request.get(
            '%s-template_id' % self.portal_type
        )
        if not template_id:
            return
        portal = api.portal.get()
        template_folder = portal.get(self.TEMPLATES_FOLDER)
        if not template_folder:
            return
        # Here we do a catalog query deliberately. Users should only see
        # a template if they are actually allowed to by the set permissions
        # src = template_folder.get(template_id)
        src = template_folder.getFolderContents({'getId': template_id})
        if not src:
            return
        return src[0].getObject()

    def create_from_template(self):
        ''' Create an ocject with the given template
        '''
        template = self.get_template()
        if not template:
            api.portal.show_message(
                _('Please specify which Case Template to use'),
                request=self.request,
                type="error",
            )
            return

        # need privilege escalation since normal users do not
        # have View permission on case templates
        # - that only comes after the template has been turned
        # into an actual case with member users
        new = execute_as_manager(
            api.content.copy,
            source=template,
            target=self.context,
            id=self.get_new_unique_id(),
            safe_id=False,
        )
        new.creation_date = datetime.now()
        return new

    def get_new_object(self):
        ''' This will create a new object
        '''
        if (
            self.portal_type in self.types_with_template and
            self.request.form.get('%s-template_id' % self.portal_type)
        ):
            return self.create_from_template()
        return super(AddWorkspace, self).get_new_object()

    def set_workspace_policy(self, obj):
        ''' Set's the workspace policy for the objects given a scenario
        '''
        form = self.request.form
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

            obj.set_external_visibility(external_visibility)
            obj.join_policy = join_policy
            obj.participant_policy = participant_policy

    def update(self, obj):
        ''' Update the object and returns the modified fields and errors
        '''
        if self.portal_type in self.types_with_policy:
            self.set_workspace_policy(obj)
        return super(AddWorkspace, self).update(obj)


class AddFolder(AddBase):

    template = ViewPageTemplateFile('templates/add_folder.pt')


class AddTask(AddBase):

    template = ViewPageTemplateFile('templates/add_task.pt')

    def redirect(self, url):
        workspace = parent_workspace(self.context)
        return self.request.response.redirect(workspace.absolute_url())


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

    def get_selection_classes(self, field, default=None):
        """ identify all groups in the invitees """
        return get_selection_classes(self.context, field, default)
