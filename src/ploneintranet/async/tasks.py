from .celerytasks import generate_and_add_preview


def queueConversionJob(context, request=None):
    if request is None:
        request = context.REQUEST

    kwargs = dict(
        url=context.absolute_url(),
        cookies=request.cookies
    )

    generate_and_add_preview.apply_async(
        countdown=10,
        kwargs=kwargs,
    )
    return True
