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
import time
from celery import Celery

from ploneintranet.async import celeryconfig
from ploneintranet.async.core import dispatch

app = Celery('ploneintranet.tasks',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/1')
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


@app.task
def generate_and_add_preview(url, data={}, headers={}, cookies={}):
    """
    Make an HTTP request to the DocConv Plone instance to generate a preview
    for the given object URL and add it to the object.

    See utils.dispatch() for interface contract.
    """
    dispatch(url, data, headers, cookies)


@app.task
def reindex_object(url, data={}, headers={}, cookies={}):
    """Reindex a content object.

    See utils.dispatch() for interface contract.
    """
    dispatch(url, data, headers, cookies)
