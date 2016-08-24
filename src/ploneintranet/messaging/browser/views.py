# coding=utf-8
from AccessControl import Unauthorized
from datetime import datetime
from datetime import timedelta
from plone import api
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from plone.protect.utils import safeWrite
from ploneintranet import api as pi_api
from ploneintranet.layout.app import apps_container_id
from ploneintranet.layout.interfaces import IAppView
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from unidecode import unidecode
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
import logging
import pytz
import urllib


logger = logging.getLogger(__name__)

# switch recurrent polling on/off
AUTOREFRESH = True


class _AppMessagingMixin(object):

    app_name = 'messaging'

    @property
    def portal_url(self):
        return api.portal.get().absolute_url()

    @property
    def counter(self):
        try:
            return pi_api.messaging.get_inbox().new_messages_count
        except KeyError:
            return 0

    @property
    @memoize_contextless
    def app_url(self):
        portal = api.portal.get()
        apps_container = getattr(portal, apps_container_id)
        return apps_container.messages.absolute_url()


@implementer(IPublishTraverse, IAppView)
class AppMessagingView(BrowserView, _AppMessagingMixin):
    """
    Render a single conversation, with the chatlist in the sidebar.
    Uses traversal: @@app-messaging-chat/userid to extract the userid.
    """

    # ~/prototype/_site/chat-guido-stevens.html

    autorefresh = AUTOREFRESH

    def __init__(self, context, request):
        super(AppMessagingView, self).__init__(context, request)
        self.userid = None
        self.inbox = None
        self.only_new = False

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
        self.only_new = self.request.get('only_new', False)
        self.update()
        html = self.index()
        self.post_process()
        return html

    def update(self):
        # mark read on initial full load, not on incremental update
        if self.userid and not self.only_new:
            self.mark_read(self.userid)
        new_userid = self.request.get('new_userid', None)
        if new_userid:
            self.create_conversation(new_userid)
            self.userid = new_userid  # render the new (empty) chat panel

    def post_process(self):
        # execute mark_read *after* updated page has rendered
        if self.userid and self.only_new:
            self.mark_read(self.userid)

    def mark_read(self, userid):
        conversation = pi_api.messaging.get_conversation(userid)
        if conversation.new_messages_count > 0:
            conversation.mark_read()
            # this is a valid write-on-read
            safeWrite(conversation, self.request)
            # the write propagates to all children messages
            for message in conversation.get_messages():
                safeWrite(message, self.request)
            # the write also propagates to parent inbox
            safeWrite(conversation.__parent__, self.request)

    def create_conversation(self, new_userid):
        if not api.user.get(new_userid):
            raise ValueError("Invalid userid: %s", new_userid)

        # maybe this user does not even have an inbox yet
        try:
            inbox = pi_api.messaging.get_inbox()
        except KeyError:
            inbox = pi_api.messaging.create_inbox()
            safeWrite(inbox, self.request)
            safeWrite(inbox.__parent__, self.request)

        # don't error out when selecting an existing conversation
        if new_userid not in inbox.keys():
            conversation = pi_api.messaging.create_conversation(new_userid)
            safeWrite(conversation, self.request)
            safeWrite(inbox, self.request)
            logger.info("%s started new conversation with %s",
                        api.user.get_current().id, new_userid)

    def conversations(self):
        try:
            inbox = pi_api.messaging.get_inbox()
        except KeyError:
            return []

        _conversations = []
        for userid in self._filter(inbox.keys()):
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
        return sorted(_conversations, key=lambda x: x['fullname'])

    def messages(self):
        conversation = pi_api.messaging.get_conversation(self.userid)
        _messages = []
        _last = None
        _maxdiff = timedelta(minutes=15)
        for msg in conversation.get_messages():
            if self.only_new and not msg.new:
                _last = msg.created
                continue
            # add time header if more than 15m since previous msg
            if not _last or msg.created > _last + _maxdiff:
                _messages.append(dict(
                    type='date',
                    status='',
                    timestamp=self._format_created(msg.created)
                ))
            _last = msg.created
            status = msg.recipient == self.userid and 'self' or ''
            _messages.append(dict(
                type='text',
                status=status,
                userid=msg.sender,
                text=msg.text,
                fullname=self._fullname(msg.sender),
                avatar_url=self._avatar_url(msg.sender)
            ))
        return _messages

    @property
    def url(self):
        return self.request['ACTUAL_URL']

    @property
    def chat_url(self):
        return '{}/@@app-messaging/{}'.format(
            self.app_url, self.userid
        )

    @property
    def delay(self):
        conversation = pi_api.messaging.get_conversation(self.userid)
        # new empty conversation?
        if not conversation.last:
            return 4000
        age = datetime.now(pytz.utc) - conversation.last.created
        if age < timedelta(seconds=60):
            return 4000
        elif age < timedelta(minutes=5):
            return 8000
        else:
            return 16000

    @memoize
    def _fullname(self, userid):
        return api.user.get(userid).getProperty('fullname')

    def _chat_url(self, userid):
        return '{0}/@@app-messaging/{1}'.format(
            self.app_url,
            urllib.quote(safe_unicode(userid))
        )

    def _avatar_url(self, userid):
        return pi_api.userprofile.avatar_url(userid)

    def _format_created(self, created):
        """Format the stored UTC datetime into local time."""
        return self.context.toLocalizedTime(created, long_format=1)

    def _filter(self, userids):
        """Apply a unicode aware fuzzy filter.

        Based on the work in ploneintranet.network.vocabularies
        """

        def safe_encode(term):
            if isinstance(term, unicode):
                # no need to use portal encoding for transitional encoding from
                # unicode to ascii. utf-8 should be fine.
                term = term.encode('utf-8')
            if term is not None:
                return term.lower()
            return term

        search = self.request.get('search', None)
        if not search or len(search) <= 1:
            return userids

        q_decode = unidecode(safe_unicode(search)).lower()
        q_encode = safe_encode(search)
        matches = set()
        for userid in userids:
            fullname = self._fullname(userid)
            if q_encode in safe_encode(userid) or \
               q_encode in safe_encode(fullname):
                matches.add(userid)
            elif q_decode and (q_decode in unidecode(userid).lower() or
                               q_decode in unidecode(fullname).lower()):
                matches.add(userid)
        return list(matches)

    def search_disabled(self):
        try:
            enabled = len(pi_api.messaging.get_inbox().keys()) > 0
        except KeyError:
            enabled = False
        if enabled:
            return ''
        else:
            return 'disabled'


@implementer(IAppView)
class AppMessagingNewChat(BrowserView, _AppMessagingMixin):
    """
    Panel helper to create a new conversation.
    """

    # /prototype/_site/apps/messages/panel-new-chat.html


@implementer(IAppView)
class AppMessagingNewMessage(BrowserView, _AppMessagingMixin):
    """
    Injection helper to add a message to a conversation.
    """

    # ~/prototype/_site/apps/messages/feedback-liz-guido.html

    def __init__(self, context, request):
        super(AppMessagingNewMessage, self).__init__(context, request)
        self.userid = None

    def __call__(self):
        if api.user.is_anonymous():
            raise Unauthorized("You must be logged in to use messaging.")
        self.update()
        return self.index()

    def update(self):
        self.userid = recipient = self.request.get('recipient')
        self.text = text = self.request.get('message')
        if recipient and text:
            pi_api.messaging.send_message(recipient, text)

    @property
    def fullname(self):
        return api.user.get_current().getProperty('fullname')

    @property
    def avatar_url(self):
        return pi_api.userprofile.avatar_url(
            api.user.get_current().id)

    def chat_url(self):
        return '{}/{}'.format(
            self.app_url, self.userid)
