"""
Defines the policies that can be applied to a workspace
"""
from collections import OrderedDict
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa

EXTERNAL_VISIBILITY = OrderedDict([
    ('secret', {
        "title": _(u"Secret"),
        "help": _(
            u"The workspace is hidden from outsiders. Only workspace "
            u"members know it exists."
        ),
    }),
    ('private', {
        "title": _(u"Private"),
        "help": _(
            u"The workspace is visible, but inaccessible to outsiders. "
            u"Only workspace members can access the workspace."
        ),
    }),
    ('open', {
        "title": _(u"Open"),
        "help": _(
            u"The workspace can be explored by outsiders. Outsiders can "
            u"browse but not actively participate."
        ),
    }),
])

JOIN_POLICY = OrderedDict([
    ('admin', {
        "title": _(u"Admin-Managed"),
        "help": _(u"Only administrators can add workspace members."),
    }),
    ('team', {
        "title": _(u"Team-Managed"),
        "help": _(
            u"Workspace members can add outsiders as a workspace member."),
    }),
    ('self', {
        "title": _(u"Self-Managed"),
        "help": _(u"Outsiders can self-join becoming a workspace member."),
    }),
])

PARTICIPANT_POLICY = OrderedDict([
    ('consumers', {
        "title": _(u"Consume"),
        "help": _(
            u"Workspace members can read content. They cannot add, "
            u"publish or edit content."
        ),
    }),
    ('producers', {
        "title": _(u"Produce"),
        "help": _(
            u"Workspace members can read and add content. They can "
            u"neither publish nor edit content."
        ),
    }),
    ('publishers', {
        "title": _(u"Publish"),
        "help": _(
            u"Workspace members can read, add and publish content. They "
            u"cannot edit other member's content."
        ),
    }),
    ('moderators', {
        "title": _(u"Moderate"),
        "help": _(
            u"Workspace members can do everything: read, add, publish and "
            u"edit content."
        ),
    }),
])
