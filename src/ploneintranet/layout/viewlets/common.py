# coding=utf-8
from plone.app.layout.viewlets import common
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ISiteSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from ploneintranet.workspace.utils import in_workspace


class GlobalSectionsViewlet(common.GlobalSectionsViewlet):

    def update(self):
        super(GlobalSectionsViewlet, self).update()
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema,
                                         prefix="plone",
                                         check=False)
        self.logo_title = settings.site_title


class LogoViewlet(common.LogoViewlet):

    index = ViewPageTemplateFile('logo.pt')

    def update(self):
        # This implements the following directive from proto:
        # The href of the link below is variable. When in a workspaces it
        # points to the workspaces overview, when in an app it points to the
        # apps overview and for other situations to the dashboard.

        # XXX to be done: add `in_app` util check and respective rule
        super(LogoViewlet, self).update()
        if in_workspace(self.context):
            self.logo_url = "{0}/workspaces".format(self.navigation_root_url)
        else:
            self.logo_url = self.navigation_root_url
