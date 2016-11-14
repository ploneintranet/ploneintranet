# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity import content
from plone.directives import form
from plone.uuid.interfaces import IUUID
from zope.interface import implements, Attribute
from zope import schema

from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.app import AbstractAppContainer, IApp, App
from ploneintranet.layout.interfaces import IAppContainer
from ploneintranet.news.browser.interfaces import INewsLayer, INewsContentLayer


import logging
log = logging.getLogger(__name__)


class INewsApp(IApp, IAppContainer):
    """Toplevel News singleton to contain all news content (IAppContainer)
    that also provides an IApp tile in the apps listing.
    """


class INewsSection(form.Schema):
    """News Sections can contain News Items"""

    uuid = Attribute("Stable unique id")

    section_visible = schema.Bool(
        title=_('section_visible', u'Section visible'),
        description=_(
            'description_section_visible',
            u'Show this section in the section navigation'),
        required=False,
        default=True)

    description_visible = schema.Bool(
        title=_('description_visible', u'Description visible'),
        description=_(
            'description_description_visible',
            u'Show the section description on the section page'),
        required=False,
        default=True)


class NewsApp(AbstractAppContainer, content.Container, App):
    implements(INewsApp, IAppContainer)

    # IAppContainer
    app_name = "news"
    app_layers = (INewsLayer, INewsContentLayer)

    # IApp
    app = 'publisher'  # bloody awkward API in ploneintranet.layout
    css_class = 'news'
    devices = 'desktop tablet'

    def sections(self):
        contentFilter = dict(portal_type="ploneintranet.news.section")
        return self.listFolderContents(contentFilter=contentFilter)

    def news_items(self, section=None, start=None, limit=None, getObject=True,
                   **query):
        query['portal_type'] = "News Item"
        if section:
            query['section_uuid'] = section.uuid
        if 'sort_on' not in query:
            query['sort_on'] = 'effective'
            query['sort_order'] = 'reverse'
        items = api.portal.get_tool('portal_catalog')(**query)
        if start and limit:
            sliced = items[start:limit]
        elif start:
            sliced = items[start:]
        elif limit:
            sliced = items[:limit]
        else:
            sliced = items
        if getObject:
            return [x.getObject() for x in sliced]
        else:
            return sliced


class NewsSection(content.Item):
    implements(INewsSection)

    @property
    def uuid(self):
        return IUUID(self)
