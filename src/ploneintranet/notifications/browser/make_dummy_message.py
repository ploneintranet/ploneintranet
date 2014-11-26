# -*- coding: utf-8 -*-
# from AccessControl import Unauthorized
# from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
# from ploneintranet.notifications.channel import AllChannel
from ploneintranet.notifications.message import create_message
from ploneintranet.notifications.msg_classes import fake_adapter


class MakeDummyMessageView(BrowserView):
    # TODO REMOVE ME dummy only

    # This may be overridden in ZCML
    index = ViewPageTemplateFile("make_dummy_message.pt")

    def render(self):
        return self.index()

    def __call__(self):
        if not self.request.get('REQUEST_METHOD', 'GET').upper() == 'POST':
            return self.render()

        # make a dummy message to all for now
        user = api.user.get_current()

        predicate = 'GLOBAL_NOTICE'
        portal = api.portal.get()

        # users = ['test0', 'test1', 'test2', 'test3', 'test4']

        dummy_title = self.request.get('dummy_title', 'Im a message title')
        # Step 1, something creates a bunch of messages
        actor = dict(fullname=user.getProperty('fullname'),
                     userid=user.getUserId(),
                     email='join@test.com')
        obj = {'id': portal.id,
               'url': portal.absolute_url(relative=True),
               'title': dummy_title}
        msg = create_message([actor], predicate, obj)

        # This should be an adapter
        msg_class_handler = fake_adapter(predicate)
        msg_class_handler.add(msg)
        return self.render()

