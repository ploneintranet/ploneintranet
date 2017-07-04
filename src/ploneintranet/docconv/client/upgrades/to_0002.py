# coding=utf-8
from collective.documentviewer.settings import GlobalSettings
from plone import api


def change_settings(context):
    ''' Update the document converter settings
    '''
    global_settings = GlobalSettings(api.portal.get())
    global_settings.thumb_size = 460
