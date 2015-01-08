# -*- coding: UTF-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ploneintranet.todo import _
from ploneintranet.todo.browser.base_view import BaseView
from ploneintranet.todo.interfaces import LIKE
from random import randrange


class ToggleLike(BaseView):

    index = ViewPageTemplateFile('templates/toggle_like.pt')

    def __call__(self):
        user_likes = self.util.query(
            self.current_user_id,
            LIKE,
            self.content_uid,
            ignore_completed=False
        )
        self.is_liked = bool(user_likes)

        # toogle like only if the button is clicked
        if 'like_button' in self.request:
            if not self.is_liked:
                self.util.add_action(
                    self.content_uid,
                    LIKE,
                    self.current_user_id,
                    completed=True
                )
            else:
                self.util.remove_action(
                    self.content_uid,
                    LIKE,
                    self.current_user_id
                )
            self.is_liked = not self.is_liked

        if self.is_liked:
            self.verb = _(u'Unlike')
        else:
            self.verb = _(u'Like')

        return self.index()

    def unique_id(self):
        # TODO: Is there a bestter solution for having unique css-id's
        return randrange(100000, 999999)

    def total_likes(self):
        likes = self.util.query(
            verbs=LIKE,
            content_uids=self.content_uid,
            ignore_completed=False
        )
        return len(likes)
