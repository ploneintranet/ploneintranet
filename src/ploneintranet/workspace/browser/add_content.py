# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.i18n.normalizer import idnormalizer
from ploneintranet.theme import _
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

    def create(self):
        """
        Create content and return url. Uses dexterity_update to set the
        appropriate fields after creation.
        """
        form = self.request.form
        new = None
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
        parts[0] = str(int(parts[0]) + 1)
        result = DateTime(date + " " + parts[0] + ":" + parts[1])
        return result

    def round_minutes(self, time):
        hours, minutes = time.split(":")
        quarters = int(minutes) / 15 + 1
        minutes = str(quarters * 15)
        if minutes == "60":
            minutes = "00"
        return hours + ":" + minutes
