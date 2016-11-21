"""
Celery tasks providing asynchronous jobs for Plone Intranet.

Don't use these tasks directly, since they are sensitive to
authentication and serialization issues.
Instead, use the wrappers provided in ploneintranet.async.tasks.

If you want to add a task, put the business logic in
ploneintranet.async.tasks and then hook that up into celery here.

Any celery task here should reference ONLY immutables.
All the tasks here should use the same interface contract as post.
"""
import logging
import os
import time
from celery import Celery

from ploneintranet.async import celeryconfig
from ploneintranet.async.core import dispatch
from ploneintranet.async.core import DispatchError
from ploneintranet.async.core import _key_for_task

broker = os.environ.get('BROKER_URL', 'redis://localhost:6379/0')
backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

app = Celery('ploneintranet.tasks',
             broker=broker,
             backend=backend)
app.config_from_object(celeryconfig)
logger = logging.getLogger(__name__)


@app.task
def add(x, y, delay=1):
    """Non-http lowlevel task used to test celery roundtrip"""
    time.sleep(delay)
    return x + y


@app.task
def post(url, data={}, headers={}, cookies={}):
    """
    Delegate a HTTP POST URL call via celery.

    Returns a <class 'celery.result.AsyncResult'> when running async,
    or a <class 'celery.result.EagerResult'> when running in sync mode.

    There is no callback, the assumption is that results
    are committed to the ZODB by the view called on `url`.

    DO NOT BYPASS CSRF FOR ACTUAL BUSINESS OBJECT WRITES like file previews.
    Instead, use the plone.protect support in ploneintranet.async.tasks.
    See https://pypi.python.org/pypi/plone.protect

    :param url: URL to be called by celery, resolvable behind
                the webserver (i.e. {portal_url}/path/to/object)
    :type url: str

    :param data: POST variables to pass through to the url
    :type data: dict

    :param headers: request headers.
    :type headers: dict

    :param cookies: request cookies. Normally contains __ac for Plone.
    :type cookies: dict
    """
    # return value comes from celery @task not from here
    dispatch(url, data, headers, cookies)


@app.task(bind=True, acks_late=True, default_retry_delay=30, max_retries=3)
def generate_and_add_preview(self, url, data={}, headers={}, cookies={}):
    """
    Make an HTTP request to the DocConv Plone instance to generate a preview
    for the given object URL and add it to the object.

    See utils.dispatch() for interface contract.

    For info on acks_late and retries, see:
    - http://docs.celeryproject.org/en/latest/faq.html#faq-acks-late-vs-retry
    - http://docs.celeryproject.org/en/latest/userguide/tasks.html#retrying
    """
    logger.info("START: generate_and_add_preview called.")
    conn = app.backend
    key = _key_for_task(url=url, task=self.name)
    counter = conn.client.get(key)
    if counter < 1:  # behave
        conn.client[key] = 1
    counter = conn.client.decr(key)
    logger.info("generate_and_add_preview: " +
                "I just decreased my key %s to %s " % (key, counter))
    if counter > 0:
        logger.info("generate_and_add_preview: Counter > 0, aborting")
        return
    try:
        logger.info("generate_and_add_preview: Counter is 0, generating now")
        dispatch(url, data, headers, cookies)
    except DispatchError as exc:
        counter = conn.client.incr(key)
        raise self.retry(exc=exc)


@app.task(bind=True, acks_late=True, default_retry_delay=10, max_retries=3)
def reindex_object(self, url, data={}, headers={}, cookies={}):
    """Reindex a content object.

    See utils.dispatch() for interface contract.

    For info on acks_late and retries, see:
    - http://docs.celeryproject.org/en/latest/faq.html#faq-acks-late-vs-retry
    - http://docs.celeryproject.org/en/latest/userguide/tasks.html#retrying
    """
    try:
        dispatch(url, data, headers, cookies)
    except DispatchError as exc:
        raise self.retry(exc=exc)


@app.task(bind=True, acks_late=True, default_retry_delay=2, max_retries=5)
def mark_read(self, url, data={}, headers={}, cookies={}):
    try:
        dispatch(url, data, headers, cookies)
    except DispatchError as exc:
        raise self.retry(exc=exc)
