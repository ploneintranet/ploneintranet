# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def include_login_colophon_actions(context):
    ''' We have a new portion of actions.xml that includes actions that
    have to be displayed in the colophon of the login form
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.layout.upgrades:to_0002'
    )
