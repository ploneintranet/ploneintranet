"""
Celery tasks providing asynchronous jobs for Plone Intranet
"""
import logging
import time
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
    """Raised if async dispatch fails"""


@app.task
def dispatch(url, auth, data={}):
    """
    Delegate a URL call via celery.
    Preserves the original authentication so that
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
    _dispatcher(url, auth, data)


def _dispatcher(url, auth, data={}):
    """
    This is not a task but a building block for tasks.

    :param url: URL to be called by celery, resolvable behind
                the webserver (i.e. localhost:8080/Plone/path/to/object)
    :type url: str
    :param cookie: The original request's user's cookie `{'__ac': 'ABC123'}`
    :type cookie: dict
    :param data: additional POST variables to pass through to the url
    :type data: dict

    """
    if not url.startswith('http'):
        url = "%s/%s" % ('http://localhost:8081/Plone', url)
    logger.info('Calling %s', url)
    resp = requests.post(url,
                         headers={"Authorization": auth},
                         data=data)
    logger.info(resp)
    if resp.status_code != 200:
        logger.error("invalid response %s: %s", resp.status_code, resp.reason)
    elif 'login_form' in resp.text:
        logger.error("Unauthorized (masked as 200 OK)")
    else:
        logger.info("%s: %s", resp.status_code, resp.reason)


class BasicAuth(object):
    """
    http://docs.python-requests.org/en/latest/user/advanced/#custom-authentication
    """  # noqa
    def __init__(self, auth):
        self.auth = auth

    def __call__(self, r):
        r.headers['Authorization'] = self.auth
        return r


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
    _dispatcher(url, cookies, data)


@app.task
def add(x, y, delay=1):
    """Demo task used to test celery roundtrip"""
    time.sleep(delay)
    return x + y
