# -*- coding: UTF-8 -*-
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plonesocial.core.integration import PLONESOCIAL
from plonesocial.microblog.interfaces import IStatusUpdate
from plonesocial.network import _
from plonesocial.network.interfaces import ILikesContainer
from random import randrange
from zope.publisher.interfaces import IPublishTraverse
from zope.interface import implementer
from zope.component import getUtility
from plone.app.uuid.utils import uuidToCatalogBrain

import uuid


@implementer(IPublishTraverse)
class ToggleLike(BrowserView):
    """The new toggle_like_view. Mostly pseudo-code.
    """

    index = ViewPageTemplateFile('templates/toggle_like.pt')

    def __init__(self, context, request):
        self.item_id = None

    def publishTraverse(self, request, name):
        """Used for traversal via publisher, i.e. when using as a url"""
        self.item_id = name
        self.request = request
        return self

    def __call__(self):
        """ """
        self.context = api.portal.get()
        if self.item_id is None:
            raise KeyError(
                _("No item id given in sub-path."
                  "Use .../@@toggle-like/123456")
            )
        if not self.validate_id(self.item_id):
            return "No valid item-id"

        self.current_user_id = api.user.get_current().getId()
        if not self.current_user_id:
            return "No user-id"

        self.util = getUtility(ILikesContainer)

        self.is_liked = self.util.is_item_liked_by_user(
            item_id=self.item_id,
            user_id=self.current_user_id,
        )

        # toogle like only if the button is clicked
        if 'like_button' in self.request:
            if not self.is_liked:
                self.util.like(
                    item_id=self.item_id,
                    user_id=self.current_user_id,
                )
            else:
                self.util.unlike(
                    item_id=self.item_id,
                    user_id=self.current_user_id,
                )
            self.is_liked = not self.is_liked

        if self.is_liked:
            self.verb = _(u'Unlike')
        else:
            self.verb = _(u'Like')
        self.unique_id = uuid.uuid4().hex
        return self.index()

    def validate_id(self, item_id):
        """Check if item_id is a UUID or a the id of a StatusUpdate"""
        if uuidToCatalogBrain(item_id) is not None:
            return True
        else:
            # check for a StatusUpdate with this id
            container = PLONESOCIAL.microblog
            if not container:
                return False
            return item_id in container

    def total_likes(self):
        likes = self.util.get_users_for_item(
            item_id=self.item_id,
        )
        return len(likes)
