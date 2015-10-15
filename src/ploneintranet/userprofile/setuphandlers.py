# -*- coding: utf-8 -*-

from logging import getLogger
from plone import api

logger = getLogger(__name__)


def get_or_create_userprofile_container(context=None):
    ''' We want to have a profiles folder in the plone site root
    We want it public

    The context paramer is ignored
    It depends on wheter this function is called as an upgrade
    or an import step
    We use plone api to get the portal.
    '''
    portal = api.portal.get()
    try:
        container = portal.contentValues(
            {'portal_type': "ploneintranet.userprofile.userprofilecontainer"}
        )[0]
    except IndexError:
        logger.info('Creating user profile container')
        container = api.content.create(
            title="Profiles",
            type="ploneintranet.userprofile.userprofilecontainer",
            container=portal
        )

    if container.getId() != 'profiles':
        logger.warning(
            'The id for user profile container is "%s" and not "profiles"',
            container.getId()
        )

    if api.content.get_state(container) != 'published':
        logger.info(
            'Publishing the user profile container %s',
            container.getId(),
        )
        try:
            api.content.transition(container, 'publish')
        except:
            logger.exception(
                'Cannot publish the user profile container %s',
                container.getId(),
            )


def update_dx_membrane_behaviors(context):
    '''dexterity.membrane 1.1.0 changed the names of its behaviours'''
    from zope.component import getUtility
    from plone.dexterity.interfaces import IDexterityFTI
    fti = getUtility(IDexterityFTI,
                     name='ploneintranet.userprofile.userprofile')
    old_behaviors = list(fti.behaviors)
    new_behaviors = []
    for behavior in old_behaviors:
        behavior = behavior.replace(
            'dexterity.membrane.behavior.membrane',
            'dexterity.membrane.behavior.')
        new_behaviors.append(behavior)
    fti.behaviors = tuple(new_behaviors)


def on_install(context):
    """
    Important!
    We do not want to have users with global roles such as Editor or
    Contributor in out test setup.
    """
    if context.readDataFile('ploneintranet.userprofile.default.txt') is None:
        return
    get_or_create_userprofile_container()
