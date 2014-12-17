from .base_view import BaseView
from ..interfaces import LIKE


class ToggleLike(BaseView):

    def __call__(self):
        is_liked = self.util.query(
            self.current_user_id,
            LIKE,
            self.content_uid,
            ignore_completed=False
        )
        if len(is_liked) == 0:
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
