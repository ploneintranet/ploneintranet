"""
Celery tasks providing asynchronous jobs for Plone Intranet
"""
from celery import Celery
import requests

app = Celery('ploneintranet.tasks', broker='redis://localhost:6379/0')


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

    url = url + '/@@convert-document'
    resp = requests.post(url, params=params, cookies=cookies)
    if resp.status_code != 200:
        raise PreviewGenerationException
