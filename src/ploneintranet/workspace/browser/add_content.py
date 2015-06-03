# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from ploneintranet.theme import _
from ploneintranet.theme.utils import dexterity_update
from ploneintranet.workspace.utils import parent_workspace
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class AddContent(BrowserView):
    """Evaluate simple form and add arbitrary content.
    """

    template = ViewPageTemplateFile('templates/add_content.pt')

    def __call__(self, portal_type=None, title=None):
        """Evaluate form and redirect"""
        if title is not None:
            self.portal_type = portal_type
            self.title = title.strip()
            if self.portal_type in api.portal.get_tool('portal_types'):
                url = self.create()
                return self.redirect(url)
        return self.template()

    def create(self):
        """Create content and return url. Uses dexterity_update to set the
        appropriate fields after creation.
        """
        container = self.context
        new = api.content.create(
            container=container,
            type=self.portal_type,
            title=self.title,
            safe_id=True,
        )

        if new:
            modified, errors = dexterity_update(new)
            if modified and not errors:
                api.portal.show_message(
                    _("Item created."), request=self.request, type="success")
                new.reindexObject()
                notify(ObjectModifiedEvent(new))

            if errors:
                api.portal.show_message(
                    _("There was an error."),
                    request=self.request,
                    type="error",
                )

            return new.absolute_url()

    def redirect(self, url):
        """Has its own method to allow overriding"""
        url = '{}/view'.format(url)
        return self.request.response.redirect(url)


class AddFolder(AddContent):

    template = ViewPageTemplateFile('templates/add_folder.pt')


class AddEvent(AddContent):

    template = ViewPageTemplateFile('templates/add_event.pt')

    def redirect(self, url):
        workspace = parent_workspace(self.context)
        return self.request.response.redirect(workspace.absolute_url() +
                                              '#workspace-events')
