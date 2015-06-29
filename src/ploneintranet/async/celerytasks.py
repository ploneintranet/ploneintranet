"""
Celery tasks providing asynchronous jobs for Plone Intranet
"""
import logging

from celery import Celery
import requests

from ploneintranet.async import celeryconfig

app = Celery('ploneintranet.tasks', broker='redis://localhost:6379/0')
app.config_from_object(celeryconfig)
logger = logging.getLogger(__name__)


class PreviewGenerationException(Exception):
    """ Raised if preview generation failed for some reason """


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
    params = {
        'action': 'add',
        'url': url
    }

    url += '/@@generate-previews'
    logger.info('Calling %s', url)
    resp = requests.post(url, data=params, cookies=cookies)
    logger.info(resp)
    if resp.status_code != 200:
        raise PreviewGenerationException
