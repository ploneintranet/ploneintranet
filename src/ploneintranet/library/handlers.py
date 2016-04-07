from .content import ILibraryApp, ILibraryFolder, ILibrarySection


def reindex_object_positions(event):
    obj = event.object
    if (
        ILibraryApp.providedBy(obj) or ILibraryFolder.providedBy(obj) or
        ILibrarySection.providedBy(obj)
    ):
        for item in obj.objectValues():
            reindex = getattr(item, 'reindexObject', None)
            if reindex is not None:
                reindex(idxs=['getObjPositionInParent'])
