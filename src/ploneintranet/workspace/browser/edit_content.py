# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.workspace.basecontent.utils import dexterity_update
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class EditFolder(BrowserView):
    """
    Evaluate simple form and edit folder.
    """

    can_edit = True  # Protected in zcml

    def __call__(self, title=None, description=None):
        """Evaluate form and redirect"""
        if title is not None or description is not None:
            url = self.edit()
            return self.redirect(url)
        return self.index()

    def edit(self):
        """
        Edit content and return url. Uses dexterity_update to set the
        appropriate fields after creation.
        """
        modified, errors = dexterity_update(self.context, self.request)
        if modified and not errors:
            api.portal.show_message(
                _("Item edited."), request=self.request, type="success")
            self.context.reindexObject()
            notify(ObjectModifiedEvent(self.context))

        if errors:
            api.portal.show_message(
                _("There was a problem: %s." % errors),
                request=self.request,
                type="error",
            )

        return self.context.absolute_url()

    def redirect(self, url):
        """
        Has its own method to allow overriding
        """
        url = '{}/view'.format(url)
        return self.request.response.redirect(url)
