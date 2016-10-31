# coding=utf-8
from plone import api
from plone.app.upgrade.utils import loadMigrationProfile


def prep_for_workgroups(context):
    ''' There is a new registry record called
    ploneintranet.userprofile.userprofile_hidden_info
    that makes the profile view configurable
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.userprofile.upgrades:to_0006',
    )
    mt = api.portal.get_tool('membrane_tool')
    if 'ploneintranet.userprofile.workgroup' not in mt.membrane_types:
        mt.membrane_types.append('ploneintranet.userprofile.workgroup')
        mt._p_changed = 1
