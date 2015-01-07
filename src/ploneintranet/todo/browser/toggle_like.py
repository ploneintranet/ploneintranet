from .base_view import BaseView
from ..interfaces import LIKE
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ToggleLike(BaseView):

    index = ViewPageTemplateFile('templates/toggle_like.pt')

    def __call__(self):
        is_liked = self.util.query(
            self.current_user_id,
            LIKE,
            self.content_uid,
            ignore_completed=False
        )
        if len(is_liked) == 0:
            self.verb = 'Like'
        else:
            self.verb = 'Unlike'

        # toogle like only if the button is clicked
        if 'like_button' in self.request:
            if not is_liked:
                self.util.add_action(
                    self.content_uid,
                    LIKE,
                    self.current_user_id,
                    completed=True
                )
            elif is_liked:
                self.util.remove_action(
                    self.content_uid,
                    LIKE,
                    self.current_user_id
                )
        return self.index()
