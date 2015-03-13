import requests
import lxml.html

from requests.exceptions import Timeout
from zope.interface import implements
from zope.component import adapts

from .interfaces import IStatusUpdate
from .interfaces import IURLPreview


class URLPreview(object):

    adapts(IStatusUpdate)
    implements(IURLPreview)

    def __init__(self, context):
        self.context = context

    def generate_preview(self, url):
        try:
            resp = requests.get(url, timeout=2)
        except Timeout:
            return []
        doc = lxml.html.fromstring(resp.content)
        links = doc.xpath('//img/@src')
        ogs = doc.xpath('//meta[@property="og:image"]/@content')
        return ogs + links
