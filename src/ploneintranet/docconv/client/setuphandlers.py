# -*- coding: utf-8 -*-
from collective.documentviewer.settings import GlobalSettings
from collective.documentviewer.config import CONVERTABLE_TYPES
from logging import getLogger
from plone import api
from zope.site.hooks import getSite

log = getLogger(__name__)

# commits are needed in interactive but break in test mode
if api.env.test_mode:
    def commit():
        return
else:
    from transaction import commit


def configure(context):
    """

    """
    global_settings = GlobalSettings(getSite())
    global_settings.enable_indexation = False
    global_settings.auto_select_layout = False
    global_settings.auto_layout_file_types = CONVERTABLE_TYPES.keys()
    commit()
    log.info("document conversion configuration: done.")
