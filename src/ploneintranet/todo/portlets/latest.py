# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.component import getUtility
from zope import schema
from plone import api
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.app.portlets.cache import render_cachekey
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ..interfaces import ITodoUtility
from ..interfaces import MUST_READ
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa


class ILatest(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=5)


@implementer(ILatest)
class Assignment(base.Assignment):

    def __init__(self, count=5):
        self.count = count

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u'Latest news')


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('latest.pt')

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    def latest_news(self):
        return [b.getObject() for b in self._data()]

    @memoize
    def _data(self):
        todos = getUtility(ITodoUtility)
        current_user = api.user.get_current()
        latest = todos.query(
            userids=[current_user.getId()],
            verbs=[MUST_READ],
            sort_on='created',
            sort_order='reverse'
        )
        limit = self.data.count
        contents = []
        for action in latest[:limit]:
            # Maybe it is better to have a catalog brain here?
            content = uuidToCatalogBrain(action.content_uid)
            contents.append(content)
        return contents


class AddForm(base.AddForm):

    schema = ILatest
    label = _(u'Add latest news portlet')
    description = _(
        u'This portlet displays the latest news that must be read.'
    )

    def create(self, data):
        return Assignment(count=data.get('count', 5))


class EditForm(base.EditForm):

    schema = ILatest
    label = _(u'Edit latest news portlet')
    description = _(
        u'This portlet displays the latest news that must be read.'
    )
