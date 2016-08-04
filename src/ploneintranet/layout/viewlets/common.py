# coding=utf-8
from plone.app.layout.viewlets import common
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ISiteSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility


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
        super(LogoViewlet, self).update()
