import requests
from celery import Celery

RABBIT = 'amqp://guest@localhost//'
REDIS = 'redis://localhost:6379/0'
app = Celery(
    # 'ploneintranet.async.celerytasks.message',
    'pimessage',
    backend=REDIS,
    broker=REDIS)


@app.task(name='pimessages')
def message(user_id, msg):
    # Send message to a Plone user, via a websocket.
    print "Handling message sending task with Celery."
    payload = dict(
        message=msg,
        to_user=user_id,
        from_user='celery',
    )
    resp = requests.post(
        'http://localhost:8888/send_message',
        data=payload)
    if resp.status_code == 200:
        return "Message {} sent to {}".format(msg, user_id)
    return "ERROR {} sending message {} to {}".format(
        resp.status_code, msg, user_id)
