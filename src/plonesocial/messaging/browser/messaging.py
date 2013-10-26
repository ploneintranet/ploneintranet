import datetime
import json

from Products.Five.browser import BrowserView

from plone import api

from plone.z3cform.fieldsets import extensible
from z3c.form import form, field, button

from zope.component import getUtility
from zope.i18nmessageid import MessageFactory

from plonesocial.messaging.interfaces import IMessage, IMessagingLocator

_ = MessageFactory('plonesocial.microblog')


class MessageForm(extensible.ExtensibleForm, form.Form):

    ignoreContext = True  # don't use context to get widget data
    id = None
    label = _(u"Add a comment")
    fields = field.Fields(IMessage).select('recipient', 'text')

    def updateActions(self):
        super(MessageForm, self).updateActions()
        self.actions['send'].addClass("standalone")

    @button.buttonAndHandler(_(u'label_sendmessage',
                               default=u"Send Message"),
                               name='send')
    def handleMessage(self, action):

        # Validation form
        data, errors = self.extractData()
        if errors:
            return

        sender = api.user.get_current()
        recipient = api.user.get(username=data['recipient'])
        assert sender and recipient, 'nope'

        locator = getUtility(IMessagingLocator)
        inboxes = locator.get_inboxes()

        inboxes.send_message(sender.id, recipient.id, data['text'])

        # Redirect to portal home
        self.request.response.redirect(self.action)

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        pass


class DateTimeJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super(DateTimeJSONEncoder, self).default(obj)


class JsonView(BrowserView):

    def __init__(self, context, request):
        super(JsonView, self).__init__(context, request)
        self.request.response.setHeader("Content-type", "application/json")

    def dumps(self, obj):
        return json.dumps(obj, indent=4, separators=(',', ': '),
                          cls=DateTimeJSONEncoder)

    def error(self, code, message):
        self.request.response.setStatus(code, reason=message)
        response = {'error': {'code': code,
                              'reason': message}}
        return self.dumps(response)

    def success(self, obj):
        return self.dumps(obj)


class MessagingView(JsonView):

    def messages(self):
        locator = getUtility(IMessagingLocator)
        inboxes = locator.get_inboxes()
        user = api.user.get_current()
        if user is None:
            return self.error(401, 'You need to log in to access the inbox')

        conversation_user_id = self.request.form.get('user')
        if conversation_user_id is None:
            return self.error(500, 'You need to provide a parameter "user"')

        if (user.id not in inboxes or
            conversation_user_id not in inboxes[user.id]):
            return self.success([])

        conversation = inboxes[user.id][conversation_user_id]
        messages = [message.to_dict() for message in
                    conversation.get_messages()]
        result = {'messages': messages}
        return self.success(result)
