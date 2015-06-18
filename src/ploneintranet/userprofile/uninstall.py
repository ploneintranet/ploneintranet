# -*- coding: utf-8 -*-
# from plone import api


def uninstall(context):
    marker = 'ploneintranet.userprofile_uninstall.txt'
    if context.readDataFile(marker) is None:
        return

    # TODO: @mattss wants to uninstall more stuff
