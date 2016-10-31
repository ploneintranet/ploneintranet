from plone import api
from plone.dexterity import content
from plone.directives import form
from zope.interface import implements
from zope import schema

from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.app import AbstractAppContainer, IApp, App
from ploneintranet.layout.interfaces import IAppContainer
from ploneintranet.layout.utils import shorten
from ploneintranet.news.browser.interfaces import INewsLayer, INewsContentLayer


import logging
log = logging.getLogger(__name__)


class INewsApp(IApp, IAppContainer):
    """Toplevel News singleton to contain all news content (IAppContainer)
    that also provides an IApp tile in the apps listing.
    """


class INewsSection(form.Schema):
    """News Sections can contain News Items"""

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
        _sections = []
        contentFilter = dict(portal_type="ploneintranet.news.section")
        for section in self.listFolderContents(contentFilter=contentFilter):
            news_items = self.news_items(section.id)
            delete_protected = len(news_items) == 0
            _sections.append(dict(
                id=section.id,
                title=section.title,
                description=section.description,
                absolute_url=section.absolute_url(),
                delete_protected=delete_protected,
                news_items=news_items,
            ))
        if len(_sections) == 1:
            _sections[0]['delete_protected'] = True
        return _sections

    def news_items(self, section_id=None, desc_len=160):
        _items = []
        contentFilter = dict(
            portal_type="News Item",
            sort_on='effective',
            sort_order='reverse'
        )
        i = 0
        for item in self.listFolderContents(contentFilter=contentFilter):
            i += 1
            _items.append(dict(
                id=item.id,
                title=item.title,
                description=shorten(item.description, desc_len),
                absolute_url=item.absolute_url(),
                date=item.effective().strftime('%B %d, %Y'),
                category=item.section.to_object.title,
                counter=i,
                can_edit=api.user.has_permission('Modify', obj=item)
            ))
        return _items


class NewsSection(content.Item):
    implements(INewsSection)

    def news_items(self):
        return self.aq_parent.news_items(self.id)
