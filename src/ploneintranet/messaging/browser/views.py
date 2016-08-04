# coding=utf-8
from datetime import timedelta
import logging
import urllib
from AccessControl import Unauthorized
from plone import api
from ploneintranet import api as pi_api
from plone.protect.utils import safeWrite
from Products.CMFPlone.utils import safe_unicode
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

    def __init__(self, context, request):
        super(AppMessagingView, self).__init__(context, request)
        self.userid = None

    def publishTraverse(self, request, name):
        userid = urllib.unquote(name)
        if isinstance(name, unicode):
            self.userid = userid
        else:
            self.userid = userid.decode('utf8')
        # stop traversing, we have arrived
        request['TraversalRequestNameStack'] = []
        # return self so the publisher calls this view
        return self

    def __call__(self):
        if api.user.is_anonymous():
            raise Unauthorized("You must be logged in to use messaging.")
        self.update()
        return self.index()

    def update(self):
        if self.userid:
            conversation = pi_api.messaging.get_conversation(self.userid)
            if conversation.new_messages_count > 0:
                conversation.mark_read()
                # this is a valid write-on-read
                safeWrite(conversation, self.request)
                # the write propagates to all children messages
                for message in conversation.get_messages():
                    safeWrite(message, self.request)
                # the write also propagates to parent inbox
                safeWrite(conversation.__parent__, self.request)

    def conversations(self):
        inbox = pi_api.messaging.get_inbox()
        _conversations = []
        for userid in inbox.keys():
            conversation = inbox[userid]
            if userid == self.userid:
                status = 'current'
            elif conversation.new_messages_count > 0:
                status = 'unread'
            else:
                status = ''
            if conversation.last:
                byline = conversation.last.text
            else:
                byline = '...'
            _conversations.append(
                dict(
                    userid=userid,
                    status=status,
                    byline=byline,
                    fullname=self._fullname(userid),
                    chat_url=self._chat_url(userid),
                    avatar_url=self._avatar_url(userid)
                )
            )
        return _conversations

    def messages(self):
        conversation = pi_api.messaging.get_conversation(self.userid)
        _messages = []
        _last = None
        _maxdiff = timedelta(minutes=15)
        for msg in conversation.get_messages():
            # add time header if more than 15m since previous msg
            if not _last or msg.created > _last + _maxdiff:
                _messages.append(dict(
                    type='date',
                    status='',
                    timestamp=self._format_created(msg.created)
                ))
            _last = msg.created
            status = msg.sender == self.userid and 'self' or ''
            _messages.append(dict(
                type='text',
                status=status,
                userid=msg.sender,
                text=msg.text,
                fullname=self._fullname(msg.sender),
                avatar_url=self._avatar_url(msg.sender)
            ))
        return _messages

    def _fullname(self, userid):
        return userid

    def _chat_url(self, userid):
        portal_url = api.portal.get().absolute_url()
        return '{}/@@app-messaging/{}'.format(
            portal_url,
            urllib.quote(safe_unicode(userid))
        )

    def _avatar_url(self, userid):
        return pi_api.userprofile.avatar_url(userid)

    def _format_created(self, created):
        """Format the stored UTC datetime into local time."""
        return self.context.toLocalizedTime(created, long_format=1)


class AppMessagingNewChat(BrowserView):
    """
    Panel helper to create a new conversation.
    """

    # /prototype/_site/apps/messages/panel-new-chat.html

    def update(self):
        pass

    def __call__(self):
        if api.user.is_anonymous():
            raise Unauthorized("You must be logged in to use messaging.")
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
        if api.user.is_anonymous():
            raise Unauthorized("You must be logged in to use messaging.")
        self.update()
        return self.index()
