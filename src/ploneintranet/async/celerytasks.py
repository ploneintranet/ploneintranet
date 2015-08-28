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
from BeautifulSoup import BeautifulSoup
from celery import Celery
import requests

# from plone import api
from ploneintranet.async import celeryconfig

app = Celery('ploneintranet.tasks',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/1')
app.config_from_object(celeryconfig)
logger = logging.getLogger(__name__)


class AsyncDispatchError(Exception):
    """Raised if async post fails"""


@app.task
def post(url, data={}, headers={}, cookies={}):
    """
    Delegate a HTTP POST URL call via celery.
    Preserves the original authentication so that
    async tasks get executed with the same security
    as the user initiating the post.

    Returns a <class 'celery.result.AsyncResult'> when running async,
    or a <class 'celery.result.EagerResult'> when running in sync mode.

    There is callback, the assumption is that results
    are committed to the ZODB by the view called on `url`.

    DO NOT BYPASS CSRF FOR ACTUAL BUSINESS OBJECT WRITES like file previews.
    Instead, use the plone.protect support in ploneintranet.async.tasks.
    See https://pypi.python.org/pypi/plone.protect

    :param url: URL to be called by celery, resolvable behind
                the webserver (i.e. localhost:8080/Plone/path/to/object)
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


def dispatch(url, data={}, headers={}, cookies={}):
    """
    This is not a task but a building block for tasks.

    See post() for interface contract.
    """
    logger.info('Calling %s', url)
    logger.info('headers: %s' % str(headers))
    logger.info('data: %s' % str(data))
    resp = requests.post(url,
                         headers=headers,
                         cookies=cookies,
                         data=data)
    logger.info(resp)
    if resp.status_code != 200:
        logger.error("Invalid response %s: %s", resp.status_code, resp.reason)
        if 'error has been logged' in resp.text:
            errcode = BeautifulSoup(resp.text).code.string
            logger.error(
                "Error logged in {portal_url}/error_log/showEntry?id=%s",
                errcode)
    elif 'login_form' in resp.text:
        logger.error("Unauthorized (masked as 200 OK)")
    else:
        logger.info("%s: %s", resp.status_code, resp.reason)
        logger.info(resp.text)


@app.task
def generate_and_add_preview(url, data={}, headers={}, cookies={}):
    """
    Make an HTTP request to the DocConv Plone instance to generate a preview
    for the given object URL and add it to the object.

    See post() for interface contract.
    """
    dispatch(url, data, headers, cookies)


@app.task
def add(x, y, delay=1):
    """Non-http lowlevel task used to test celery roundtrip"""
    time.sleep(delay)
    return x + y
