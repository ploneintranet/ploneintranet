# -*- coding: utf-8 -*-
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

from plone import api
from plone.dexterity.interfaces import IDexterityContent
from plone.memoize import view
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five import BrowserView

from ploneintranet import api as pi_api
from ploneintranet.layout.interfaces import IAppContent
from ploneintranet.library.content import ILibraryApp, ILibraryFolder
from ploneintranet.library.browser.utils import sections_of
from ploneintranet.workspace.unrestricted import execute_as_manager

import logging
log = logging.getLogger(__name__)


class IPublishWidely(Interface):
    """
    A behavior that allows an object to place a copy
    of itself in the Library.

    Note that not every object with this behavior necessarily
    is published widely. It's just enabled to do so if needed.
    """

    def can_publish_widely():
        """
        Is the context object eligible to be published widely?
        Checks the following conditions:
        - context is not contained in Library app
        - context state is 'published'
        - context is not already widely published
        - user has Reviewer permissions

        :rtype: bool
        """

    def copy_to(target):
        """
        Copies the context object to the target.
        Submits copy for review.

        :param target: Target folder to copy to.
        :type target: ILibraryFolder.
        :returns: The newly created copy object.
        :rtype: IDexterityContent (same as self.context)
        """

    def source():
        """
        Get the original content object, if the current context
        is a widely published copy of an original.

        :returns: Original for this context, or None
        :rtype: IDexterityContent or None
        """

    def target():
        """
        Get the copied content object, if the current context
        is the original for a widely published copy.

        :returns: Target for this context, or None
        :rtype: IDexterityContent or None
        """


@implementer(IPublishWidely)
@adapter(IDexterityContent)
class PublishWidely(object):

    def __init__(self, context):
        self.context = context

    def can_publish_widely(self):
        app = IAppContent(self.context).get_app()
        # don't allow copying FROM library
        if ILibraryApp.providedBy(app):
            return False
        # only locally published content may be widely published
        try:
            if api.content.get_state(self.context) not in ('published',):
                return False
        except WorkflowException:
            # no workflow, e.g. images
            pass
        # may only publish widely once
        if self.target():
            return False
        # only reviewers may publish widely
        return api.user.has_permission(
            "Review portal content",
            obj=self.context
        )

    def get_library(self):
        # cannot use object_provides query for some reason
        portal = api.portal.get()
        try:
            if ILibraryApp.providedBy(portal.library):
                return portal.library
        except (AttributeError, TypeError):
            pass
        for section in portal.objectValues():
            if ILibraryApp.providedBy(section):
                return section
        raise ValueError("No library app")

    def copy_to(self, target):
        if not self.can_publish_widely():
            log.error("Cannot publish widely: {}".format(self.context))
            return None
        if not ILibraryFolder.providedBy(target):
            log.error("Invalid target: {}".format(target))
            return None
        pi_api.events.disable_previews()

        def copy_and_submit(content, target, user):
            new = api.content.copy(content, target)
            api.content.transition(new, 'submit')
            new.changeOwnership(user)
            # list publishing user as first creator = owner
            creators = [user.id] + [x for x in new.creators if x != user.id]
            new.setCreators(creators)

            # If the required registry setting is present, order the items in
            # the target folder in reverse chronological order.
            if api.portal.get_registry_record(
                'ploneintranet.library.order_by_modified',
                default=False,
            ):
                ordering = target.getOrdering()
                catalog = api.portal.get_tool('portal_catalog')
                query = {
                    'path': {
                        'query': '/'.join(target.getPhysicalPath()),
                        'depth': 1
                    },
                    'sort_on': 'modified',
                    'sort_order': 'descending',
                }
                brains = catalog(**query)
                for idx, brain in enumerate(brains):
                    ordering.moveObjectToPosition(brain.id, idx)

            return new

        user = api.user.get_current()
        new = execute_as_manager(copy_and_submit,
                                 self.context, target, user)
        log.info("{} copied {} --> {}".format(
            user.id, self.context.absolute_url(), new.absolute_url()
        ))
        setattr(self.context, 'publish_widely_target_uuid', IUUID(new))
        setattr(new, 'publish_widely_source_uuid', IUUID(self.context))
        return new

    def source(self):
        uuid = getattr(self.context, 'publish_widely_source_uuid', None)
        if uuid:
            return uuidToObject(uuid)

    def target(self):
        uuid = getattr(self.context, 'publish_widely_target_uuid', None)
        if uuid:
            return uuidToObject(uuid)


class PublishActionView(BrowserView):

    copy_obj = None

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        target_path = self.request.get('target_path')
        if target_path:
            path = target_path.split('/')
            target = self.library.restrictedTraverse(path)
            self.copy_obj = IPublishWidely(self.context).copy_to(target)

    @property
    @view.memoize_contextless
    def library(self):
        return IPublishWidely(self.context).get_library()

    def library_url(self):
        return self.library.absolute_url()

    def copied_to_url(self):
        if not self.copy_obj:
            log.error("No copy found")
            return '#'
        return self.copy_obj.absolute_url()

    def target_tree(self):
        return sections_of(self.library)
