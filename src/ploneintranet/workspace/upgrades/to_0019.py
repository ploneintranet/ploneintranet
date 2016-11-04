# coding=utf-8
from plone import api
from ploneintranet.userprofile.setuphandlers import get_or_create_workgroup_container  # noqa


def workspacecontainer_contains_workgroups(context):
    ''' We have a new type ploineintranet.userprofile.workgroup
    that should be added to workspace containers
    '''
    pt = api.portal.get_tool('portal_types')
    typ = pt['ploneintranet.workspace.workspacecontainer']
    typ.allowed_content_types
    if 'ploneintranet.userprofile.workgroup' not in typ.allowed_content_types:
        typ.allowed_content_types += ('ploneintranet.userprofile.workgroup',)
    get_or_create_workgroup_container(context)
