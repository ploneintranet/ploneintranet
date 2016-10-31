# coding=utf-8
from plone import api


def add_the_dashboard_tile(context):
    ''' We have a new tile in the dashboard.
    We want an upgrade step to add it if needed
    '''
    record_id = 'ploneintranet.layout.dashboard_activity_tiles'
    new_value = u'./@@bookmarks.tile?id_suffix=-dashboard'

    values = api.portal.get_registry_record(record_id)
    if new_value in values:
        # if the new value is already there, there is no reason to go on
        return

    # we want the new value after the target value
    target_value = u'./@@contacts_search.tile'

    if target_value in values:
        idx = values.index(target_value)
        values = list(values)
        values.insert(idx + 1, new_value)
    else:
        values = (new_value, ) + values

    api.portal.set_registry_record(record_id, tuple(values))
