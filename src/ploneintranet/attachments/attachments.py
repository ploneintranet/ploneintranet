from Acquisition import Explicit
from Acquisition import aq_inner
from Acquisition import aq_base
from BTrees.OOBTree import OOBTree
from OFS.Traversable import Traversable
from Products.Archetypes.utils import shasattr
from Products.CMFPlone.interfaces.breadcrumbs import IHideFromBreadcrumbs
from persistent import Persistent
from zExceptions import NotFound
from zope import component
from zope import interface
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.container.interfaces import DuplicateIDError
from zope.traversing.interfaces import ITraversable

try:
    from plone.app.discussion.comment import Comment
except ImportError:
    Comment = None
try:
    from slc.underflow.question import Question
except ImportError:
    Question = None

ANNOTATION_KEY = 'ploneintranet.attachments:attachments'


class IAttachmentStoragable(IAnnotatable):
    """ Marker interface for things that can have attachments
    """

if Comment is not None:
    interface.classImplements(Comment, IAttributeAnnotatable)
    interface.classImplements(Comment, IAttachmentStoragable)
if Question is not None:
    interface.classImplements(Question, IAttachmentStoragable)


class IAttachmentStorage(interface.Interface):
    """ """

    def init_storage():
        """ """

    def keys():
        """ """

    def values():
        """ """

    def get(id):
        """ """

    def add(attachment):
        """ """

    def remove(id):
        """ """


class AttachmentStorage(Traversable, Persistent, Explicit):
    """ The attachment storage is a container for all attachments on content
        objects (that provide IAttachmentStoragable).

        All objects including non-folderish ones, can be adapted to store
        attachments, since attached objects are not stored inside the object,
        but inside this AttachmentStorage container (which is stored as an
        annotation on the object being attached to).
    """
    interface.implements(IAttachmentStorage, IHideFromBreadcrumbs)
    __allow_access_to_unprotected_subobjects__ = True

    def __init__(self, id="++attachments++default"):
        self.id = id
        if not shasattr(self, '_attachments'):
            self.init_storage()

    def __getitem__(self, id):
        """ """
        return self.get(id)

    def getId(self):
        """ Get the id of the storage. This is used to construct a URL.
        """
        return self.id

    def init_storage(self):
        self._attachments = OOBTree()

    def keys(self):
        return self._attachments.keys()

    def values(self):
        return [att.__of__(self) for att in
                self._attachments.values()]

    def get(self, id):
        return self._attachments.get(id).__of__(self)

    def add(self, attachment):
        if attachment.getId() in self._attachments:
            raise DuplicateIDError
        self._attachments[attachment.getId()] = attachment

    def remove(self, id):
        del self._attachments[id]


@interface.implementer(IAttachmentStorage)
@component.adapter(IAttachmentStoragable)
def AttachmentStorageAdapterFactory(content):
    """ Adapter factory to fetch the attachment storage from annotations.
    """
    annotions = IAnnotations(content)
    if not ANNOTATION_KEY in annotions:
        attachments = AttachmentStorage()
        attachments.__parent__ = aq_base(content)
        annotions[ANNOTATION_KEY] = attachments
    else:
        attachments = annotions[ANNOTATION_KEY]
    return attachments.__of__(content)


class AttachmentsNamespace(object):
    """ Allows traversal into the attachments storage via the
        ++attachments++name namespace.

        The name is the name of an adapter from context to
        IAttachmentStoragable. The special name 'default' will be taken
        as the default (unnamed) adapter. This is to work around a bug in
        OFS.Traversable which does not allow traversal to namespaces with
        an empty string name.

        For example, the file.txt attachment can be accessed via
        /path/to/object/++attachments++default/file.txt
    """
    interface.implements(ITraversable)

    def __init__(self, context, request=None):
        self.context = aq_inner(context)
        self.request = request

    def traverse(self, name, ignore):
        attachments = component.queryAdapter(
            self.context, IAttachmentStorage)

        if attachments is None:
            raise NotFound

        return attachments
