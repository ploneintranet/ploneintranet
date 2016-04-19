# coding=utf-8
import logging
from plone import api

from update_social import UpdateSocialHandler

logger = logging.getLogger(__name__)


class CommentWellSaidView(UpdateSocialHandler):
    '''
    Helper view that handles HTTP POST of update-social
    and renders a new update-social + the created post
    for injection back into the calling view.
    '''

    def get_post_as_comment(self, post):
        ''' Transforms a post (aka StatusUpdate) into a renderable comment
        '''
        return api.content.get_view(
            'comment.html',
            post,
            self.request,
        )
