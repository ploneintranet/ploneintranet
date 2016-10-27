# -*- coding: utf-8 -*-
import logging

default_profile = 'profile-ploneintranet.bookmarks:default'
logger = logging.getLogger(__file__)


def reload_registry(context):
    context.runImportStepFromProfile(default_profile, 'plone.app.registry')
