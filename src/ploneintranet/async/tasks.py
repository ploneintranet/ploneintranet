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
    """Raised if async post fails"""


@app.task
def post(url, data={}, headers={}, cookies={}):
    """
    Delegate a HTTP POST URL call via celery.
    Preserves the original authentication so that
    async tasks get executed with the same security
    as the user initiating the post.

    There is no result or callback, the assumption is that results
    are committed to the ZODB by the view called on `url`.

    DO NOT BYPASS CSRF FOR ACTUAL BUSINESS OBJECT WRITES like file previews.
    Instead, include a proper authenticator in the POST `data`.
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
    if not url.startswith('http'):
        url = "%s/%s" % ('http://localhost:8081/Plone', url)
    logger.info('Calling %s', url)
    resp = requests.post(url,
                         headers=headers,
                         cookies=cookies,
                         data=data)
    logger.info(resp)
    if resp.status_code != 200:
        logger.error("invalid response %s: %s", resp.status_code, resp.reason)
    elif 'login_form' in resp.text:
        logger.error("Unauthorized (masked as 200 OK)")
    else:
        logger.info("%s: %s", resp.status_code, resp.reason)


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
    dispatch(url, cookies, data)


@app.task
def add(x, y, delay=1):
    """Demo task used to test celery roundtrip"""
    time.sleep(delay)
    return x + y
