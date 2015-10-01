# -*- coding: utf-8 -*-
import logging
import transaction

from plone import api
from zope.site.hooks import getSite
from collective.documentviewer.settings import GlobalSettings
from collective.documentviewer.config import CONVERTABLE_TYPES

log = logging.getLogger(__name__)

# commits are needed in interactive but break in test mode
if api.env.test_mode:
    commit = lambda: None
else:
    commit = transaction.commit


def configure(context):
    """

    """
    if context.readDataFile('ploneintranet.docconv_default.txt') is None:
        return
    log.info("document conversion configuration")

    global_settings = GlobalSettings(getSite())
    global_settings.enable_indexation = False
    global_settings.auto_select_layout = False
    global_settings.auto_layout_file_types = CONVERTABLE_TYPES.keys()
    commit()
    log.info("document conversion configuration: done.")
