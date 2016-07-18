# coding=utf-8
from plone import api
from plone.registry.field import Bool
from plone.registry.record import Record
import logging

default_profile = 'profile-ploneintranet.userprofile:default'
logger = logging.getLogger(__file__)


def add_password_reset_registry_entry(context):
    portal_registry = api.portal.get_tool('portal_registry')
    portal_registry.records[
        'ploneintranet.userprofile.enable_password_reset'] = Record(
            Bool(), True)
    assert(portal_registry[
        'ploneintranet.userprofile.enable_password_reset'] is True)
