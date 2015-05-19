from __future__ import print_function

# import uuid
import json

import requests
import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.gen
import redis
import tornadoredis
import tornadoredis.pubsub

try:
    import sockjs.tornado
except:
    print('Please install the sockjs-tornado package to run this demo.')
    exit(1)


# Use the synchronous redis client to publish messages to a channel
redis_client = redis.Redis()
# Create the tornadoredis.Client instance
# and use it for redis channel subscriptions
subscriber = tornadoredis.pubsub.SockJSSubscriber(tornadoredis.Client())


class IndexPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("template.html", title="PubSub + SockJS Demo")


class SendMessageHandler(tornado.web.RequestHandler):
    def _send_message(self, channel, msg_type, msg, user=None):
        msg = {'type': msg_type,
               'msg': msg,
               'user': user}
        msg = json.dumps(msg)
        redis_client.publish(channel, msg)

    def post(self):
        message = self.get_argument('message')
        from_user = self.get_argument('from_user')
        to_user = self.get_argument('to_user')
        if to_user:
            self._send_message('private.{}'.format(to_user),
                               'pvt', message, from_user)
            self._send_message('private.{}'.format(from_user),
                               'tvp', message, to_user)
        else:
            self._send_message('broadcast_channel', 'msg', message, from_user)
        self.set_header('Content-Type', 'text/plain')
        self.write('sent: %s' % (message,))


class MessageHandler(sockjs.tornado.SockJSConnection):
    """
    SockJS connection handler.

    Note that there are no "on message" handlers - SockJSSubscriber class
    calls SockJSConnection.broadcast method to transfer messages
    to subscribed clients.
    """

    def _enter_leave_notification(self, msg_type):
        broadcasters = list(subscriber.subscribers['broadcast_channel'].keys())
        message = json.dumps({'type': msg_type,
                              'user': self.user_id,
                              'msg': '',
                              'user_list': [{'id': b.user_id}
                                            for b in broadcasters]})
        if broadcasters:
            broadcasters[0].broadcast(broadcasters, message)

    def _send_message(self, msg_type, msg, user=None):
        if not user:
            user = self.user_id
        self.send(json.dumps({'type': msg_type,
                              'msg': msg,
                              'user': user}))

    def on_open(self, request):
        ac = request.cookies.get('__ac', None)
        if ac is None:
            ac = ''
        else:
            ac = ac.value
        cookie = {
            '__ac': ac
        }
        resp = requests.get(
            'http://localhost:8080/Plone/check-auth',
            cookies=cookie)
        if resp.status_code == 403:
            self.close()
        # Generate a user ID and name to demonstrate 'private' channels
        # self.user_id = str(uuid.uuid4())[:5]
        # Repsonse text should now have only the user id:
        self.user_id = resp.text
        # Subscribe to 'broadcast' and 'private' message channels
        subscriber.subscribe(['broadcast_channel',
                              'private.{}'.format(self.user_id)],
                             self)
        # Send the 'user enters the chat' notification
        self._enter_leave_notification('enters')

    def on_close(self):
        subscriber.unsubscribe('private.{}'.format(self.user_id), self)
        subscriber.unsubscribe('broadcast_channel', self)
        # Send the 'user leaves the chat' notification
        self._enter_leave_notification('leaves')


application = tornado.web.Application(
    [(r'/', IndexPageHandler),
     (r'/send_message', SendMessageHandler)] +
    sockjs.tornado.SockJSRouter(MessageHandler, '/sockjs').urls)

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    print('Demo is running at 0.0.0.0:8888\n'
          'Quit the demo with CONTROL-C')
    tornado.ioloop.IOLoop.instance().start()
