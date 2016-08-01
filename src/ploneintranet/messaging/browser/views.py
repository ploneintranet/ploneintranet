# coding=utf-8
import logging
from Products.Five import BrowserView
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

logger = logging.getLogger(__name__)


@implementer(IPublishTraverse)
class AppMessagingView(BrowserView):
    """
    Render a single conversation, with the chatlist in the sidebar.
    Uses traversal: @@app-messaging-chat/userid to extract the userid.
    """

    # ~/prototype/_site/chat-guido-stevens.html

    def publishTraverse(self, request, name):
        if isinstance(name, unicode):
            self.userid = name
        else:
            self.userid = name.decode('utf8')
        # stop traversing, we have arrived
        request['TraversalRequestNameStack'] = []
        # return self so the publisher calls this view
        return self


class AppMessagingNewChat(BrowserView):
    """
    Panel helper to create a new conversation.
    """

    # /prototype/_site/apps/messages/panel-new-chat.html

    def update(self):
        pass

    def __call__(self):
        if False:
            self.update()
            return self.request.response.redirect('FIXME CHAT URL')
        else:
            return self.index()


class AppMessagingNewMessage(BrowserView):
    """
    Injection helper to add a message to a conversation.
    """

    # ~/prototype/_site/apps/messages/feedback-liz-guido.html

    def update(self):
        pass

    def __call__(self):
        self.update()
        return self.index()
