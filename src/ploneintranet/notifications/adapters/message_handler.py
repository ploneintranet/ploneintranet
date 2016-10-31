# -*- coding: utf-8 -*-
from plone import api


class Base(object):
    ''' A base handler for notifications
    '''
    msg_class = 'GLOBAL_NOTICE'

    def __init__(self, context):
        self.context = context
        try:
            self.tool = api.portal.get_tool('ploneintranet_notifications')
        except api.exc.InvalidParameterError:
            self.tool = None

    def _for_each_user(self, func):
        for user in api.user.get_users():
            yield func(user)

    def g_add(self, message):
        def outer_add(tool, message):
            def inner_add(user):
                tool.append_to_user_queue(user.getUserId(), message.clone())
            return inner_add
        return self._for_each_user(outer_add(self.tool, message))

    def add(self, message):
        if not self.tool:
            # we are most likely not installed
            return
        assert message.predicate == self.msg_class, \
            'This handler is not responsible for this message, wrong predicate'
        list(self.g_add(message))

    def g_cleanup(self):
        def outer_cleanup(tool):
            def inner_cleanup(user):
                queue = tool.get_user_queue(user.getUserId())
                if not queue:
                    return

                queue = tool._users[user.getUserId()]
                for key in reversed(queue.keys()):
                    if queue[key].obj['read']:
                        queue.pop(key)

            return inner_cleanup
        return self._for_each_user(outer_cleanup(self.tool))

    def cleanup(self):
        list(self.g_cleanup())
