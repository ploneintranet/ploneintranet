# coding=utf-8
import logging
import urllib
from plone import api
from ploneintranet import api as pi_api
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

    def conversations(self):
        fake = [
            dict(userid='allan_neece',
                 status='unread',
                 byline='Foo the bar'),
            dict(userid='alice_lindstrom',
                 status='',
                 byline='Nix the nought'),
            dict(userid='guy_hackey',
                 status='',
                 byline='...')
        ]
        for x in fake:
            if x['userid'] == self.userid:
                x['status'] = 'current'
            x['fullname'] = self._fullname(x['userid'])
            x['chat_url'] = self._chat_url(x['userid'])
            x['avatar_url'] = self._avatar_url(x['userid'])
        return fake

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

    def messages(self):
        fake = [
            dict(type='date',
                 status='',
                 timestamp='20 June 2016, 14:32'),
            dict(type='text',
                 status='self',
                 userid='guido_stevens',
                 message='Whatever. Wherever.'),
            dict(type='text',
                 status='',
                 userid='alice_lindstrom',
                 message='Seriously? Today?'),
            dict(type='date',
                 status='',
                 timestamp='21 June 2016, 11:23'),
            dict(type='text',
                 status='self',
                 userid='guido_stevens',
                 message='Ping?'),
            dict(type='text',
                 status='',
                 userid='alice_lindstrom',
                 message='Pong!'),
        ]
        for x in fake:
            if x['type'] == 'text':
                x['fullname'] = self._fullname(x['userid'])
                x['avatar_url'] = self._avatar_url(x['userid'])
        return fake


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
