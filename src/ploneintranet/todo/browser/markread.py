from .todo_view import BaseView
from ..interfaces import MUST_READ


class MarkRead(BaseView):

    def __call__(self):
        self.util.complete_action(
            content_uid=self.content_uid,
            verb=MUST_READ,
            userids=self.current_user_id
        )
