# coding=utf-8
import logging
from Products.Five.browser import BrowserView

from ploneintranet.microblog.browser.tiles.newpostbox import AbstractNewPostBox

logger = logging.getLogger(__name__)


class PostWellDoneView(AbstractNewPostBox, BrowserView):
    '''
    Helper view that handles HTTP POST of update-social
    and renders a new update-social + the created post
    for injection back into the calling view.
    '''
