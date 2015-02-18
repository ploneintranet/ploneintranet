# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.protect import CheckAuthenticator, PostOnly


class AddContent(BrowserView):
    """Evaluate simple form and add arbitrary content.
    """

    template = ViewPageTemplateFile('templates/add_content.pt')

    def __call__(self, portal_type=None, title=None, description=None):
        """Evaluate form and redirect"""
        if title is not None:
            CheckAuthenticator(self.request)
            PostOnly(self.request)
            self.portal_type = portal_type
            self.title = title.strip()
            self.description = description.strip()
            if self.portal_type in api.portal.get_tool('portal_types'):
                url = self.create()
                return self.redirect(url)
        return self.template()

    def create(self):
        """Create content and return url"""
        container = self.context
        new = api.content.create(
            container=container,
            type=self.portal_type,
            title=self.title,
            safe_id=True,
        )
        if new:
            new.description = safe_unicode(self.description)
            return new.absolute_url()

    def redirect(self, url):
        """Has its own method to allow overriding"""
        url = '{}/edit'.format(url)
        return self.request.response.redirect(url)


class AddFolder(AddContent):

    template = ViewPageTemplateFile('templates/add_folder.pt')

    def redirect(self, url):
        """redirect to view"""
        return self.request.response.redirect(url)
