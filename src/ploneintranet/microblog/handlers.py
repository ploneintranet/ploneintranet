import logging
from plone import api

from ploneintranet import api as pi_api

logger = logging.getLogger(__name__)


def create_post_on_content_published(event):
    if not event.action == 'publish':
        return
    logger.info('CONTENT_PUBLISHED: %s', event)
    obj = event.object
    workspace = getattr(obj, 'acquire_workspace', lambda: None)()
    user = api.user.get(username=obj.creators[0])
    pi_api.microblog.statusupdate.create(
        '{0} {1}ed <a href="{2}">{3}</a>'.format(
            user.fullName(),
            event.action,
            obj.absolute_url(),
            obj.Title()
        ),
        context=workspace
    )
