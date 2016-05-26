import threading
import Queue
import logging
import time
import math
import sys

from BTrees import LOBTree
from BTrees import OOBTree
from BTrees import LLBTree

from persistent import Persistent
import transaction
from Acquisition import Explicit
from AccessControl import Unauthorized
import Zope2
from Testing.makerequest import makerequest
from Products.CMFCore.utils import getToolByName

from zope.component.hooks import setSite
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.container.contained import ObjectAddedEvent
from zope.event import notify
from zope.interface import implements

from plone import api
from plone.uuid.interfaces import IUUID
from plone.memoize import ram
from plone.protect.utils import safeWrite
from interfaces import IStatusContainer
from interfaces import IStatusUpdate
from interfaces import IMicroblogContext
from utils import longkeysortreverse

logger = logging.getLogger('ploneintranet.microblog')

LOCK = threading.RLock()
STATUSQUEUE = Queue.PriorityQueue()


def cache_key(method, self):
    """
    Used as ramcache key for the expensive and frequently used
    allowed_status_keys() results.
    - cache per user
    - until a new update is inserted
    - for maximally 1 second

    The short time interval is needed in case the user's workspace
    memberships change - this should invalidate the cache but we're
    not listening to that event directly.
    One second on the other hand is enough to cache the results for
    multiple calls during a single page rendering request.

    memoize.ram automatically garbage collects the cache after 24 hours.
    """
    try:
        member = api.user.get_current()
    except api.exc.CannotGetPortalError:
        # getSite() fails in integration tests, disable caching
        raise ram.DontCache
    return (member.id,
            self._mtime,  # last add in milliseconds (self = statuscontainer)
            self._ctime,  # last delete in microseconds
            time.time() // 1)


def getZope2App(*args, **kwargs):
    """Gets the Zope2 app.

    Copied almost verbatim from collective.celery
    """
    if Zope2.bobo_application is None:
        orig_argv = sys.argv
        sys.argv = ['']
        res = Zope2.app(*args, **kwargs)
        sys.argv = orig_argv
        return res
    # should set bobo_application
    # man, freaking zope2 is weird
    return Zope2.bobo_application(*args, **kwargs)


class BaseStatusContainer(Persistent, Explicit):

    """This implements IStatusUpdate storage, indexing and query logic.

    This is just a base class, the actual IStorageContainer used
    in the implementation is the QueuedStatusContainer defined below.

    StatusUpdates are stored in the private _status_mapping BTree.
    A subset of BTree accessors are exposed, see interfaces.py.
    StatusUpdates are keyed by longint microsecond ids.

    Additionally, StatusUpdates are indexed by users and tags.
    These indexes use the same longint microsecond IStatusUpdate.id.

    Special user_* prefixed accessors take an extra argument 'users',
    an interable of userids, and return IStatusUpdate keys, instances or items
    filtered by userids, in addition to the normal min/max statusid filters.

    For backward compatibility sake, microblog_context is indexed as
    _uuid_mapping and accessors are called .context_*.
    This microblog_context is the security context for statusupdates.

    The newer content_context is indexed as
    _content_mapping and accessors are called .content_*.
    This has no security impact and is only a convenience for per-document
    accessors.
    """

    implements(IStatusContainer)
    dontcache = False  # used to disable cache during deletion

    def __init__(self, context=None):
        # last add in milliseconds - used in both async and cache key
        self._mtime = 0
        # cache buster in MICROseconds - used in cache key only
        self._ctime = 0
        # primary storage: (long statusid) -> (object IStatusUpdate)
        self._status_mapping = LOBTree.LOBTree()
        # index by user: (string userid) -> (object TreeSet(long statusid))
        self._user_mapping = OOBTree.OOBTree()
        # index by tag: (string tag) -> (object TreeSet(long statusid))
        self._tag_mapping = OOBTree.OOBTree()
        # index by microblog_context:
        # (string UUID) -> (object TreeSet(long statusid))
        self._uuid_mapping = OOBTree.OOBTree()  # keep old name for backcompat
        # index by content_context:
        # (string UUID) -> (object TreeSet(long statusid))
        self._content_uuid_mapping = OOBTree.OOBTree()
        # index by thread (string UUID) -> (object TreeSet(long statusid))
        self._threadid_mapping = OOBTree.OOBTree()
        # index by mentions (string UUID) -> (object TreeSet(long statusid))
        self._mentions_mapping = OOBTree.OOBTree()

    def add(self, status):
        self._check_status(status)
        self._check_add_permission(status)
        self._store(status)

    def _store(self, status):
        # see ZODB/Btree/Interfaces.py
        # If the key was already in the collection, there is no change
        while not self._status_mapping.insert(status.id, status):
            status.id += 1
        self._idx_user(status)
        self._idx_tag(status)
        self._idx_microblog_context(status)
        self._idx_content_context(status)
        self._idx_threadid(status)
        self._idx_mentions(status)
        self._notify(status)
        # the _store() method is shared between Base and Async
        # putting counter updates here ensures maximal consistency
        self._update_mtime()  # millisec for async scheduler
        self._update_ctime()  # microsecond granularity cache busting

    def _check_status(self, status):
        if not IStatusUpdate.providedBy(status):
            raise ValueError("IStatusUpdate interface not provided.")

    def _notify(self, status):
        event = ObjectAddedEvent(status,
                                 newParent=self,
                                 newName=status.id)
        notify(event)

    def delete(self, id):
        status = self._get(id)  # bypass view permission check
        # delete permission check only original, not thread cascase
        self._check_delete_permission(status)
        thread_mapping = self._threadid_mapping.get(id)
        if thread_mapping:
            # list() avoids RuntimeError
            # mapping includes current parent id automatically
            to_delete = list(thread_mapping)
        else:
            to_delete = [id]
        for xid in to_delete:
            self._unidx(xid)
            self._status_mapping.pop(xid)
        self._update_ctime()  # purge cache

    def _unidx(self, id):
        status = self._get(id)  # bypass view permission check
        self._unidx_user(status)
        self._unidx_tag(status)
        self._unidx_microblog_context(status)
        self._unidx_content_context(status)
        self._unidx_threadid(status)
        self._unidx_mentions(status)

    # --- INDEXES ---

    def _idx_user(self, status):
        userid = unicode(status.userid)
        # If the key was already in the collection, there is no change
        # create user treeset if not already present
        self._user_mapping.insert(userid, LLBTree.LLTreeSet())
        # add status id to user treeset
        self._user_mapping[userid].insert(status.id)

    def _unidx_user(self, status):
        self._user_mapping[status.userid].remove(status.id)

    def _idx_tag(self, status):
        """
        Update the `StatusContainer` tag index with any new tags
        :param status: a `StatusUpdate` object
        """
        if status.tags is None:
            return
        for tag in [tag.decode('utf-8') for tag in status.tags]:
            # If the key was already in the collection, there is no change
            # create tag treeset if not already present
            self._tag_mapping.insert(tag, LLBTree.LLTreeSet())
            # add status id to tag treeset
            self._tag_mapping[tag].insert(status.id)

    def _unidx_tag(self, status):
        if status.tags is None:
            return
        for tag in [tag.decode('utf-8') for tag in status.tags]:
            self._tag_mapping[tag].remove(status.id)

    def _idx_microblog_context(self, status):
        uuid = status._microblog_context_uuid
        if not uuid:
            return
        # If the key was already in the collection, there is no change
        # create tag treeset if not already present
        self._uuid_mapping.insert(uuid, LLBTree.LLTreeSet())
        self._uuid_mapping[uuid].insert(status.id)

    def _unidx_microblog_context(self, status):
        uuid = status._microblog_context_uuid
        if not uuid:
            return
        self._uuid_mapping[uuid].remove(status.id)

    def _idx_content_context(self, status):
        uuid = status._content_context_uuid
        if not uuid:
            return
        # If the key was already in the collection, there is no change
        # create tag treeset if not already present
        self._content_uuid_mapping.insert(uuid, LLBTree.LLTreeSet())
        self._content_uuid_mapping[uuid].insert(status.id)

    def _unidx_content_context(self, status):
        uuid = status._content_context_uuid
        if not uuid:
            return
        self._content_uuid_mapping[uuid].remove(status.id)

    def _idx_threadid(self, status):
        if not getattr(status, 'thread_id', False):
            return
        thread_id = status.thread_id
        if thread_id:
            # If the key was already in the collection, there is no change
            # create tag treeset if not already present
            self._threadid_mapping.insert(thread_id, LLBTree.LLTreeSet())
            self._threadid_mapping[thread_id].insert(status.id)
            # Make sure thread_id is also in the mapping
            self._threadid_mapping[thread_id].insert(thread_id)

    def _unidx_threadid(self, status):
        if not getattr(status, 'thread_id', False):
            return
        thread_id = status.thread_id
        if thread_id:
            self._threadid_mapping[thread_id].remove(status.id)

    def _idx_mentions(self, status):
        if not getattr(status, 'mentions', False):
            return
        mentions = status.mentions.keys()
        for mention in mentions:
            # If the key was already in the collection, there is no change
            # create tag treeset if not already present
            self._mentions_mapping.insert(mention, LLBTree.LLTreeSet())
            self._mentions_mapping[mention].insert(status.id)

    def _unidx_mentions(self, status):
        if not getattr(status, 'mentions', False):
            return
        mentions = status.mentions.keys()
        for mention in mentions:
            self._mentions_mapping[mention].remove(status.id)

    def clear(self):
        self._user_mapping.clear()
        self._tag_mapping.clear()
        self._uuid_mapping.clear()
        self._content_uuid_mapping.clear()
        self._threadid_mapping.clear()
        self._mentions_mapping.clear()
        return self._status_mapping.clear()

    # --- WRITE SECURITY ---

    def _check_add_permission(self, status):
        permission = "Plone Social: Add Microblog Status Update"
        # can also throw statusupdate._uuid2context() uuid lookup Unauthorized
        if not api.user.has_permission(
                permission,
                obj=status.microblog_context):  # None=SiteRoot handled by api
            raise Unauthorized("You do not have permission <%s>" % permission)

    def _check_delete_permission(self, status):
        """
        StatusUpdates have no local 'owner' role. Instead we check against
        permissions on the microblog context and compare with the creator.
        """
        if not status.can_delete:
            raise Unauthorized("Not allowed to delete this statusupdate")

    # --- READ SECURITY ---

    def _check_global_view_permission(self):
        """Stopgap. To support extranet scenarios this will need
        to be refactored without sacrificing performance.
        """
        # hardcode non-anon protection at siteroot for now
        permission = "Plone Social: View Microblog Status Update"
        try:
            if not api.user.has_permission(permission):
                raise Unauthorized()
        except api.exc.CannotGetPortalError:  # happens in tests
            pass

    def secure(self, keyset):
        """Filter keyset to return only keys the current user may see.

        NB this may return statusupdates with a microblog_context (workspace)
        accessible to the user, but referencing a content_context (document)
        which the user may not access yet because of content workflow.

        Filtering that is quite costly and not done here - instead there's a
        postprocessing filter in activitystream just before rendering.
        """
        return LLBTree.intersection(
            LLBTree.LLTreeSet(keyset),
            LLBTree.LLTreeSet(self.allowed_status_keys()))

    @ram.cache(cache_key)
    def allowed_status_keys(self):
        """Return the subset of IStatusUpdate keys
        that are related to UUIDs of accessible contexts.
        I.e. blacklist all IStatusUpdate that has a context
        which we don't have permission to access.

        This is the key security protection used by all getters.
        Because it's called a lot we're caching results per user request.
        """
        self._check_global_view_permission()

        uuid_blacklist = self._blacklist_microblogcontext_uuids()
        if not uuid_blacklist:
            return self._status_mapping.keys()
        else:
            # for each uid, expand uid into set of statusids
            blacklisted_treesets = (self._uuid_mapping.get(uuid)
                                    for uuid in uuid_blacklist
                                    if uuid in self._uuid_mapping.keys())
            # merge sets of blacklisted statusids into single blacklist
            blacklisted_statusids = reduce(LLBTree.union,
                                           blacklisted_treesets,
                                           LLBTree.TreeSet())
            # subtract blacklisted statusids from all statusids
            all_statusids = LLBTree.LLSet(self._status_mapping.keys())
            return LLBTree.difference(all_statusids,
                                      blacklisted_statusids)

    def _blacklist_microblogcontext_uuids(self):
        """Returns the uuids for all IMicroblogContext that the current
        user has no access to.

        All the read accessors rely on this method for security checks.

        Current catalog query implicitly filters on View permission for
        the current user.
        We should not rely on View adequately representing ViewStatusUpdate.

        The current implementation takes a conservative approach by
        applying an extra explicit security check for ViewStatusUpdate.

        It is theoretically possible that the result excludes workspaces for
        which the user does have ViewStatusUpdate but does not have View.

        A possible performance optimization that would also fix the overly
        conservative bias would be to add a special index for
        ViewStatusUpdate and use that directly in the catalog query.
        See http://stackoverflow.com/questions/23950860/how-to-list-users-having-review-permission-on-content-object

        However, the number of IMicroblogContext objects in a site is
        normally quite limited and the outcome of this check is cached
        per request, which should hopefully limit the performance cost.
        """  # noqa
        catalog = getToolByName(self, 'portal_catalog')
        marker = IMicroblogContext.__identifier__

        results = catalog.searchResults(object_provides=marker)

        permission = "Plone Social: View Microblog Status Update"

        # SiteRoot context is NOT whitelisted
        whitelist = []
        for brain in results:
            try:
                obj = brain.getObject()
            except Unauthorized:
                # can View but not Access workspace - skip
                continue
            # and double check for ViewStatusUpdate
            if api.user.has_permission(permission, obj=obj):
                whitelist.append(brain.UID)

        # SiteRoot context is not UUID indexed, so not blacklisted
        blacklist = [x for x in self._uuid_mapping.keys()
                     if x not in whitelist]

        # return all statuses with no IMicroblogContext (= SiteRoot)
        # or with a IMicroblogContext that is accessible (= not blacklisted)
        return blacklist

    # --- DISABLED ACCESSORS ---
    # blocked IBTree methods to protect index consistency
    # (also not sensible for our use case)

    def insert(self, key, value):
        raise NotImplementedError("Can't allow that to happen.")

    def pop(self, k, d=None):
        raise NotImplementedError("Can't allow that to happen.")

    def setdefault(self, k, d):
        raise NotImplementedError("Can't allow that to happen.")

    def update(self, collection):
        raise NotImplementedError("Can't allow that to happen.")

    # --- PRIMARY ACCESSORS ---

    def get(self, key):
        key = int(key)
        # secure
        if key in self.allowed_status_keys():
            return self._get(key)
        # don't mask lookup error with Unauthorized
        elif key not in self._status_mapping.keys():
            raise KeyError(key)
        else:
            raise(Unauthorized("You're not allowed to get status %s'" % key))

    # performance helper to avoid multiple security checks
    def _get(self, key):
        return self._status_mapping.get(key)

    def items(self, min=None, max=None, limit=100, tag=None):
        # secured in keys()
        return ((key, self._get(key))
                for key in self.keys(min, max, limit, tag))

    def values(self, min=None, max=None, limit=100, tag=None):
        # secured in keys()
        return (self._get(key)
                for key in self.keys(min, max, limit, tag))

    def keys(self, min=None, max=None, limit=100, tag=None):
        if tag and tag not in self._tag_mapping:
            return ()
        # secure
        mapping = self._keys_tag(tag, self.allowed_status_keys())
        return longkeysortreverse(mapping,
                                  min, max, limit)

    iteritems = items
    iterkeys = keys
    itervalues = values

    # --- THREAD CONVERSATION ACCESSORS ---

    def thread_items(self, thread_id, min=None, max=None, limit=100):
        # secured by thread_keys
        return ((key, self._get(key)) for key
                in self.thread_keys(thread_id, min, max, limit))

    def thread_values(self, thread_id, min=None, max=None, limit=100):
        # secured by thread_keys
        return (self._get(key) for key
                in self.thread_keys(thread_id, min, max, limit))

    def thread_keys(self, thread_id, min=None, max=None, limit=100):
        if not thread_id:
            return ()
        mapping = self._threadid_mapping.get(thread_id) or [thread_id]
        mapping = self.secure(mapping)
        return longkeysortreverse(mapping,
                                  min, max, limit)

    # --- USER ACCESSORS ---

    def user_items(self, users, min=None, max=None, limit=100, tag=None):
        # secured by user_keys
        return ((key, self._get(key)) for key
                in self.user_keys(users, min, max, limit, tag))

    def user_values(self, users, min=None, max=None, limit=100, tag=None):
        # secured by user_keys
        return (self._get(key) for key
                in self.user_keys(users, min, max, limit, tag))

    def user_keys(self, users, min=None, max=None, limit=100, tag=None):
        if not users:
            return ()
        if tag and tag not in self._tag_mapping:
            return ()

        if users == str(users):
            # single user optimization
            userid = users
            mapping = self._user_mapping.get(userid)
            if not mapping:
                return ()

        else:
            # collection of user LLTreeSet
            treesets = (self._user_mapping.get(userid)
                        for userid in users
                        if userid in self._user_mapping.keys())
            mapping = reduce(LLBTree.union, treesets, LLBTree.TreeSet())

        # returns unchanged mapping if tag is None
        mapping = self._keys_tag(tag, mapping)
        mapping = self.secure(mapping)
        return longkeysortreverse(mapping,
                                  min, max, limit)

    # --- CONTEXT ACCESSORS = microblog_context security context ---

    def context_items(self, microblog_context,
                      min=None, max=None, limit=100, tag=None, nested=True):
        # secured by microblog_context_keys
        return ((key, self._get(key)) for key
                in self.context_keys(microblog_context,
                                     min, max, limit, tag, nested))

    def context_values(self, microblog_context,
                       min=None, max=None, limit=100, tag=None, nested=True):
        # secured by microblog_context_keys
        return (self._get(key) for key
                in self.context_keys(microblog_context, min, max,
                                     limit, tag, nested))

    def context_keys(self, microblog_context,
                     min=None, max=None, limit=100,
                     tag=None, nested=True, mention=None):
        if tag and tag not in self._tag_mapping:
            return ()

        if nested:
            # hits portal_catalog
            nested_uuids = [uuid
                            for uuid in self.nested_uuids(microblog_context)
                            if uuid in self._uuid_mapping]
            if not nested_uuids:
                return ()

        else:
            # used in test_statuscontainer_microblog_context
            uuid = self._context2uuid(microblog_context)
            if uuid not in self._uuid_mapping:
                return ()
            nested_uuids = [uuid]

        # tag and uuid filters handle None inputs gracefully
        keyset_tag = self._keys_tag(tag, self.allowed_status_keys())

        # mention and uuid filters handle None inputs gracefully
        keyset_mention = self._keys_tag(mention, keyset_tag)

        # calculate the tag+mention+uuid intersection for microblog_context
        keyset_uuids = [self._keys_uuid(_uuid, keyset_mention)
                        for _uuid in nested_uuids]

        # merge the intersections
        merged_set = LLBTree.multiunion(keyset_uuids)
        merged_set = self.secure(merged_set)
        return longkeysortreverse(merged_set,
                                  min, max, limit)

    # enable unittest override of plone.app.uuid lookup
    def _context2uuid(self, context):
        return IUUID(context)

    # --- CONTENT ACCESSORS = content_context

    def content_items(self, content_context):
        return ((key, self._get(key)) for key
                in self.content_keys(content_context))

    def content_values(self, content_context):
        return (self._get(key) for key
                in self.content_keys(content_context))

    def content_keys(self, content_context):
        uuid = self._context2uuid(content_context)
        mapping = self._content_uuid_mapping.get(uuid)
        if not mapping:
            return ()
        # security is derived from microblog_context NOT from content_context
        mapping = self.secure(mapping)
        # not reversing, keep document discussion in chronological order
        return mapping

    # --- MENTION ACCESSORS ---

    def mention_items(self, mentions, min=None, max=None, limit=100, tag=None):
        # secured by mention_keys
        return ((key, self._get(key)) for key
                in self.mention_keys(mentions, min, max, limit, tag))

    def mention_values(self, mentions,
                       min=None, max=None, limit=100,
                       tag=None):
        # secured by mention_keys
        return (self._get(key) for key
                in self.mention_keys(mentions, min, max, limit, tag))

    def mention_keys(self, mentions, min=None, max=None, limit=100, tag=None):
        if not mentions:
            return ()
        if tag and tag not in self._tag_mapping:
            return ()

        if mentions == str(mentions):
            # single mention optimization
            mention = mentions
            mapping = self._mentions_mapping.get(mention)
            if not mapping:
                return ()

        else:
            # collection of LLTreeSet
            treesets = (self._mentions_mapping.get(mention)
                        for mention in mentions
                        if mention in self._mentions_mapping.keys())
            mapping = reduce(LLBTree.union, treesets, LLBTree.TreeSet())

        # returns unchanged mapping if tag is None
        mapping = self._keys_tag(tag, mapping)
        mapping = self.secure(mapping)
        return longkeysortreverse(mapping,
                                  min, max, limit)

    # --- HELPERS ---

    def nested_uuids(self, context):
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(path={'query': '/'.join(context.getPhysicalPath()),
                                'depth': -1},
                          object_implements=IMicroblogContext)
        return([item.UID for item in results])

    def _keys_tag(self, tag, keyset):
        if tag is None:
            return keyset
        return LLBTree.intersection(
            LLBTree.LLTreeSet(keyset),
            self._tag_mapping[tag])

    def _keys_mention(self, mention, keyset):
        if mention is None:
            return keyset
        return LLBTree.intersection(
            LLBTree.LLTreeSet(keyset),
            self._mentions_mapping[mention])

    def _keys_uuid(self, uuid, keyset):
        if uuid is None:
            return keyset
        return LLBTree.intersection(
            LLBTree.LLTreeSet(keyset),
            self._uuid_mapping[uuid])

    def _update_mtime(self):
        """Update _mtime on statusupdate add.
        Uses milliseconds. This flag is used for the cache key
        and for the async time window.
        """
        with LOCK:
            self._mtime = int(time.time() * 1000)

    def _update_ctime(self):
        """Update _ctime for cache busting.
        Requires *micro*seconds granularity to avoid RuntimeError
        by cache interference. Only used for cache invalidation.
        """
        with LOCK:
            self._ctime = int(time.time() * 1000000)


class QueuedStatusContainer(BaseStatusContainer):

    """A write performance optimized IStatusContainer.

    This separates the queuing logic from the base class to make
    the code more readable (and testable).

    For performance reasons, an in-memory STATUSQUEUE is used.
    StatusContainer.add() puts StatusUpdates into the queue.

    MAX_QUEUE_AGE is the commit window in milliseconds.
    To disable batch queuing, set MAX_QUEUE_AGE = 0

    .add() calls .autoflush(), which flushes the queue when
    ._mtime is longer than MAX_QUEUE_AGE ago.

    So each .add() checks the queue. In a low-traffic site this will
    result in immediate disk writes (msg frequency < timeout).
    In a high-traffic site this will result on one write per timeout,
    which makes it possible to attain > 100 status update inserts
    per second.

    Note that the algorithm is structured in such a way, that the
    system automatically adapts to low/high traffic conditions.

    Additionally, a non-interactive queue flush is set up via
    _schedule_flush() which uses a volatile thread timer _v_timer
    to set up a non-interactive queue flush. This ensures that
    the "last Tweet of the day" also gets committed to disk.

    An attempt is made to make self._mtime and self._v_timer
    thread-safe. These function as a kind of ad-hoc locking
    mechanism so that only one thread at a time is flushing the
    memory queue into persistent storage.
    """

    implements(IStatusContainer)

    # set ASYNC=False to force sync mode and ignore MAX_QUEUE_AGE
    if api.env.test_mode():
        ASYNC = False
    else:
        ASYNC = True
    # max in-memory time in millisec before disk sync, if in ASYNC mode
    MAX_QUEUE_AGE = 1000

    def add(self, status):
        self._check_status(status)
        self._check_add_permission(status)
        if self.ASYNC and self.MAX_QUEUE_AGE > 0:
            self._queue(status)
            # fallback sync in case of NO traffic (kernel timer)
            self._schedule_flush()
            # immediate sync on low traffic (old ._mtime)
            # postpones sync on high traffic (next .add())
            return self._autoflush()  # updates _mtime on write
        else:
            self._store(status)
            return 1  # immediate write

    def _queue(self, status):
        STATUSQUEUE.put((status.id, status))

    def _schedule_flush(self):
        """A fallback queue flusher that runs without user interactions"""
        if not self.MAX_QUEUE_AGE > 0:
            return

        try:
            # non-persisted, absent on first request
            self._v_timer
        except AttributeError:
            # initialize on first request
            self._v_timer = None

        if self._v_timer is not None:
            # timer already running
            return

        # only a one-second granularity, round upwards
        timeout = int(math.ceil(float(self.MAX_QUEUE_AGE) / 1000))
        # Get the global request,
        # we just need to copy over some environment stuff.
        request = getRequest()
        request_environ = {}
        site = getSite()
        # We do not use plone.api here because we cannot assume
        # that site == plone portal.
        # It could also be a directory under it
        if site:
            site_path = '/'.join(site.getPhysicalPath())
            if request is None:
                # If we fail getting a request,
                # we might still have it in portal
                request = getattr(site, 'REQUEST', None)
        else:
            # This situation can happen in tests.
            logger.warning("Could not get the site")
            site_path = None
        if request is not None:
            request_environ = {
                'SERVER_NAME': request.SERVER_NAME,
                'SERVER_PORT': request.SERVER_PORT,
                'REQUEST_METHOD': request.REQUEST_METHOD
            }
        with LOCK:
            # logger.info("Setting timer")
            self._v_timer = threading.Timer(
                timeout,
                self._scheduled_autoflush,
                kwargs={'site_path': site_path, 'environ': request_environ}
            )
            self._v_timer.start()

    def _scheduled_autoflush(self, site_path=None, environ=None):
        """This method is run from the timer, outside a normal request scope.
        This requires an explicit commit on db write"""
        if site_path is not None:
            app = makerequest(getZope2App(), environ=environ)
            site = app.restrictedTraverse(site_path)
            setSite(site)
        if self._autoflush():  # returns 1 on actual write
            transaction.commit()

    def _autoflush(self):
        # logger.info("autoflush")
        # compares millisecond _mtime with millisecond MAX_QUEUE_AGE
        if int(time.time() * 1000) - self._mtime > self.MAX_QUEUE_AGE:
            return self.flush_queue()  # 1 on write, 0 on noop
        return 0  # no write

    def flush_queue(self):
        # update marker - block autoflush
        self._update_mtime()
        with LOCK:
            try:
                # cancel scheduled flush
                if self.MAX_QUEUE_AGE > 0 and self._v_timer is not None:
                    # logger.info("Cancelling timer")
                    self._v_timer.cancel()
                    self._v_timer = None
            except AttributeError:
                self._v_timer = None

        if STATUSQUEUE.empty():
            return 0  # no write

        while True:
            try:
                (id, status) = STATUSQUEUE.get(block=False)
                safeWrite(status)
                self._store(status)
            except Queue.Empty:
                break
        return 1  # confirmed write
