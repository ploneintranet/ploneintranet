"""
Tornado based websocket server for Plone Intranet
"""
import requests
from tornado import websocket
import tornado
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application
import tornadoredis


class PushMessageWebSocket(websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(PushMessageWebSocket, self).__init__(*args, **kwargs)
        self.listen()
        self.client = None

    def check_origin(self, origin):
        # TODO: Do we need to check origin?
        return True

    @tornado.gen.engine
    def listen(self):
        self.client = tornadoredis.Client()
        self.client.connect()
        yield tornado.gen.Task(self.client.subscribe, 'test_channel')
        self.client.listen(self.on_message)

    def on_message(self, msg):
        if getattr(msg, 'kind', None) is None:
            return
        if msg.kind == 'message':
            self.write_message(str(msg.body))
        if msg.kind == 'disconnect':
            # Do not try to reconnect, just send a message back
            # to the client and close the client connection
            self.write_message('The connection terminated '
                               'due to a Redis server error.')
            self.close()

    def on_close(self):
        if self.client and self.client.subscribed:
            self.client.unsubscribe('test_channel')
            self.client.disconnect()
        print "WebSocket closed"

    def open(self):
        resp = requests.get('http://localhost:8080/Plone/check-auth',
                            cookies={'__ac': self.get_cookie('__ac')})
        if resp.status_code == 403:
            self.close(403, 'Not authorised')
        print "WebSocket opened"


application = Application([
    (r'/ws', PushMessageWebSocket),
])

if __name__ == "__main__":
    http_server = HTTPServer(application)
    http_server.listen(8888)
    IOLoop.instance().start()
