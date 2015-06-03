import ExtensionClass
from Acquisition import Explicit
from Acquisition import aq_base
from BTrees.OOBTree import OOBTree
from OFS.Traversable import Traversable
from Products.Archetypes.utils import shasattr
from Products.CMFPlone.interfaces.breadcrumbs import IHideFromBreadcrumbs
from Products.CMFPlone.Portal import PloneSite
from persistent import Persistent
from zope import component
from zope import interface
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from zope.container.interfaces import DuplicateIDError

ANNOTATION_KEY = 'ploneintranet.attachments:attachments'


class IAttachmentStoragable(IAnnotatable):
    """ Marker interface for things that can have attachments
    """

# Make sure we can store attachments at the root of plone
interface.classImplements(PloneSite, IAttachmentStoragable)


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
    __allow_access_to_unprotected_subobjects__ = False

    def __init__(self):
        if not shasattr(self, '_attachments'):
            self.init_storage()

    def __getitem__(self, id):
        """ """
        return self.get(id)

    def getId(self):
        """ Get the id of the storage. This is used to construct a URL.
        """
        return '@@attachments'  # hardcode for backcompat in devel

    def init_storage(self):
        self._attachments = OOBTree()

    def keys(self):
        return self._attachments.keys()

    def values(self):
        return [att.__of__(self) for att in
                self._attachments.values()]

    def get(self, id):
        return self._attachments[id].__of__(self)

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
    annotations = IAnnotations(content)
    if ANNOTATION_KEY not in annotations:
        attachments = AttachmentStorage()
        attachments.__parent__ = aq_base(content)
        annotations[ANNOTATION_KEY] = attachments
    else:
        attachments = annotations[ANNOTATION_KEY]
    if isinstance(content, ExtensionClass.Base):
        return attachments.__of__(content)
    else:
        return attachments
