# -*- coding: utf-8 -*-
from plone import api
import logging

log = logging.getLogger(__name__)


def uninstall(context):
    portal = api.portal.get()
    if 'news' in portal:
        api.content.delete(portal['news'])
