# -*- coding: utf-8 -*-
from plone import api
import logging

log = logging.getLogger(__name__)


def uninstall(context):
    if context.readDataFile('ploneintranet.theme_uninstall.txt') is None:
        return
    portal = api.portal.get()
    portal.setLayout('listing_view')
