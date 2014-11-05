from plone.uuid.interfaces import IUUID
from collective.celery import task


@task()
def create_content(context, ctype, id_, **fields):
    context.invokeFactory(
        ctype,
        id_
    )
    object_ = context[id_]
    for key, value in fields.iteritems():
        if key.startswith('set'):
            getattr(object_, key)(value)
        else:
            setattr(object_, key, value)
    return IUUID(object_)
