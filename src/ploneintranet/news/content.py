from plone.dexterity import content
from plone.directives import form
from zope.interface import implements
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

    def news_items(self, section_id=None):
        contentFilter = dict(
            portal_type="News Item",
            sort_on='effective',
            sort_order='reverse'
        )
        items = []
        for item in self.listFolderContents(contentFilter=contentFilter):
            # maintaining an index just for this would also be costly
            if section_id and item.section.to_object.id != section_id:
                continue
            items.append(item)
        return items


class NewsSection(content.Item):
    implements(INewsSection)

    def news_items(self):
        return self.aq_parent.news_items(self.id)
