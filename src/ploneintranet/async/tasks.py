"""
Celery tasks providing asynchronous jobs for Plone Intranet
"""
from celery.task import task
import requests


class PreviewGenerationException(Exception):
    """ Raised if preview generation failed for some reason """


@task
def generate_and_add_preview(url, cookie):
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
    resp = requests.get('http://localhost:8000/@@generate-preview',
                        params=params,
                        cookies=cookie)
    if resp.status_code != 200:
        raise PreviewGenerationException
