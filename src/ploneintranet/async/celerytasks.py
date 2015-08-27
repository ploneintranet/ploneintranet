"""
Celery tasks providing asynchronous jobs for Plone Intranet
"""
import logging
import time
from celery import Celery
import requests

from ploneintranet.async import celeryconfig

app = Celery('ploneintranet.tasks',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/1')
app.config_from_object(celeryconfig)
logger = logging.getLogger(__name__)


class AsyncDispatchError(Exception):
    """Raised if async dispatch fails"""


def dispatcher(url, cookies, data={}):
    """
    This is not a task but a building block for tasks.

    Delegate a URL call via celery,
    preserving the original authentication so that
    async tasks get executed with the same security
    as the user initiating the dispatch.

    There is no result or callback, the assumption is that results
    are committed to the ZODB by the view called on `url`.

    DO NOT BYPASS CSRF FOR ACTUAL BUSINESS OBJECT WRITES like file previews.
    Instead, include a proper authenticator in the POST `data`.
    See https://pypi.python.org/pypi/plone.protect

    :param url: URL to be called by celery, resolvable behind
                the webserver (i.e. localhost:8080/Plone/path/to/object)
    :type url: str
    :param cookie: The original request's user's cookie `{'__ac': 'ABC123'}`
    :type cookie: dict
    :param data: additional POST variables to pass through to the url
    :type data: dict

    """
    logger.info('Calling %s', url)
    resp = requests.post(url, data=data, cookies=cookies)
    logger.info(resp)
    if resp.status_code != 200:
        raise AsyncDispatchError


@app.task
def dispatch(url, cookies, data={}):
    """
    Generic url dispatch task leveraging `dispatcher`.

    :param url: URL to be called by celery, resolvable behind
                the webserver (i.e. localhost:8080/Plone/path/to/object)
    :type url: str
    :param cookie: The original request's user's cookie `{'__ac': 'ABC123'}`
    :type cookie: dict
    :param data: additional POST variables to pass through to the url
    :type data: dict
    """
    dispatcher(url, cookies, data)


@app.task
def generate_and_add_preview(url, cookies):
    """
    Make an HTTP request to the DocConv Plone instance to generate a preview
    for the given URL and add it to the object
    :param url: URL to the object to generate preview for, resolvable behind
                the webserver (i.e. localhost:8080/Plone/path/to/object)
    :type url: str
    :param cookie: The original request's user's cookie `{'__ac': 'ABC123'}`
    :type cookie: dict
    """
    data = {
        'action': 'add',
        'url': url
    }
    url += '/@@generate-previews'
    dispatcher(url, cookies, data)


@app.task
def add(x, y, delay=1):
    """Demo task used to test celery roundtrip"""
    time.sleep(delay)
    return x + y
