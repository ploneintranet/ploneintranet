from ploneintranet.userprofile.interfaces import IMemberGroup
from Products.CMFCore.interfaces import ISiteRoot


def search_membergroup(context):
    """
    This deceptively simple algorithm relies on the ZCA
    'more specific interface' preference.

    This is the fallback adapter factory that only gets called
    if no more specific adapter for the context is registered.

    It simply delegates to the aq_parent. If that does have a
    more specific adapter, the recursion breaks. Else this factory
    is hit again and walks the acquisition tree upward, until
    it is pre-empted by a more specific adapter or reaches ISiteRoot.

    The goal is to take a content object, and walk the acquisition tree
    upward until the specific workspace adapter is found for e.g.
    ploneintranet.workspace.workspacefolder.IWorkspaceFolder which
    is registered in ploneintranet.workspace.

    This scheme makes it possible to later registere additional specific
    adapters for e.g. library sections etc.
    """
    if ISiteRoot.providedBy(context):
        return  # raises TypeError 'Could not adapt'
    # recurse upward until a more specific adapter takes precedence
    return IMemberGroup(context.aq_inner.aq_parent)
